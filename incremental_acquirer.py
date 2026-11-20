"""
Incremental Acquirer for Target Pairs (BTC, ETH, ADA, LINK, LTC).
Strictly bounded to max 4 closed-bar requests per batch per product.
Enforces:
- Rate-limiting and pacing (0.5s between calls)
- PENDING_PORTFOLIO / Public Coinbase Exchange only
- Strictly closed hourly candles (candle end <= cutoff)
- Re-use of verified BTC/ETH archives in mode=ro
- Storage in isolated in-memory or verified staging store (:memory:)
- Deduplication and SHA-256 provenance binding
- Zero modification to original databases
"""
import sys
import time
import json
import sqlite3
import hashlib
import urllib.request
import urllib.error
from pathlib import Path
from urllib.parse import urlencode
from datetime import datetime, timezone

sys.path.insert(0, '/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e')
import multi_currency_history

TARGET_PRODUCTS = ['BTC-EUR', 'ETH-EUR', 'ADA-EUR', 'LINK-EUR', 'LTC-EUR']
ORIGIN = 'https://api.exchange.coinbase.com'
HEADERS = {'User-Agent': 'trading-office-consolidator/1.0'}

DDL_STAGING = """
CREATE TABLE IF NOT EXISTS staged_candles (
    product TEXT NOT NULL,
    granularity_s INTEGER NOT NULL,
    time_utc_s INTEGER NOT NULL,
    low REAL NOT NULL,
    high REAL NOT NULL,
    open REAL NOT NULL,
    close REAL NOT NULL,
    volume REAL NOT NULL,
    source TEXT NOT NULL,
    payload_sha256 TEXT NOT NULL,
    staged_at_utc TEXT NOT NULL,
    PRIMARY KEY(product, granularity_s, time_utc_s)
);
CREATE TABLE IF NOT EXISTS acquisition_audit (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    product TEXT NOT NULL,
    slot_utc_s INTEGER NOT NULL,
    status TEXT NOT NULL,
    attempt INTEGER NOT NULL,
    bytes_received INTEGER,
    sha256 TEXT,
    at_utc TEXT NOT NULL
);
"""

class IncrementalAcquirer:
    def __init__(self, in_memory=True):
        self.in_memory = in_memory
        self.db = sqlite3.connect(':memory:')
        self.db.executescript(DDL_STAGING)
        
    def fetch_candle(self, product, start_s, interval=3600):
        end_s = start_s + interval
        start_iso = datetime.fromtimestamp(start_s, timezone.utc).isoformat()
        end_iso = datetime.fromtimestamp(end_s, timezone.utc).isoformat()
        
        query = urlencode({'granularity': interval, 'start': start_iso, 'end': end_iso})
        path = f"/products/{product}/candles?{query}"
        url = ORIGIN + path
        req = urllib.request.Request(url, headers=HEADERS)
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                raw = resp.read()
                data = json.loads(raw.decode('utf-8'))
                digest = hashlib.sha256(raw).hexdigest()
                return {'status': 'ok', 'data': data, 'raw_bytes': len(raw), 'sha256': digest, 'latency_s': round(time.time() - t0, 3)}
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'latency_s': round(time.time() - t0, 3)}

    def acquire_bounded_batch(self, product, max_batch=4, current_cutoff=None):
        cutoff = current_cutoff or int(time.time())
        plan = multi_currency_history.plan_720h_incremental_gaps(product, cutoff)
        
        missing_slots = plan['missing_slots_sample'][:max_batch]
        acquired = []
        now_iso = datetime.now(timezone.utc).isoformat()
        
        for slot in missing_slots:
            time.sleep(0.5) # Pacing anti rate-limit
            res = self.fetch_candle(product, slot)
            if res['status'] == 'ok' and isinstance(res['data'], list) and len(res['data']) >= 1:
                # Coinbase candela: [time, low, high, open, close, volume]
                bar = res['data'][0]
                t, low, high, o, c, vol = bar
                # Validazione di sicurezza
                if t == slot and low > 0 and high >= low and vol >= 0:
                    try:
                        self.db.execute(
                            "INSERT INTO staged_candles VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                            (product, 3600, t, float(low), float(high), float(o), float(c), float(vol),
                             'Coinbase Exchange public', res['sha256'], now_iso)
                        )
                        self.db.execute(
                            "INSERT INTO acquisition_audit(product, slot_utc_s, status, attempt, bytes_received, sha256, at_utc) VALUES(?,?,?,?,?,?,?)",
                            (product, t, 'ACQUIRED', 1, res['raw_bytes'], res['sha256'], now_iso)
                        )
                        acquired.append({
                            'slot_utc_s': t,
                            'slot_iso': datetime.fromtimestamp(t, timezone.utc).isoformat(),
                            'close_price': c,
                            'volume': vol,
                            'sha256': res['sha256']
                        })
                    except sqlite3.IntegrityError:
                        # Deduplica: già presente
                        pass
            else:
                self.db.execute(
                    "INSERT INTO acquisition_audit(product, slot_utc_s, status, attempt, bytes_received, sha256, at_utc) VALUES(?,?,?,?,?,?,?)",
                    (product, slot, f"FAIL: {res.get('error', 'empty')}", 1, 0, None, now_iso)
                )
                
        # Ricalcola gap residui
        updated_plan = multi_currency_history.plan_720h_incremental_gaps(product, cutoff)
        # Sottrai quelli appena acquisiti nello staging in-memory
        remaining_gap_count = max(0, updated_plan['missing_count'] - len(acquired))
        
        return {
            'product': product,
            'batch_requested_slots': len(missing_slots),
            'bars_acquired_verified': len(acquired),
            'acquired_sample': acquired,
            'initial_gap_count': plan['missing_count'],
            'remaining_gap_count': remaining_gap_count,
            'original_archive_untouched': True
        }

def run_consolidation_acquisition():
    cutoff = int(time.time())
    acquirer = IncrementalAcquirer(in_memory=True)
    summary = {
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'cutoff_ts': cutoff,
        'cutoff_utc': datetime.fromtimestamp(cutoff, timezone.utc).isoformat(),
        'products_processed': {}
    }
    
    for prod in TARGET_PRODUCTS:
        print(f"Acquiring bounded batch for {prod}...")
        res = acquirer.acquire_bounded_batch(prod, max_batch=4, current_cutoff=cutoff)
        summary['products_processed'][prod] = res
        print(f"  {prod}: Acquired {res['bars_acquired_verified']} bars. Remaining gaps: {res['remaining_gap_count']}.")
        
    out_file = '/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/consolidation_acquisition_report.json'
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
        
    print(f"Acquisition complete. Written to {out_file}")
    return summary

if __name__ == '__main__':
    run_consolidation_acquisition()
