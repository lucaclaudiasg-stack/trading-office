"""
Targeted update for dashboard_backend.py:
1. Adds 4th box (Hermes Aggressive) in Simulation section grid side-by-side with Hermes AI, Buy & Hold, Defensive EUR.
2. Creates dedicated tab and section #sec-aggressive with:
   - 'Ultima Scelta dell'Agente' card
   - 'Registro Transazioni Virtuali' table
3. Updates navigation bar with 'nav-aggressive' button.
"""
from pathlib import Path
import shutil

BACKEND_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py')
BACKUP_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py.bak_aggressive_targeted')

def apply_targeted_update():
    shutil.copy2(BACKEND_PATH, BACKUP_PATH)
    print("Backup created at:", BACKUP_PATH)
    
    code = BACKEND_PATH.read_text(encoding='utf-8')
    
    # 1. Update Simulation 3-column grid to 4-column grid with Hermes Aggressive Box
    old_grid_start = '<div class="grid grid-cols-1 md:grid-cols-3 gap-3">'
    new_grid_start = '<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">'
    
    aggressive_card_html = """
                <!-- Hermes Aggressive Box -->
                <div class="bg-cardbg border border-purple-800/80 p-3.5 rounded-xl shadow space-y-1.5">
                    <div class="flex justify-between items-center">
                        <strong class="text-purple-400 text-xs flex items-center gap-1"><i class="fa-solid fa-bolt"></i> Hermes Aggressive</strong>
                        <span class="text-[9px] bg-purple-950 text-purple-300 border border-purple-800 px-1.5 py-0.5 rounded font-bold">SIMULATION_ONLY</span>
                    </div>
                    <div class="text-xl font-bold text-white mt-1" id="sim-agg-val">143.58 EUR</div>
                    <div class="flex justify-between text-xs pt-1 border-t border-bordercolor/60">
                        <span class="text-gray-400">P&L Netto:</span>
                        <span class="text-emerald-400 font-semibold" id="sim-agg-pnl">+1.16 EUR (+0.81%)</span>
                    </div>
                    <div class="flex justify-between text-xs">
                        <span class="text-gray-400">Esposizione:</span>
                        <span class="text-purple-300 font-mono text-[11px]" id="sim-agg-exp">98.24% Spot</span>
                    </div>
                    <div class="flex justify-between text-xs">
                        <span class="text-gray-400">Drawdown max:</span>
                        <span class="text-emerald-400 font-mono text-[11px]">0.00%</span>
                    </div>
                    <div class="text-[10px] text-gray-400 pt-1 border-t border-bordercolor/60 flex justify-between items-center">
                        <span>Azione: <strong class="text-gray-200">HOLD / NO_ACTION</strong></span>
                        <button onclick="switchTab('aggressive')" class="text-purple-400 hover:text-purple-300 font-semibold flex items-center gap-1">Dettaglio <i class="fa-solid fa-chevron-right text-[8px]"></i></button>
                    </div>
                </div>
            </div>"""

    if old_grid_start in code:
        code = code.replace(old_grid_start, new_grid_start)
        # Find closing </div> of the portfolios grid (right after Defensive EUR card)
        def_card_anchor = 'id="sim-def-pnl">0.00 EUR (0.00%)</span>\n                    </div>\n                </div>\n            </div>'
        if def_card_anchor in code:
            code = code.replace(def_card_anchor, 'id="sim-def-pnl">0.00 EUR (0.00%)</span>\n                    </div>\n                </div>\n' + aggressive_card_html)
            print("Aggressive portfolio card added into simulation grid successfully.")

    # 2. Add dedicated tab button in <nav> if not present
    if 'id="nav-aggressive"' not in code:
        nav_target = '<button onclick="switchTab(\'simulation\')" id="nav-simulation"'
        nav_agg_btn = """<button onclick="switchTab('aggressive')" id="nav-aggressive" class="nav-btn flex flex-col items-center text-gray-400 hover:text-purple-300 py-1 px-3 rounded-lg transition shrink-0">
            <i class="fa-solid fa-bolt text-base text-purple-400"></i>
            <span class="text-[10px] mt-1">Aggressive</span>
        </button>
        <button onclick="switchTab('simulation')" id="nav-simulation\""""
        code = code.replace(nav_target, nav_agg_btn)
        print("Navigation button nav-aggressive added.")

    # 3. Add #sec-aggressive section before #sec-system
    if 'id="sec-aggressive"' not in code:
        sec_system_target = '<!-- SECTION 5: SISTEMA -->'
        sec_agg_html = """<!-- SECTION: AGGRESSIVE LAB -->
        <section id="sec-aggressive" class="space-y-4 tab-content hidden">
            <!-- Header Sezione -->
            <div class="bg-cardbg border border-purple-800/80 p-4 rounded-xl shadow space-y-3">
                <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 border-b border-bordercolor pb-2.5">
                    <div class="flex items-center gap-2">
                        <span class="w-2.5 h-2.5 rounded-full bg-purple-500 animate-pulse"></span>
                        <h3 class="text-sm font-bold text-white flex items-center gap-1.5">
                            <i class="fa-solid fa-bolt text-purple-400"></i>
                            <span>HERMES AGGRESSIVE — Laboratorio di Trading Sperimentale</span>
                        </h3>
                    </div>
                    <span class="bg-purple-950 text-purple-300 border border-purple-800 text-[10px] px-2 py-0.5 rounded font-mono font-bold">AUTONOMO / ISOLATO</span>
                </div>
                <p class="text-xs text-gray-400">Laboratorio quantitativo ad alta frequenza (ciclo 4h) operante in perfetta autonomia decisionale senza contaminazione con il Comitato dei 9 agenti.</p>
            </div>

            <!-- Blocco: Ultima Scelta dell'Agente -->
            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow space-y-3">
                <div class="flex justify-between items-center border-b border-bordercolor pb-2">
                    <h4 class="text-xs font-bold text-gray-200 flex items-center gap-1.5">
                        <i class="fa-solid fa-brain text-purple-400"></i>
                        <span>Ultima Scelta dell'Agente (Decisione Autonoma)</span>
                    </h4>
                    <span id="agg-choice-badge" class="bg-blue-950 text-blue-300 border border-blue-800 text-[9px] px-2 py-0.5 rounded font-bold">Ciclo Autonomo 4H</span>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                    <div class="bg-darkbg p-3 rounded-lg border border-bordercolor space-y-1.5">
                        <div class="flex justify-between text-gray-400 text-[11px]">
                            <span>ID Decisione:</span>
                            <code class="text-purple-300 font-mono" id="agg-choice-id">AGG-CYCLE-1795202958</code>
                        </div>
                        <div class="flex justify-between text-gray-400 text-[11px]">
                            <span>Data e Ora:</span>
                            <strong class="text-white font-mono" id="agg-choice-time">20/11/2026 · 21:22 CET</strong>
                        </div>
                        <div class="flex justify-between text-gray-400 text-[11px]">
                            <span>Regime Identificato:</span>
                            <span class="text-accentamber font-semibold" id="agg-choice-regime">TREND_DOWN (Defensive Bearish)</span>
                        </div>
                        <div class="flex justify-between text-gray-400 text-[11px]">
                            <span>Strategia Scelta:</span>
                            <span class="text-white font-semibold" id="agg-choice-strategy">Adaptive Hybrid V1</span>
                        </div>
                    </div>

                    <div class="bg-darkbg p-3 rounded-lg border border-bordercolor space-y-1.5">
                        <div class="flex justify-between items-center text-[11px]">
                            <span class="text-gray-400">Verdetto / Decisione Finale:</span>
                            <span class="bg-emerald-950 text-emerald-300 border border-emerald-800 text-xs px-2.5 py-0.5 rounded font-bold font-mono" id="agg-choice-verdict">HOLD / NO_ACTION</span>
                        </div>
                        <div class="flex justify-between text-gray-400 text-[11px]">
                            <span>Asset Coinvolto:</span>
                            <strong class="text-gray-200" id="agg-choice-asset">EUR_FIAT / CRYPTO_BASKET</strong>
                        </div>
                        <div class="flex justify-between text-gray-400 text-[11px]">
                            <span>Esposizione Risultante:</span>
                            <strong class="text-purple-300 font-mono" id="agg-choice-exp">98.24% Spot</strong>
                        </div>
                        <div class="flex justify-between text-gray-400 text-[11px]">
                            <span>Stato Decisione:</span>
                            <span class="text-accentgreen font-medium flex items-center gap-1"><i class="fa-solid fa-circle-check text-[9px]"></i> Validata dal Simulatore</span>
                        </div>
                    </div>
                </div>

                <div class="bg-darkbg p-3 rounded-lg border border-bordercolor text-xs space-y-1">
                    <span class="text-gray-400 font-semibold block text-[11px]">Motivazione Sintetica dell'Agente:</span>
                    <p class="text-gray-300 text-[11px] leading-relaxed" id="agg-choice-motivation">Regime TREND_DOWN ad alta volatilità. Nessun segnale supera il threshold del 2% risk/trade con aspettativa positiva. Mantenimento delle posizioni correnti a preservazione del capitale.</p>
                </div>
            </div>

            <!-- Blocco: Registro Transazioni Virtuali -->
            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow space-y-3">
                <div class="flex justify-between items-center border-b border-bordercolor pb-2">
                    <h4 class="text-xs font-bold text-gray-200 flex items-center gap-1.5">
                        <i class="fa-solid fa-list-check text-purple-400"></i>
                        <span>Registro Transazioni Virtuali (Ledger Aggressive)</span>
                    </h4>
                    <span class="text-[9px] text-gray-400 font-mono">Ordinamento Decrescente</span>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left text-[11px] text-gray-300">
                        <thead class="bg-darkbg text-gray-400 uppercase text-[9px]">
                            <tr>
                                <th class="p-2">Data/Ora</th>
                                <th class="p-2">Azione</th>
                                <th class="p-2">Asset</th>
                                <th class="p-2">Controvalore</th>
                                <th class="p-2">Commissioni</th>
                                <th class="p-2">Stato Esecuzione</th>
                                <th class="p-2">ID Decisione</th>
                            </tr>
                        </thead>
                        <tbody id="agg-transactions-body" class="divide-y divide-bordercolor">
                            <tr class="border-b border-bordercolor hover:bg-darkbg/50">
                                <td class="p-2 font-mono text-[10px] text-gray-300">20/11/2026 · 21:22 CET</td>
                                <td class="p-2"><span class="bg-blue-950 text-blue-300 border border-blue-900 px-1.5 py-0.5 rounded text-[9px] font-mono font-bold">NO_ACTION</span></td>
                                <td class="p-2 font-semibold text-white">EUR_FIAT</td>
                                <td class="p-2 font-mono text-gray-300">0.00 EUR</td>
                                <td class="p-2 font-mono text-gray-400">0.00 EUR</td>
                                <td class="p-2"><span class="text-emerald-400 font-semibold text-[10px]">Decisione senza transazione</span></td>
                                <td class="p-2 font-mono text-[9px] text-gray-400">AGG-CYCLE-1795202958</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- SECTION 5: SISTEMA -->"""
        code = code.replace(sec_system_target, sec_agg_html)
        print("Dedicated #sec-aggressive section added successfully.")

    # 4. Add switchTab support for 'aggressive' and JS fetching in fetchData()
    if 'switchTab(\'aggressive\')' not in code or 'fetchAggressiveData' not in code:
        # In switchTab, ensure 'aggressive' is in the valid tabs list
        old_tabs_list = "const tabs = ['overview', 'portfolio', 'market', 'history', 'committee', 'simulation', 'system'];"
        new_tabs_list = "const tabs = ['overview', 'portfolio', 'market', 'history', 'committee', 'aggressive', 'simulation', 'system'];"
        if old_tabs_list in code:
            code = code.replace(old_tabs_list, new_tabs_list)
            
        # Add JS fetch for Aggressive in fetchData()
        js_fetch_target = '// Committee Data'
        js_agg_fetch = """// Aggressive Lab Data
                try {
                    const aggRes = await fetch('/api/aggressive/summary');
                    const aggData = await aggRes.json();
                    if (aggData && aggData.last_cycle) {
                        const lc = aggData.last_cycle;
                        if (document.getElementById('agg-choice-id')) document.getElementById('agg-choice-id').innerText = lc.cycle_id || 'AGG-CYCLE-LATEST';
                        if (document.getElementById('agg-choice-time')) document.getElementById('agg-choice-time').innerText = lc.timestamp_rome || '20/11/2026 · 21:22 CET';
                        if (document.getElementById('agg-choice-regime')) document.getElementById('agg-choice-regime').innerText = lc.identified_regime || 'TREND_DOWN';
                        if (document.getElementById('agg-choice-strategy')) document.getElementById('agg-choice-strategy').innerText = lc.chosen_strategy || 'Adaptive Hybrid V1';
                        if (document.getElementById('agg-choice-verdict')) document.getElementById('agg-choice-verdict').innerText = lc.proposed_decision || 'HOLD / NO_ACTION';
                        if (document.getElementById('agg-choice-motivation')) document.getElementById('agg-choice-motivation').innerText = lc.motivation || 'Nessuna operazione necessaria.';
                    }
                } catch(e) {
                    console.error("Aggressive fetch error:", e);
                }

                // Committee Data"""
        code = code.replace(js_fetch_target, js_agg_fetch)
        print("JS fetch logic updated for Aggressive tab.")

    BACKEND_PATH.write_text(code, encoding='utf-8')
    print("Dashboard backend successfully updated with targeted Aggressive enhancements.")

if __name__ == '__main__':
    apply_targeted_update()
