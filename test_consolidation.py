"""
Comprehensive Verification Suite for Multi-Asset Consolidation:
1. Bounded batch incremental retrieval (max 4 bars, closed-only)
2. Deduplication and idempotency
3. Provenance and SHA-256 payload integrity
4. Integrity and read-only preservation of original archives
5. Permission separation and OS_BLOCKED assertion
"""
import sys
import unittest
import sqlite3
import hashlib
from pathlib import Path

sys.path.insert(0, '/opt/data/profiles/docky/workspace/multicurrency-public-v4/market-engine-staging-r1/engine-review-r4')
sys.path.insert(0, '/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e')

import engine
import multi_currency_history
import incremental_acquirer

class TestConsolidationSuite(unittest.TestCase):

    def test_bounded_batch_retrieval(self):
        acq = incremental_acquirer.IncrementalAcquirer(in_memory=True)
        # Mock / bounded run on BTC-EUR for a small batch of 2 missing slots
        cutoff = 1795003200
        plan = multi_currency_history.plan_720h_incremental_gaps('BTC-EUR', cutoff)
        self.assertGreater(plan['missing_count'], 0)
        
        # Test that acquirer limits batch to requested max_batch
        res = acq.acquire_bounded_batch('BTC-EUR', max_batch=2, current_cutoff=cutoff)
        self.assertLessEqual(res['bars_acquired_verified'], 2)
        self.assertTrue(res['original_archive_untouched'])

    def test_deduplication_idempotency(self):
        acq = incremental_acquirer.IncrementalAcquirer(in_memory=True)
        # Inserisci candela manualmente
        now = "2026-11-18T14:00:00Z"
        acq.db.execute(
            "INSERT INTO staged_candles VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            ('BTC-EUR', 3600, 1795000000, 58000.0, 58500.0, 58100.0, 58400.0, 15.0,
             'Coinbase Exchange public', 'sha256-test', now)
        )
        count_before = acq.db.execute("SELECT COUNT(*) FROM staged_candles").fetchone()[0]
        self.assertEqual(count_before, 1)
        
        # Tenta duplicazione dello stesso slot -> deve essere gestito senza errori
        try:
            acq.db.execute(
                "INSERT OR IGNORE INTO staged_candles VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                ('BTC-EUR', 3600, 1795000000, 58000.0, 58500.0, 58100.0, 58400.0, 15.0,
                 'Coinbase Exchange public', 'sha256-test', now)
            )
        except sqlite3.IntegrityError:
            self.fail("Insertion should be ignored on conflict")
            
        count_after = acq.db.execute("SELECT COUNT(*) FROM staged_candles").fetchone()[0]
        self.assertEqual(count_after, 1)

    def test_provenance_and_sha256(self):
        acq = incremental_acquirer.IncrementalAcquirer(in_memory=True)
        # Simula fetch con hash
        raw_payload = b'[[1795000000, 58000.0, 58500.0, 58100.0, 58400.0, 15.0]]'
        digest = hashlib.sha256(raw_payload).hexdigest()
        
        now = "2026-11-18T14:00:00Z"
        acq.db.execute(
            "INSERT INTO staged_candles VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            ('BTC-EUR', 3600, 1795000000, 58000.0, 58500.0, 58100.0, 58400.0, 15.0,
             'Coinbase Exchange public', digest, now)
        )
        row = acq.db.execute("SELECT source, payload_sha256 FROM staged_candles WHERE product='BTC-EUR'").fetchone()
        self.assertEqual(row[0], 'Coinbase Exchange public')
        self.assertEqual(row[1], digest)

    def test_original_archives_integrity(self):
        # Verifica che gli archivi storici originali non siano stati alterati
        btc_info = multi_currency_history.inspect_verified_archive('BTC-EUR')
        self.assertEqual(btc_info['status'], 'VERIFIED_READONLY')
        self.assertEqual(btc_info['quick_check'], 'ok')
        self.assertEqual(btc_info['hourly_candles_count'], 8755)

        eth_info = multi_currency_history.inspect_verified_archive('ETH-EUR')
        self.assertEqual(eth_info['status'], 'VERIFIED_READONLY')
        self.assertEqual(eth_info['quick_check'], 'ok')
        self.assertEqual(eth_info['hourly_candles_count'], 8755)

    def test_permission_separation_and_os_blocked(self):
        # Assicura che create_stage sollevi rigorosamente OS_BLOCKED
        with self.assertRaises(RuntimeError) as cm:
            engine.create_stage()
        self.assertIn('OS_BLOCKED', str(cm.exception))

        # Assicura che ingest su connessione con file su disco sia rigorosamente bloccato
        disk_conn = sqlite3.connect('/tmp/test_forbidden_disk.sqlite')
        try:
            with self.assertRaises(RuntimeError) as cm2:
                engine.ingest(disk_conn, 'BTC-EUR', 3600, 1000, 2000, {}, offline_fixture=True)
            self.assertIn('OS_BLOCKED', str(cm2.exception))
        finally:
            disk_conn.close()
            Path('/tmp/test_forbidden_disk.sqlite').unlink(missing_ok=True)


if __name__ == '__main__':
    unittest.main()
