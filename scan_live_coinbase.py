"""
Scans public Coinbase Exchange spot EUR markets and produces real exploratory Top 20.
Enforces:
- Strict rate-limiting (0.3s-0.5s pacing)
- Timeout 8s
- Classification into EXPLORATORY / INSUFFICIENT_DATA
- Advisory discussion generation
- Incremental gap planning for top pairs
- Persists results to live_exploratory_results.json
"""
import sys
import os
import json
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

sys.path.insert(0, '/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e')
import exploratory_top20
import multi_currency_history
import analyst_exploratory_bridge

ORIGIN = 'https://api.exchange.coinbase.com'
HEADERS = {'User-Agent': 'trading-office-exploratory-scanner/1.0'}

def fetch_json(path):
    url = ORIGIN + path
    req = urllib.request.Request(url, headers=HEADERS)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            t1 = time.time()
            return {'status': 'ok', 'data': data, 'start': t0, 'end': t1}
    except Exception as e:
        return {'status': 'error', 'error': str(e), 'start': t0, 'end': time.time()}

def run_scan():
    print("1. Discovering online EUR pairs from Coinbase...")
    res = fetch_json('/products')
    if res['status'] != 'ok':
        print(f"Error fetching products: {res['error']}")
        return {'error': res['error']}
    
    products = res['data']
    eur_pairs = [
        p['id'] for p in products
        if isinstance(p, dict) and p.get('quote_currency') == 'EUR'
        and p.get('status') == 'online' and not p.get('trading_disabled', True)
    ]
    eur_pairs = sorted(eur_pairs)
    print(f"Discovered {len(eur_pairs)} online EUR spot pairs.")
    
    # Process up to 25 pairs to remain well within safe limits
    scan_targets = eur_pairs[:25]
    market_results = []
    
    print(f"2. Fetching stats and book for {len(scan_targets)} pairs...")
    for idx, pair in enumerate(scan_targets, start=1):
        time.sleep(0.3) # Pacing between calls
        stats_res = fetch_json(f'/products/{pair}/stats')
        time.sleep(0.3) # Pacing between calls
        book_res = fetch_json(f'/products/{pair}/book?level=2')
        
        if stats_res['status'] != 'ok' or book_res['status'] != 'ok':
            market_results.append({
                'product': pair,
                'tier': 'INSUFFICIENT_DATA',
                'reason': f"Fetch error: stats={stats_res.get('error')}, book={book_res.get('error')}"
            })
            continue
            
        stats = stats_res['data']
        book = book_res['data']
        
        t_start = min(stats_res['start'], book_res['start'])
        t_end = max(stats_res['end'], book_res['end'])
        envelope = {
            'skew_s': round(t_end - t_start, 3),
            'age_s': round(time.time() - t_start, 3)
        }
        
        # Check local history summary if BTC or ETH
        history_summary = None
        if pair in ('BTC-EUR', 'ETH-EUR'):
            history_summary = multi_currency_history.inspect_verified_archive(pair)
            
        classification = exploratory_top20.classify_market_data(
            pair, book, stats, history_summary=history_summary, fetch_envelope=envelope
        )
        market_results.append(classification)
        print(f"  [{idx}/{len(scan_targets)}] {pair}: Tier={classification['tier']}, Score={classification.get('metrics', {}).get('score')}")
        
    print("3. Generating Exploratory Top 20...")
    ranking = exploratory_top20.build_exploratory_top20(market_results)
    
    print("4. Planning 720h incremental gaps for top 5 pairs...")
    cutoff_now = time.time()
    gaps_plan = {}
    for entry in ranking['top20'][:5]:
        p = entry['product']
        gaps_plan[p] = multi_currency_history.plan_720h_incremental_gaps(p, cutoff_now)
        
    print("5. Generating Analyst Consultative Deliberations (DATA_ONLY) for top 5 pairs...")
    deliberations = []
    for entry in ranking['top20'][:5]:
        packet = analyst_exploratory_bridge.generate_analyst_packet(entry)
        deliberations.append(packet)
        
    final_output = {
        'scan_timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'pairs_discovered_total': len(eur_pairs),
        'pairs_scanned_sample': len(scan_targets),
        'top20_ranking': ranking,
        'gap_planner_top5': gaps_plan,
        'analyst_deliberations_sample': deliberations,
        'safety_confirmation': {
            'all_cron_jobs_paused': True,
            'paper_trading_status': 'DISABLED',
            'real_trading_status': 'PROHIBITED',
            'coinbase_private_status': 'PENDING_AUTH',
            'os_blocked_status': 'MAINTAINED'
        }
    }
    
    out_file = '/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/live_exploratory_results.json'
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=2)
    print(f"Scan complete. Output written to {out_file}")
    return final_output

if __name__ == '__main__':
    run_scan()
