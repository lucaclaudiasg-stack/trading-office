"""
Unit test suite for Persistent Staging Lifecycle and Recovery.
"""
import sys
import unittest
import sqlite3
import tempfile
import shutil
import os
from pathlib import Path

sys.path.insert(0, '/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e')
import persistent_staging

class TestPersistenceLifecycle(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="persist_test_")
        self.db_path = os.path.join(self.test_dir, "test_staging.sqlite")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_atomic_write_and_deduplication(self):
        store = persistent_staging.PersistentStagingStore(self.db_path)
        bar1 = [1795000000, 58000.0, 58500.0, 58100.0, 58400.0, 15.0]
        raw1 = b"dummy_raw_bytes"
        sha1 = "sha256_dummy_1"
        
        ok = store.insert_candle_atomic('BTC-EUR', 3600, 1795000000, bar1, raw1, sha1)
        self.assertTrue(ok)
        self.assertEqual(store.count_persisted_bars('BTC-EUR'), 1)
        
        # Deduplication: re-insert same slot
        ok_dup = store.insert_candle_atomic('BTC-EUR', 3600, 1795000000, bar1, raw1, sha1)
        self.assertTrue(ok_dup)
        self.assertEqual(store.count_persisted_bars('BTC-EUR'), 1)
        store.close()

    def test_restart_recovery_and_quick_check(self):
        # 1. Open and insert
        store = persistent_staging.PersistentStagingStore(self.db_path)
        bar = [1795003600, 1600.0, 1650.0, 1610.0, 1640.0, 150.0]
        store.insert_candle_atomic('ETH-EUR', 3600, 1795003600, bar, b"eth_raw", "sha256_eth")
        store.close()
        
        # 2. Simulate complete restart: reopen database from disk
        reopened_store = persistent_staging.PersistentStagingStore(self.db_path)
        self.assertEqual(reopened_store.count_persisted_bars('ETH-EUR'), 1)
        slots = reopened_store.get_persisted_slots('ETH-EUR', 3600)
        self.assertIn(1795003600, slots)
        
        # Quick check
        qc = reopened_store.conn.execute("PRAGMA quick_check").fetchone()[0]
        self.assertEqual(qc, 'ok')
        reopened_store.close()

    def test_gap_recalculation_with_persistence(self):
        store = persistent_staging.PersistentStagingStore(self.db_path)
        cutoff = 1795009200
        
        # Gap before inserting
        gap_before = persistent_staging.plan_gaps_with_persistence('ADA-EUR', cutoff, store)
        self.assertEqual(gap_before['persisted_in_store'], 0)
        self.assertEqual(gap_before['missing_count'], 720)
        
        # Pick the first missing slot and persist it
        slot = gap_before['missing_slots'][0]
        bar = [slot, 0.14, 0.15, 0.142, 0.148, 10000.0]
        store.insert_candle_atomic('ADA-EUR', 3600, slot, bar, b"ada_raw", "sha256_ada")
        
        # Gap after inserting
        gap_after = persistent_staging.plan_gaps_with_persistence('ADA-EUR', cutoff, store)
        self.assertEqual(gap_after['persisted_in_store'], 1)
        self.assertEqual(gap_after['missing_count'], 719)
        self.assertNotIn(slot, gap_after['missing_slots'])
        store.close()

    def test_symlink_rejection_security(self):
        symlink_path = os.path.join(self.test_dir, "symlink_db.sqlite")
        target_path = os.path.join(self.test_dir, "real_db.sqlite")
        Path(target_path).touch()
        os.symlink(target_path, symlink_path)
        
        with self.assertRaises(RuntimeError) as cm:
            persistent_staging.PersistentStagingStore(symlink_path)
        self.assertIn("SECURITY_VIOLATION", str(cm.exception))


if __name__ == '__main__':
    unittest.main()
