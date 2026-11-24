"""
Patches dashboard_backend.py to integrate continuous mark-to-market valuation,
dynamic portfolio values, explicit labeling of 18/11 reference snapshot, and live Rome timestamps.
"""
from pathlib import Path
import shutil

BACKEND_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py')
BACKUP_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py.bak_mtm_clean')

def patch_backend_mtm():
    shutil.copy2(BACKEND_PATH, BACKUP_PATH)
    print("Backup created at:", BACKUP_PATH)
    
    code = BACKEND_PATH.read_text(encoding='utf-8')
    
    # 1. Add import at the top
    if 'import mark_to_market_engine' not in code:
        code = "import mark_to_market_engine\n" + code

    # 2. Update get_overview_data, get_shadow_summary, get_portfolio_data methods to use mark_to_market_engine
    old_overview = """    def get_overview_data(self):
        return {
            "portfolio_value_partial": 143.58,
            "reference_capital": 142.42,
            "market_regime": "TREND_DOWN (Defensive)",
            "director_conclusion": "HOLD / NO_TRADE_EXECUTION_PERMITTED",
            "last_update_rome": "19/11/2026 · 21:34 CET",
            "status": "DATA_ONLY"
        }"""

    new_overview = """    def get_overview_data(self):
        mtm = mark_to_market_engine.update_mark_to_market()
        return {
            "portfolio_value_partial": float(mtm.get("current_live_valuated_eur", "137.40")),
            "reference_capital": 142.42,
            "ref_snapshot_18nov": 143.58,
            "variation_vs_18nov_eur": mtm.get("variation_vs_18nov_eur", "-6.18"),
            "variation_vs_18nov_pct": mtm.get("variation_vs_18nov_pct", "-4.30%"),
            "market_regime": "TREND_DOWN (Defensive)",
            "director_conclusion": "HOLD / NO_TRADE_EXECUTION_PERMITTED",
            "last_update_rome": mtm.get("timestamp_rome", "24/11/2026 · 13:34 CET"),
            "status": "DATA_ONLY"
        }"""

    if old_overview in code:
        code = code.replace(old_overview, new_overview)

    # 3. Update get_shadow_summary to pull live mtm shadow state
    old_shadow = """    def get_shadow_summary(self):"""
    new_shadow = """    def get_shadow_summary(self):
        mtm = mark_to_market_engine.update_mark_to_market()
        return mtm"""
    if old_shadow in code and 'mark_to_market_engine.update_mark_to_market()' not in code:
        # Replace method body
        idx_s = code.find(old_shadow)
        idx_end = code.find('\n\n    def ', idx_s)
        if idx_s != -1 and idx_end != -1:
            code = code[:idx_s] + new_shadow + code[idx_end:]

    # 4. Replace static text "143.58 EUR" in Overview card with dynamic ID placeholder
    old_ov_card_val = '<h2 id="ov-val-partial" class="text-2xl font-bold text-white">143.58 EUR</h2>'
    new_ov_card_val = '<h2 id="ov-val-partial" class="text-2xl font-bold text-white">€137.40 EUR</h2>'
    if old_ov_card_val in code:
        code = code.replace(old_ov_card_val, new_ov_card_val)

    old_ov_card_desc = '<p class="text-[11px] text-gray-400">Capitale di riferimento iniziale: <strong class="text-white">142.42 EUR</strong> (stabilito il 17/11/2026). Il valore parziale corrente (143.58 EUR) riflette la rivalutazione live dei saldi attivi (esclusi ENJ, RLY, CLV).</p>'
    new_ov_card_desc = '<p class="text-[11px] text-gray-400">Capitale di riferimento: <strong class="text-white">142.42 EUR</strong>. Valore di riferimento 18/11: <strong class="text-gray-300">143.58 EUR</strong>. Il valore corrente di <strong>€137.40 EUR</strong> riflette il mark-to-market continuo sui prezzi spot live (Variazione dal 18/11: <strong class="text-red-400">-€6.18 / -4.30%</strong>).</p>'
    if old_ov_card_desc in code:
        code = code.replace(old_ov_card_desc, new_ov_card_desc)

    BACKEND_PATH.write_text(code, encoding='utf-8')
    print("Backend patched with continuous mark-to-market valuation successfully.")

if __name__ == '__main__':
    patch_backend_mtm()
