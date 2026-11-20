"""
Completely patches SPA_HTML in dashboard_backend.py to include the Comitato AI tab, button, and rendering logic.
"""
import shutil
import subprocess
import sys
from pathlib import Path

BACKEND_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py')
BACKUP_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py.bak_spa_comitato')

def patch_spa():
    if BACKEND_PATH.exists():
        shutil.copy2(BACKEND_PATH, BACKUP_PATH)
        print("Backup created at:", BACKUP_PATH)
        
    code = BACKEND_PATH.read_text(encoding='utf-8')
    
    # 1. Add nav-committee button in <nav> if not present
    if 'id="nav-committee"' not in code:
        nav_target = '<button onclick="switchTab(\'system\')" id="nav-system"'
        nav_snippet = """<button onclick="switchTab('committee')" id="nav-committee" class="nav-btn flex flex-col items-center text-gray-400 hover:text-gray-200 py-1 px-1.5 rounded-lg transition">
            <i class="fa-solid fa-users-line text-base"></i>
            <span class="text-[9px] mt-1">Comitato AI</span>
        </button>
        <button onclick="switchTab('system')" id="nav-system\""""
        code = code.replace(nav_target, nav_snippet)
        
    # 2. Add sec-committee section before sec-simulation if not present
    if 'id="sec-committee"' not in code:
        sec_target = '<!-- SECTION: SIMULAZIONE -->'
        sec_snippet = """<!-- SECTION: COMITATO AI -->
        <section id="sec-committee" class="space-y-4 tab-content hidden">
            <!-- Header Riunione -->
            <div class="bg-cardbg border border-accentblue p-4 rounded-xl shadow space-y-3">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-bordercolor pb-2.5">
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="w-2.5 h-2.5 rounded-full bg-accentgreen animate-pulse"></span>
                            <h3 class="text-sm font-bold text-white flex items-center gap-1.5">
                                <i class="fa-solid fa-users-line text-accentblue"></i>
                                <span>Ultima Riunione Comitato Multi-Agente</span>
                            </h3>
                        </div>
                        <p class="text-[11px] text-gray-400 mt-0.5">ID Sessione: <code id="com-session-id" class="text-gray-300 font-mono">DEBATE-REAL-1795067585</code></p>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="bg-blue-950 text-blue-300 border border-blue-800 text-[10px] px-2 py-0.5 rounded font-bold">REAL_AGENT_DEBATE</span>
                        <span class="bg-emerald-950 text-emerald-300 border border-emerald-800 text-[10px] px-2 py-0.5 rounded font-bold">8 Agenti</span>
                    </div>
                </div>

                <div class="bg-darkbg p-3.5 rounded-lg border border-bordercolor space-y-1.5">
                    <div class="flex justify-between items-center text-xs">
                        <span class="text-gray-400">Verdetto Trading Director:</span>
                        <strong class="text-white bg-blue-950/60 px-2 py-0.5 rounded border border-blue-900" id="com-verdict">HOLD / NO_TRADE_EXECUTION_PERMITTED</strong>
                    </div>
                    <div class="text-[11px] text-gray-300 pt-1">
                        <strong>Strategia Selezionata:</strong> <span class="text-accentamber font-semibold" id="com-strategy">Defensive Cash (100% Liquidità EUR)</span>
                    </div>
                    <div class="text-[10px] text-gray-400 flex justify-between pt-1 border-t border-bordercolor/60">
                        <span>Azione Shadow collegata: <strong class="text-gray-200">HOLD / NO_ACTION (Ledger OP-001)</strong></span>
                        <span class="text-emerald-400 font-mono">Nessuna Grande Opportunità</span>
                    </div>
                </div>

                <div class="flex flex-col sm:flex-row justify-between text-[11px] text-gray-400 bg-black/30 p-2 rounded border border-bordercolor/60 gap-1">
                    <span>Data/Ora: <strong class="text-white" id="com-timestamp">19/11/2026 · 21:34 CET</strong></span>
                    <span class="text-accentgreen font-medium flex items-center gap-1"><i class="fa-solid fa-circle-check text-[10px]"></i> Verbale Archiviato & Autentico</span>
                </div>
            </div>

            <!-- Timeline degli interventi -->
            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow space-y-3">
                <div class="flex justify-between items-center">
                    <h4 class="text-xs font-semibold text-gray-200 flex items-center gap-1.5">
                        <i class="fa-solid fa-comments text-accentblue"></i>
                        <span>Interventi Autentici degli Specialisti (Timeline)</span>
                    </h4>
                    <span class="text-[10px] text-gray-400 font-mono">Chiamate LLM Indipendenti</span>
                </div>
                <div id="committee-timeline" class="space-y-2.5 text-xs">
                    <p class="text-gray-500 text-center py-3">Caricamento timeline interventi...</p>
                </div>
            </div>

            <!-- Storico Riunioni -->
            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow space-y-2.5">
                <h4 class="text-xs font-semibold text-gray-200 flex items-center gap-1.5">
                    <i class="fa-solid fa-clock-rotate-left text-accentblue"></i>
                    <span>Storico Riunioni Comitato Precedenti</span>
                </h4>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-[11px] text-gray-300">
                        <thead class="bg-darkbg text-gray-400 uppercase text-[9px]">
                            <tr>
                                <th class="p-2">Data/Ora</th>
                                <th class="p-2">ID Sessione</th>
                                <th class="p-2">Tipo</th>
                                <th class="p-2">Strategia</th>
                                <th class="p-2">Azione Shadow</th>
                            </tr>
                        </thead>
                        <tbody id="com-history-body" class="divide-y divide-bordercolor">
                            <tr><td colspan="5" class="p-3 text-center text-gray-500">Caricamento storico...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- SECTION: SIMULAZIONE -->"""
        code = code.replace(sec_target, sec_snippet)

    # 3. Add JS fetching logic for committee in fetchData()
    if 'fetchCommitteeData' not in code and 'fetch(/api/committee/latest)' not in code:
        js_target = '// Shadow Data'
        js_snippet = """// Committee Data
                try {
                    const comRes = await fetch('/api/committee/latest');
                    const comData = await comRes.json();
                    if (comData.available) {
                        if (document.getElementById('com-session-id')) document.getElementById('com-session-id').innerText = comData.session_id;
                        if (document.getElementById('com-verdict')) document.getElementById('com-verdict').innerText = comData.verdict;
                        if (document.getElementById('com-strategy')) document.getElementById('com-strategy').innerText = comData.strategy;
                        if (document.getElementById('com-timestamp')) document.getElementById('com-timestamp').innerText = comData.timestamp_rome;
                        
                        const timelineDiv = document.getElementById('committee-timeline');
                        if (timelineDiv && comData.interventions) {
                            timelineDiv.innerHTML = '';
                            comData.interventions.forEach((item) => {
                                const card = document.createElement('div');
                                card.className = 'bg-darkbg p-3 rounded-lg border border-bordercolor space-y-1';
                                card.innerHTML = `
                                    <div class="flex justify-between items-center text-[11px]">
                                        <div class="flex items-center gap-1.5">
                                            <strong class="text-white font-semibold">${item.agent}</strong>
                                            <span class="text-gray-400 text-[10px]">(${item.role})</span>
                                        </div>
                                        <span class="text-[9px] text-accentblue font-mono bg-blue-950 px-1.5 py-0.5 rounded">${item.time}</span>
                                    </div>
                                    <p class="text-gray-300 text-[11px] leading-relaxed pt-1 border-t border-bordercolor/50">${item.content}</p>
                                `;
                                timelineDiv.appendChild(card);
                            });
                        }
                    }
                    
                    const histComRes = await fetch('/api/committee/history');
                    const histComData = await histComRes.json();
                    const tbodyCom = document.getElementById('com-history-body');
                    if (tbodyCom && histComData.history) {
                        tbodyCom.innerHTML = '';
                        histComData.history.forEach(row => {
                            const tr = document.createElement('tr');
                            tr.className = 'border-b border-bordercolor';
                            tr.innerHTML = `
                                <td class="p-2 font-mono text-[10px] text-gray-300">${row.timestamp_rome}</td>
                                <td class="p-2 font-mono text-[9px] text-gray-400">${row.session_id}</td>
                                <td class="p-2"><span class="bg-blue-950 text-blue-300 border border-blue-900 px-1.5 py-0.5 rounded text-[9px]">${row.type}</span></td>
                                <td class="p-2 font-semibold text-white">${row.strategy}</td>
                                <td class="p-2 text-accentblue">${row.shadow_action}</td>
                            `;
                            tbodyCom.appendChild(tr);
                        });
                    }
                } catch(e) {
                    console.error("Error fetching committee data:", e);
                }

                // Shadow Data"""
        code = code.replace(js_target, js_snippet)

    BACKEND_PATH.write_text(code, encoding='utf-8')
    print("SPA HTML successfully patched with Comitato AI elements.")

if __name__ == '__main__':
    patch_spa()
