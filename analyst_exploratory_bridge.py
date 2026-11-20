"""
Analyst Exploratory Bridge & Advisory Integration (Refined for Objective 2)
Permette l'analisi consultiva DATA_ONLY delle opportunità EXPLORATORY.
Il Bear Analyst formula valutazioni critiche e identifica fattori di rischio.
Il veto vincolante / blocco esecutivo è applicato dal Risk Engine al gate di autorizzazione all'esecuzione.
"""
from datetime import datetime, timezone

def generate_analyst_packet(exploratory_market, portfolio_policy=None):
    """
    Produce il pacchetto di analisi consultiva DATA_ONLY per gli analisti.
    Consente la discussione delle opportunità esplorative, garantendo che
    il Risk Engine mantenga il rifiuto categorico (DENY) per l'esecuzione.
    """
    product = exploratory_market.get('product')
    tier = exploratory_market.get('tier')
    metrics = exploratory_market.get('metrics', {})
    
    spread = metrics.get('spread_bps', 999.0)
    vol_eur = metrics.get('volume_eur_proxy_24h', 0.0)
    depth_eur = metrics.get('depth_total_1pct_eur', 0.0)
    last_px = metrics.get('last_price_eur', 0.0)
    score = metrics.get('score', 0.0)
    
    # 1. Market Analyst evaluation
    # Valuta liquidità, spread e trend volumetrico
    if spread < 10.0 and vol_eur > 1000000.0:
        ma_signal = 'STRONG_INTEREST'
        ma_rationale = f"Alta liquidità (Depth ~{depth_eur:.0f} EUR), spread eccellente ({spread:.1f} bps), volume solido (~{vol_eur:.0f} EUR)."
    elif spread < 25.0 and vol_eur > 250000.0:
        ma_signal = 'MODERATE_INTEREST'
        ma_rationale = f"Liquidità adeguata (Depth ~{depth_eur:.0f} EUR), spread accettabile ({spread:.1f} bps), volume ~{vol_eur:.0f} EUR."
    else:
        ma_signal = 'LOW_INTEREST'
        ma_rationale = f"Spread elevato ({spread:.1f} bps) o volume ridotto (~{vol_eur:.0f} EUR). Bassa priorità."
        
    market_analyst_opinion = {
        'role': 'market-analyst',
        'signal': ma_signal,
        'score': score,
        'rationale': ma_rationale,
        'data_tier': tier
    }
    
    # 2. Bear Analyst evaluation (Valutazione critica senza bloccare la discussione consultiva)
    bear_concerns = []
    if tier == 'EXPLORATORY':
        bear_concerns.append("Asincronia temporale intrinseca (Coinbase /stats privo di clock exchange certificato)")
    if spread > 15.0:
        bear_concerns.append(f"Rischio slippage elevato per spread allargato ({spread:.1f} bps)")
    if depth_eur < 50000.0:
        bear_concerns.append(f"Libro ordini sottile entro +/-1% (~{depth_eur:.0f} EUR): rischio assorbimento impatti")
    if vol_eur < 500000.0:
        bear_concerns.append("Volume rolling modesto: possibile liquidità apparente non durevole")
        
    bear_analyst_opinion = {
        'role': 'bear-analyst',
        'critical_evaluation': 'HIGH_CAUTION' if len(bear_concerns) >= 2 else 'ACCEPTABLE_RISK_FOR_STUDY',
        'risk_factors': bear_concerns or ['Volatilità di mercato standard'],
        'advisory_notes': 'Opportunità interessante per osservazione, ma non conforme agli standard per ordini operativi.'
    }
    
    # 3. Trading Strategist proposal
    # Formula ipotesi teoriche e stop loss ipotetici
    if ma_signal in ('STRONG_INTEREST', 'MODERATE_INTEREST'):
        strat_action = 'THEORETICAL_STUDY_LONG'
        strat_notes = f"Valutare dinamica di accumulo sopra {last_px * 0.99:.2f} EUR. Stop loss teorico a {last_px * 0.97:.2f} EUR."
    else:
        strat_action = 'THEORETICAL_STUDY_MONITOR'
        strat_notes = "Mantenere solo in watchlist per divergenze spread/volume."
        
    strategist_proposal = {
        'role': 'trading-strategist',
        'theoretical_action': strat_action,
        'strategy_notes': strat_notes,
        'operational_action': 'HOLD (Dati non validati per ordini)'
    }
    
    # 4. Trading Director Synthesis
    director_synthesis = {
        'role': 'trading-director',
        'discussion_status': 'DELIBERATION_RECORDED_CONSULTATIVE_ONLY',
        'consensus_summary': f"{product}: Discussione analisti completata in modalità DATA_ONLY. Segnale MA: {ma_signal}, Giudizio Bear: {bear_analyst_opinion['critical_evaluation']}.",
        'operational_decision': 'HOLD / NO_TRADE_EXECUTION_PERMITTED'
    }
    
    # 5. Risk Engine Gate (Enforces FAIL-CLOSED execution gate)
    # Il Risk Engine blocca categoricamente qualsiasi tentativo operativo per mercati non validati
    risk_evaluation = {
        'gate_status': 'DENY' if tier != 'VALIDATED' else 'EVALUATE',
        'gate_reason': 'FAIL-CLOSED: Market tier is EXPLORATORY (Unsynchronized exchange clocks or incomplete historical 720h series). Execution authorization denied.' if tier != 'VALIDATED' else 'VALIDATED_FOR_RISK_CHECK',
        'paper_status': 'DISABLED',
        'can_execute': False
    }
    
    return {
        'schema_version': 1,
        'packet_type': 'DATA_ONLY_CONSULTATIVE_ADVISORY',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'product': product,
        'market_tier': tier,
        'analysts': {
            'market_analyst': market_analyst_opinion,
            'bear_analyst': bear_analyst_opinion,
            'trading_strategist': strategist_proposal
        },
        'director': director_synthesis,
        'risk_gate': risk_evaluation
    }
