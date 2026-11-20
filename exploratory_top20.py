"""
Top 20 Esplorativa Multi-Valuta (Coinbase Public)
Distingue rigorosamente:
- VALIDATED: Sincronizzazione alla fonte certificata, 720 barre orarie complete, book auditato (attualmente nessuno soddisfa i requisiti).
- EXPLORATORY: Metriche pubbliche reali osservate con asincronia dichiarata, utilizzabile ESCLUSIVAMENTE per analisi, NON per autorizzare operazioni.
- INSUFFICIENT_DATA: Dati incompleti, mercato sospeso, quotazione non EUR, o errore di fetch.
"""
import math
import hashlib
import json
from decimal import Decimal
from datetime import datetime, timezone

def calculate_exploratory_score(vol_eur, depth_eur, spread_bps, vol_component=None):
    """
    Calcola un punteggio comparativo normalizzato trasparente per l'analisi esplorativa.
    Formula: 0.40 * log10(1 + vol_eur) + 0.35 * log10(1 + depth_eur) - 0.25 * (spread_bps / 100.0)
    Spread minore aumenta il punteggio; volume e profondità maggiori aumentano il punteggio.
    La volatilità non aumenta il punteggio (trattata come descrittore di rischio).
    """
    if vol_eur <= 0 or depth_eur <= 0 or spread_bps < 0:
        return None
    s = (
        0.40 * math.log10(1.0 + vol_eur) +
        0.35 * math.log10(1.0 + depth_eur) -
        0.25 * (spread_bps / 100.0)
    )
    return round(s, 6)

def classify_market_data(product_id, book, stats, history_summary=None, fetch_envelope=None):
    """
    Classifica una coppia spot EUR in: VALIDATED, EXPLORATORY o INSUFFICIENT_DATA.
    """
    envelope = fetch_envelope or {}
    skew_s = envelope.get('skew_s', 0.0)
    age_s = envelope.get('age_s', 0.0)
    
    # Validazione base metadati
    if not book or not stats:
        return {
            'product': product_id,
            'tier': 'INSUFFICIENT_DATA',
            'reason': 'Missing book or stats object'
        }
    
    # Controllo book levels
    bids = book.get('bids', [])
    asks = book.get('asks', [])
    if not bids or not asks:
        return {
            'product': product_id,
            'tier': 'INSUFFICIENT_DATA',
            'reason': 'Empty book sides'
        }
    
    try:
        best_bid = float(bids[0][0])
        best_ask = float(asks[0][0])
        last_px = float(stats.get('last', 0.0))
        vol_base = float(stats.get('volume', 0.0))
    except (ValueError, TypeError, IndexError):
        return {
            'product': product_id,
            'tier': 'INSUFFICIENT_DATA',
            'reason': 'Invalid numerical values in book or stats'
        }
    
    if best_bid <= 0 or best_ask <= 0 or best_bid >= best_ask or last_px <= 0 or vol_base <= 0:
        return {
            'product': product_id,
            'tier': 'INSUFFICIENT_DATA',
            'reason': 'Non-positive prices, crossed book or zero volume'
        }
    
    mid = (best_bid + best_ask) / 2.0
    spread_bps = (best_ask - best_bid) / mid * 10000.0
    vol_eur = vol_base * last_px
    
    # Calcolo profondità entro +/- 1% (gestisce righe book a 2 o 3 elementi: price, size, num_orders)
    depth_bid = sum(float(row[0]) * float(row[1]) for row in bids if len(row) >= 2 and float(row[0]) >= mid * 0.99)
    depth_ask = sum(float(row[0]) * float(row[1]) for row in asks if len(row) >= 2 and float(row[0]) <= mid * 1.01)
    depth_total = depth_bid + depth_ask
    
    score = calculate_exploratory_score(vol_eur, depth_total, spread_bps)
    
    # Controllo se può essere VALIDATED
    # Requisiti VALIDATED: source_time book == source_time stats, 720 barre complete, volatilità calcolata
    book_time = book.get('time')
    stats_time = stats.get('time')
    is_synchronized = (book_time is not None and stats_time is not None and book_time == stats_time)
    hist_status = history_summary.get('status') if history_summary else 'missing'
    
    if is_synchronized and hist_status == 'ok':
        tier = 'VALIDATED'
        tier_reason = 'Synchronized exchange source clock and complete 720h historical volatility'
    else:
        tier = 'EXPLORATORY'
        missing_reasons = []
        if not is_synchronized:
            missing_reasons.append('stats endpoint lacks source timestamp (asynchronous fetch envelope)')
        if hist_status != 'ok':
            missing_reasons.append(f'historical 720h hourly candles status: {hist_status}')
        tier_reason = '; '.join(missing_reasons)
    
    return {
        'product': product_id,
        'tier': tier,
        'tier_reason': tier_reason,
        'operational_permission': 'ANALYSIS_ONLY (No trade authorization allowed)' if tier == 'EXPLORATORY' else 'AUTHORIZED_FOR_RISK_EVALUATION',
        'metrics': {
            'last_price_eur': last_px,
            'spread_bps': round(spread_bps, 2),
            'volume_base_24h': vol_base,
            'volume_eur_proxy_24h': round(vol_eur, 2),
            'depth_bid_1pct_eur': round(depth_bid, 2),
            'depth_ask_1pct_eur': round(depth_ask, 2),
            'depth_total_1pct_eur': round(depth_total, 2),
            'score': score
        },
        'timestamps': {
            'book_source_time': book_time,
            'stats_source_time': stats_time,
            'fetch_skew_s': skew_s,
            'fetch_age_s': age_s
        }
    }

def build_exploratory_top20(market_results):
    """
    Ordina e produce la Top 20 Esplorativa dai mercati con tier EXPLORATORY o VALIDATED.
    """
    eligible = [m for m in market_results if m.get('tier') in ('EXPLORATORY', 'VALIDATED') and m.get('metrics', {}).get('score') is not None]
    
    # Ordinamento: punteggio decrescente, profondità decrescente, spread crescente, volume decrescente, product_id crescente
    eligible.sort(
        key=lambda x: (
            -x['metrics']['score'],
            -x['metrics']['depth_total_1pct_eur'],
            x['metrics']['spread_bps'],
            -x['metrics']['volume_eur_proxy_24h'],
            x['product']
        )
    )
    
    top20 = eligible[:20]
    for rank, entry in enumerate(top20, start=1):
        entry['rank'] = rank
    
    insufficient = [m for m in market_results if m.get('tier') == 'INSUFFICIENT_DATA']
    
    return {
        'generated_utc': datetime.now(timezone.utc).isoformat(),
        'unsupported_or_insufficient_count': len(insufficient),
        'eligible_count': len(eligible),
        'top20_count': len(top20),
        'classification_policy': 'EXPLORATORY_ONLY — Strictly prohibited for operational order execution',
        'top20': top20,
        'insufficient_samples': insufficient[:5]
    }
