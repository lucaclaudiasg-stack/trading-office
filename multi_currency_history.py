"""
Multi-Currency Incremental History Planner & Manager
Re-uses verified BTC and ETH archives in mode=ro.
Plans incremental 720 hourly closed-bar acquisition for selected pairs.
Guarantees NO mass downloads, strict rate-limiting, and staging isolation.
"""
import sqlite3
import math
from pathlib import Path
from datetime import datetime, timezone

ORIGINAL_ARCHIVES = {
    'BTC-EUR': '/opt/data/trading-office-data/market_history.sqlite',
    'ETH-EUR': '/opt/data/profiles/linu/workspace/eth-history/eth_market_history.sqlite'
}

def inspect_verified_archive(product_id):
    """
    Legge in sola lettura l'archivio storico verificato, senza toccarlo.
    """
    path = ORIGINAL_ARCHIVES.get(product_id)
    if not path or not Path(path).exists():
        return {'status': 'NOT_FOUND', 'product': product_id}
    
    uri = Path(path).resolve().as_uri() + '?mode=ro'
    db = sqlite3.connect(uri, uri=True)
    try:
        db.execute('PRAGMA query_only=ON')
        qc = db.execute('PRAGMA quick_check').fetchone()[0]
        # Conta barre orarie
        row = db.execute(
            'SELECT COUNT(*), MIN(time_utc_s), MAX(time_utc_s) FROM candles WHERE product=? AND granularity_s=3600',
            (product_id,)
        ).fetchone()
        count, min_t, max_t = row
        return {
            'status': 'VERIFIED_READONLY',
            'product': product_id,
            'path': path,
            'quick_check': qc,
            'hourly_candles_count': count,
            'min_time_utc': datetime.fromtimestamp(min_t, timezone.utc).isoformat() if min_t else None,
            'max_time_utc': datetime.fromtimestamp(max_t, timezone.utc).isoformat() if max_t else None,
            'latest_open_ts': max_t
        }
    finally:
        db.close()

def plan_720h_incremental_gaps(product_id, current_cutoff_ts, target_staging_db=None):
    """
    Pianifica l'acquisizione delle 720 barre orarie chiuse (30 giorni) precedenti al cutoff.
    Identifica esattamente gli intervalli mancanti senza scaricare dati massivi.
    """
    interval = 3600
    end = (int(current_cutoff_ts) // interval) * interval
    expected_latest = end - interval
    start = end - (720 * interval)
    
    expected_slots = set(range(start, end, interval))
    existing_slots = set()
    
    # 1. Controlla archivio storico originale se presente
    orig_path = ORIGINAL_ARCHIVES.get(product_id)
    if orig_path and Path(orig_path).exists():
        uri = Path(orig_path).resolve().as_uri() + '?mode=ro'
        db = sqlite3.connect(uri, uri=True)
        try:
            db.execute('PRAGMA query_only=ON')
            rows = db.execute(
                'SELECT time_utc_s FROM candles WHERE product=? AND granularity_s=? AND time_utc_s>=? AND time_utc_s<?',
                (product_id, interval, start, end)
            ).fetchall()
            existing_slots.update(r[0] for r in rows)
        finally:
            db.close()
            
    # 2. Controlla staging isolato se presente
    if target_staging_db and Path(target_staging_db).exists():
        db = sqlite3.connect(Path(target_staging_db).resolve().as_uri() + '?mode=ro', uri=True)
        try:
            db.execute('PRAGMA query_only=ON')
            rows = db.execute(
                'SELECT t FROM candles WHERE product=? AND interval_s=? AND t>=? AND t<?',
                (product_id, interval, start, end)
            ).fetchall()
            existing_slots.update(r[0] for r in rows)
        except sqlite3.OperationalError:
            pass # tabella non ancora creata
        finally:
            db.close()
            
    missing_slots = sorted(expected_slots - existing_slots)
    
    return {
        'product': product_id,
        'window_start_utc': datetime.fromtimestamp(start, timezone.utc).isoformat(),
        'window_end_utc': datetime.fromtimestamp(end, timezone.utc).isoformat(),
        'expected_total': 720,
        'existing_count': len(existing_slots),
        'missing_count': len(missing_slots),
        'coverage_pct': round((len(existing_slots) / 720.0) * 100.0, 2),
        'missing_slots_sample': missing_slots[:10],
        'requires_incremental_fetch': len(missing_slots) > 0,
        'bounded_batch_recommended_size': min(len(missing_slots), 4) # Max 4 richieste per batch per evitare rate limit
    }
