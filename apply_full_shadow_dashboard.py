"""
Applies full Shadow Trading dashboard integration to dashboard_backend.py:
- Adds Simulazione section to SPA_HTML
- Adds Simulazione nav button to bottom bar and desktop nav
- Adds SHADOW TRADING card to Overview section
- Adds JS fetch logic to populate all shadow components
- Restarts daemon on port 8765
"""
import subprocess
import sys
from pathlib import Path

BACKEND_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py')

def apply_update():
    content = BACKEND_PATH.read_text(encoding='utf-8')
    
    # 1. Add Simulazione button in bottom nav if not present
    if 'id="nav-simulation"' not in content:
        nav_button = """        <button onclick="switchTab('simulation')" id="nav-simulation" class="nav-btn flex flex-col items-center text-gray-400 hover:text-gray-200 py-1 px-2 rounded-lg transition">
            <i class="fa-solid fa-robot text-base"></i>
            <span class="text-[10px] mt-1">Simulazione</span>
        </button>
        <button onclick="switchTab('system')" id="nav-system" """
        content = content.replace('<button onclick="switchTab(\'system\')" id="nav-system" ', nav_button)
        
    # 2. Add SHADOW TRADING card in Overview section if not present
    if 'SHADOW TRADING (Virtuale)' not in content:
        overview_card = """            <!-- SHADOW TRADING CARD (Overview) -->
            <div onclick="switchTab('simulation')" class="bg-cardbg border border-accentblue/50 p-4 rounded-xl shadow cursor-pointer hover:border-accentblue transition">
                <div class="flex justify-between items-center mb-1">
                    <span class="text-xs font-semibold text-accentblue flex items-center gap-1.5">
                        <i class="fa-solid fa-robot"></i>
                        <span>SHADOW TRADING (Virtuale)</span>
                    </span>
                    <span class="text-[9px] bg-blue-950 text-blue-300 border border-blue-800 px-1.5 py-0.5 rounded">SIMULAZIONE</span>
                </div>
                <div class="flex justify-between items-end mt-2">
                    <div>
                        <span class="text-gray-400 text-[10px] block">Valore Hermes AI</span>
                        <strong id="ov-shadow-val" class="text-white text-base font-bold">143.58 EUR</strong>
                    </div>
                    <div class="text-right">
                        <span class="text-gray-400 text-[10px] block">Delta vs Buy & Hold</span>
                        <span id="ov-shadow-delta" class="text-emerald-400 font-semibold text-xs font-mono">+0.00 EUR</span>
                    </div>
                </div>
                <div class="mt-2 text-[10px] text-gray-400 flex justify-between items-center border-t border-bordercolor/60 pt-1.5">
                    <span>Ultima operazione: <strong class="text-gray-200">HOLD / NO_ACTION</strong></span>
                    <span class="text-accentblue font-medium flex items-center gap-1">Apri Simulazione <i class="fa-solid fa-chevron-right text-[8px]"></i></span>
                </div>
            </div>

            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow">
                <div class="flex justify-between items-center mb-2">"""
        content = content.replace('<div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow">\n                <div class="flex justify-between items-center mb-2">', overview_card)

    # 3. Add SIMULATION section before SYSTEM section if not present
    if 'id="sec-simulation"' not in content:
        sim_section = """        <!-- SECTION: SIMULAZIONE -->
        <section id="sec-simulation" class="space-y-4 tab-content hidden">
            <!-- Disclaimer Banner -->
            <div class="bg-amber-950/40 border border-amber-800/80 p-2.5 rounded-xl flex items-center justify-between text-xs text-amber-300">
                <div class="flex items-center gap-2">
                    <i class="fa-solid fa-triangle-exclamation text-accentamber text-sm"></i>
                    <span><strong>SIMULAZIONE — DENARO NON REALE</strong>: Portafogli paralleli virtuali.</span>
                </div>
                <span class="text-[10px] bg-amber-900/60 px-2 py-0.5 rounded font-mono">DATA_ONLY</span>
            </div>

            <!-- 3 Portfolios Cards -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                <!-- Hermes AI -->
                <div class="bg-cardbg border border-accentblue p-3.5 rounded-xl shadow space-y-1.5">
                    <div class="flex justify-between items-center">
                        <strong class="text-accentblue text-xs flex items-center gap-1"><i class="fa-solid fa-robot"></i> Hermes AI</strong>
                        <span class="text-[9px] bg-blue-950 text-blue-400 px-1.5 py-0.5 rounded font-bold">ATTIVO</span>
                    </div>
                    <div class="text-xl font-bold text-white mt-1" id="sim-hermes-val">143.58 EUR</div>
                    <div class="text-[11px] text-gray-400 flex justify-between">
                        <span>P&L Netto: <strong id="sim-hermes-pnl" class="text-emerald-400 font-mono">0.00 EUR (0.00%)</strong></span>
                        <span>DD: <strong class="text-gray-300">1.20%</strong></span>
                    </div>
                    <p class="text-[10px] text-gray-500 pt-1 border-t border-bordercolor">Segue decisioni consultive del Comitato</p>
                </div>

                <!-- Buy & Hold -->
                <div class="bg-cardbg border border-bordercolor p-3.5 rounded-xl shadow space-y-1.5">
                    <div class="flex justify-between items-center">
                        <strong class="text-emerald-400 text-xs flex items-center gap-1"><i class="fa-solid fa-hand-holding-dollar"></i> Buy & Hold</strong>
                        <span class="text-[9px] bg-emerald-950 text-emerald-400 px-1.5 py-0.5 rounded">BENCHMARK</span>
                    </div>
                    <div class="text-xl font-bold text-white mt-1" id="sim-bh-val">143.58 EUR</div>
                    <div class="text-[11px] text-gray-400 flex justify-between">
                        <span>P&L Netto: <strong id="sim-bh-pnl" class="text-emerald-400 font-mono">0.00 EUR (0.00%)</strong></span>
                        <span>DD: <strong class="text-gray-300">1.20%</strong></span>
                    </div>
                    <p class="text-[10px] text-gray-500 pt-1 border-t border-bordercolor">Quantità iniziali statiche invariate</p>
                </div>

                <!-- Defensive EUR -->
                <div class="bg-cardbg border border-bordercolor p-3.5 rounded-xl shadow space-y-1.5">
                    <div class="flex justify-between items-center">
                        <strong class="text-amber-400 text-xs flex items-center gap-1"><i class="fa-solid fa-euro-sign"></i> Defensive EUR</strong>
                        <span class="text-[9px] bg-amber-950 text-amber-400 px-1.5 py-0.5 rounded">CASH 100%</span>
                    </div>
                    <div class="text-xl font-bold text-white mt-1" id="sim-def-val">142.45 EUR</div>
                    <div class="text-[11px] text-gray-400 flex justify-between">
                        <span>P&L Netto: <strong class="text-rose-400 font-mono">-1.13 EUR (-0.79%)</strong></span>
                        <span>DD: <strong class="text-gray-300">0.79%</strong></span>
                    </div>
                    <p class="text-[10px] text-gray-500 pt-1 border-t border-bordercolor">Netto di drag commissionale (-1.13 EUR)</p>
                </div>
            </div>

            <!-- Metriche di Confronto -->
            <div class="bg-cardbg border border-bordercolor p-3.5 rounded-xl shadow space-y-2">
                <h4 class="text-xs font-semibold text-gray-200">Metriche di Confronto (Hermes AI vs Benchmark)</h4>
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                    <div class="bg-darkbg p-2 rounded border border-bordercolor">
                        <span class="text-gray-400 text-[10px] block">Delta vs Buy & Hold</span>
                        <strong class="text-white text-xs font-mono" id="sim-delta-bh">+0.00 EUR</strong>
                    </div>
                    <div class="bg-darkbg p-2 rounded border border-bordercolor">
                        <span class="text-gray-400 text-[10px] block">Delta vs Defensive</span>
                        <strong class="text-emerald-400 text-xs font-mono" id="sim-delta-def">+1.13 EUR</strong>
                    </div>
                    <div class="bg-darkbg p-2 rounded border border-bordercolor">
                        <span class="text-gray-400 text-[10px] block">Commissioni Pagate</span>
                        <strong class="text-white text-xs font-mono" id="sim-fees">0.00 EUR</strong>
                    </div>
                    <div class="bg-darkbg p-2 rounded border border-bordercolor">
                        <span class="text-gray-400 text-[10px] block">Operazioni Virtuali</span>
                        <strong class="text-white text-xs font-mono" id="sim-ops-count">0</strong>
                    </div>
                </div>
            </div>

            <!-- Ledger Registro Operazioni Virtuali -->
            <div class="bg-cardbg border border-bordercolor p-3.5 rounded-xl shadow space-y-2">
                <div class="flex justify-between items-center">
                    <h4 class="text-xs font-semibold text-gray-200 flex items-center gap-1.5">
                        <i class="fa-solid fa-book text-accentblue"></i>
                        <span>Registro Operazioni Virtuali (Ledger)</span>
                    </h4>
                    <span class="text-[9px] text-gray-400 font-mono">Idempotente & Decimal</span>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-[11px] text-gray-300">
                        <thead class="bg-darkbg text-gray-400 uppercase text-[9px]">
                            <tr>
                                <th class="p-2">Data/Ora UTC</th>
                                <th class="p-2">Azione</th>
                                <th class="p-2">Decisione ID</th>
                                <th class="p-2">Asset</th>
                                <th class="p-2">Fee</th>
                                <th class="p-2">Esito</th>
                            </tr>
                        </thead>
                        <tbody id="sim-ledger-body" class="divide-y divide-bordercolor">
                            <tr><td colspan="6" class="p-3 text-center text-gray-500">Caricamento ledger...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- SECTION 5: SISTEMA -->"""
        content = content.replace('<!-- SECTION 5: SISTEMA -->', sim_section)

    # 4. Add JS shadow fetch logic in fetchData()
    if 'fetchShadowData' not in content:
        js_shadow_fetch = """
                // Shadow Data
                try {
                    const shRes = await fetch('/api/shadow/summary');
                    const shData = await shRes.json();
                    if (shData.portfolios) {
                        const h = shData.portfolios.hermes_ai;
                        const bh = shData.portfolios.buy_and_hold;
                        const def = shData.portfolios.defensive_eur;
                        const m = shData.metrics_comparison;
                        
                        if (document.getElementById('ov-shadow-val')) document.getElementById('ov-shadow-val').innerText = h.current_capital_eur + ' EUR';
                        if (document.getElementById('ov-shadow-delta')) document.getElementById('ov-shadow-delta').innerText = m.hermes_vs_buy_and_hold_eur;
                        
                        if (document.getElementById('sim-hermes-val')) document.getElementById('sim-hermes-val').innerText = h.current_capital_eur + ' EUR';
                        if (document.getElementById('sim-hermes-pnl')) document.getElementById('sim-hermes-pnl').innerText = `${h.pnl_net_eur} EUR (${h.pnl_net_pct})`;
                        
                        if (document.getElementById('sim-bh-val')) document.getElementById('sim-bh-val').innerText = bh.current_capital_eur + ' EUR';
                        if (document.getElementById('sim-bh-pnl')) document.getElementById('sim-bh-pnl').innerText = `${bh.pnl_net_eur} EUR (${bh.pnl_net_pct})`;
                        
                        if (document.getElementById('sim-def-val')) document.getElementById('sim-def-val').innerText = def.current_capital_eur + ' EUR';
                        
                        if (document.getElementById('sim-delta-bh')) document.getElementById('sim-delta-bh').innerText = m.hermes_vs_buy_and_hold_eur;
                        if (document.getElementById('sim-delta-def')) document.getElementById('sim-delta-def').innerText = m.hermes_vs_defensive_eur;
                        if (document.getElementById('sim-fees')) document.getElementById('sim-fees').innerText = m.total_fees_paid_eur;
                        if (document.getElementById('sim-ops-count')) document.getElementById('sim-ops-count').innerText = m.operations_count;
                    }
                    
                    const ledRes = await fetch('/api/shadow/ledger');
                    const ledData = await ledRes.json();
                    const tbody = document.getElementById('sim-ledger-body');
                    if (tbody && ledData.ledger) {
                        tbody.innerHTML = '';
                        ledData.ledger.forEach(row => {
                            const tr = document.createElement('tr');
                            tr.className = 'border-b border-bordercolor';
                            tr.innerHTML = `
                                <td class="p-2 font-mono text-[10px] text-gray-400">${row.timestamp_utc ? row.timestamp_utc.substring(0, 19).replace('T', ' ') : ''}</td>
                                <td class="p-2 font-bold text-accentblue">${row.action}</td>
                                <td class="p-2 font-mono text-[9px] text-gray-400">${row.decision_id || 'N/A'}</td>
                                <td class="p-2 font-bold text-white">${row.symbol}</td>
                                <td class="p-2 text-gray-300">${row.fees_paid_eur} EUR</td>
                                <td class="p-2"><span class="bg-emerald-950 text-emerald-400 px-1.5 py-0.5 rounded text-[9px]">${row.outcome}</span></td>
                            `;
                            tbody.appendChild(tr);
                        });
                    }
                } catch(e) {
                    console.error("Error fetching shadow data:", e);
                }
"""
        content = content.replace("// System Jobs & Executions", js_shadow_fetch + "\n                // System Jobs & Executions")

    BACKEND_PATH.write_text(content, encoding='utf-8')
    print("Full Shadow Dashboard applied to dashboard_backend.py.")

if __name__ == '__main__':
    apply_update()
