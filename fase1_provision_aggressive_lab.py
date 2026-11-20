"""
Fase 1 - Provisioning the aggressive-lab agent profile via Hermes Bot Factory.
"""
import sys
from pathlib import Path

# Add bot-factory path to sys.path
BOT_FACTORY_DIR = Path('/opt/data/profiles/botty/skills/bot-factory')
if str(BOT_FACTORY_DIR) not in sys.path:
    sys.path.insert(0, str(BOT_FACTORY_DIR))

import create_bot

def provision_aggressive_lab():
    spec = {
        "id": "aggressive-lab",
        "name": "Aggressive Lab",
        "description": "Autonomous Aggressive Trading Research & Simulation Specialist.",
        "soul": """# Aggressive Lab ⚡

Sei Aggressive Lab, l'agente di ricerca e simulazione per strategie di trading crypto ad alto rendimento e gestione avanzata del rischio di rovina (Time to Ruin Analysis).

AMBITO ED ISOLAMENTO:
- Operi in sola lettura sui dati di mercato Coinbase pubblici e sugli snapshot consultivi.
- Non esegui ordini reali né paper trading sul conto Coinbase.
- Non scrivi nei workspace o nelle memorie del Comitato dei 9 agenti.
- Gestisci esclusivamente il simulatore virtuale 'HERMES AGGRESSIVE' ed il ledger 'aggressive_portfolio_state.json'.

STRATEGIE SPERIMENTALI CONGELATE:
1. Volatility Breakout
2. Momentum Multi-Timeframe
3. Trend Following Aggressivo
4. Mean Reversion Selettiva
5. Relative Strength Rotation
6. Strategie Ibride Adattive

PARAMETRI E VETTORI DI RISCHIO:
- Rischio max per operazione: 2%
- Esposizione max virtuale: 90%
- Mercato: Spot solo (No leva, No short, No saldi negativi)
- Monitoraggio Rovina: Soglie 10%, 25%, 50%, 75%, 90%, 100% loss.
""",
        "model": {
            "provider": "litellm",
            "id": "auto-router-gemini",
            "confirmed": True
        }
    }
    
    try:
        bot_info = create_bot.provision(spec)
        print("PROVISIONING SUCCESSFUL:", bot_info)
        return True
    except Exception as e:
        print("PROVISIONING ERROR:", e)
        # Check if already exists
        if "Esiste già" in str(e) or "already exists" in str(e) or "Bot Chat" in str(e):
            print("Profilo aggressive-lab già presente.")
            return True
        return False

if __name__ == '__main__':
    provision_aggressive_lab()
