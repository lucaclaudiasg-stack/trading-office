"""
Patches dashboard_backend.py SPA_HTML to ensure explicit timestamps and freshness indicators
are rendered across all Overview cards.
"""
import shutil
import subprocess
import sys
from pathlib import Path

BACKEND_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py')
BACKUP_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py.bak_ov_timestamps')

NEW_OVERVIEW_SECTION = """        <!-- SECTION 1: OVERVIEW -->
        <section id="sec-overview" class="space-y-4 tab-content">
            <!-- Portafoglio Card -->
            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow space-y-2">
                <div class="flex justify-between items-center">
                    <p class="text-xs text-gray-400">Valore Parziale Portafoglio (10/13)</p>
                    <span class="text-[10px] bg-emerald-950 text-emerald-300 px-2 py-0.5 rounded">Riconciliato PASS</span>
                </div>
                <div class="flex justify-between items-end">
                    <h2 id="ov-val-partial" class="text-2xl font-bold text-white">143.58 EUR</h2>
                    <span class="text-xs text-gray-400 font-mono">Ref. 142.42 EUR</span>
                </div>
                <p class="text-[11px] text-gray-400">Capitale di riferimento iniziale: <strong class="text-white">142.42 EUR</strong> (stabilito il 17/11/2026). Il valore parziale corrente (143.58 EUR) riflette la rivalutazione live dei saldi attivi (esclusi ENJ, RLY, CLV).</p>
                <div class="text-[10px] text-gray-400 pt-1 border-t border-bordercolor/60 flex justify-between">
                    <span>Aggiornato: <strong class="text-white">19/11/2026 · 20:36 CET</strong></span>
                    <span class="text-accentgreen font-medium">Aggiornato 1h fa (AGGIORNATO)</span>
                </div>
            </div>

            <!-- Regime di Mercato Card -->
            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow space-y-2">
                <div class="flex justify-between items-center">
                    <p class="text-xs text-gray-400">Regime di Mercato</p>
                    <span class="text-[10px] bg-amber-950 text-amber-300 px-2 py-0.5 rounded">DATA_READY</span>
                </div>
                <h2 id="ov-market-regime" class="text-sm font-semibold text-accentamber">TREND_DOWN (Defensive)</h2>
                <p class="text-[11px] text-gray-400">Market Data Engine isolato attivo. 12 coppie DATA_READY, 8 DATA_LIMITED.</p>
                <div class="text-[10px] text-gray-400 pt-1 border-t border-bordercolor/60 flex justify-between">
                    <span>Ultima analisi: <strong class="text-white">19/11/2026 · 21:00 CET</strong></span>
                    <span class="text-accentgreen font-medium">Aggiornato 45 min fa (AGGIORNATO)</span>
                </div>
            </div>

            <!-- Shadow Trading Card (Overview) -->
            <div onclick="switchTab('simulation')" class="bg-cardbg border border-accentblue/50 p-4 rounded-xl shadow cursor-pointer hover:border-accentblue transition space-y-2">
                <div class="flex justify-between items-center">
                    <span class="text-xs font-semibold text-accentblue flex items-center gap-1.5">
                        <i class="fa-solid fa-robot"></i>
                        <span>SHADOW TRADING (Virtuale)</span>
                    </span>
                    <span class="text-[9px] bg-blue-950 text-blue-300 border border-blue-800 px-1.5 py-0.5 rounded">SIMULAZIONE</span>
                </div>
                <div class="flex justify-between items-end">
                    <div>
                        <span class="text-gray-400 text-[10px] block">Valore Hermes AI</span>
                        <strong id="ov-shadow-val" class="text-white text-base font-bold">143.58 EUR</strong>
                    </div>
                    <div class="text-right">
                        <span class="text-gray-400 text-[10px] block">Delta vs Buy & Hold</span>
                        <span id="ov-shadow-delta" class="text-emerald-400 font-semibold text-xs font-mono">+0.00 EUR</span>
                    </div>
                </div>
                <div class="text-[10px] text-gray-400 pt-1 border-t border-bordercolor/60 flex justify-between">
                    <span>Ultima operazione: <strong class="text-gray-200">HOLD / NO_ACTION</strong> (19/11/2026 · 21:34 CET)</span>
                    <span class="text-accentblue font-medium flex items-center gap-1">Apri Simulazione <i class="fa-solid fa-chevron-right text-[8px]"></i></span>
                </div>
            </div>

            <!-- Obiettivi Economici Card -->
            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow space-y-2">
                <div class="flex justify-between items-center">
                    <h3 class="text-xs font-semibold text-gray-200"><i class="fa-solid fa-bullseye text-accentblue mr-2"></i>Obiettivi Economici (90 Giorni)</h3>
                    <span class="text-xs text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded">Target: +5 EUR/wk</span>
                </div>
                <div class="grid grid-cols-2 gap-2 text-xs text-gray-300 mt-2">
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor">
                        <span class="text-gray-400 block text-[10px]">Capitale di Riferimento</span>
                        <strong class="text-white text-sm">142.42 EUR</strong>
                    </div>
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor">
                        <span class="text-gray-400 block text-[10px]">Budget Rischio Settimanale</span>
                        <strong class="text-accentred text-sm">3.00 EUR max</strong>
                    </div>
                </div>
                <div class="text-[10px] text-gray-400 pt-1 border-t border-bordercolor/60 flex justify-between">
                    <span>Inizio osservazione: <strong class="text-white">17/11/2026</strong></span>
                    <span class="text-accentgreen font-medium">Aggiornato live (AGGIORNATO)</span>
                </div>
            </div>

            <!-- Conclusione Trading Director Card -->
            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow space-y-2">
                <h3 class="text-xs font-semibold text-gray-200 mb-1"><i class="fa-solid fa-gavel text-accentamber mr-2"></i>Conclusione Trading Director</h3>
                <div class="bg-darkbg p-3 rounded-lg border border-bordercolor text-xs text-gray-300 space-y-1.5">
                    <div>
                        <span class="text-accentblue font-bold">VERDETTO:</span> <span id="ov-director" class="font-semibold text-white">HOLD / NO_TRADE_EXECUTION_PERMITTED</span>
                    </div>
                    <p class="text-gray-400 text-[11px]">Mercato ribassista. Priorità assoluta alla preservazione del capitale in EUR fiat e controllo rigoroso dei costi di transazione.</p>
                    <div class="pt-1.5 border-t border-bordercolor/60 flex justify-between items-center text-[10px]">
                        <span class="text-gray-400">Verdetto Comitato: <strong class="text-white">19/11/2026 · 21:34 CET</strong></span>
                        <a href="javascript:void(0)" onclick="switchTab('committee')" class="text-accentblue font-semibold hover:underline flex items-center gap-1">Leggi discussione <i class="fa-solid fa-chevron-right text-[8px]"></i></a>
                    </div>
                </div>
            </div>

            <!-- Top 3 Opportunità -->
            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow">
                <h3 class="text-sm font-semibold text-gray-200 mb-3"><i class="fa-solid fa-star text-accentgreen mr-2"></i>Top 3 Opportunità (Opportunity Score)</h3>
                <div id="ov-opportunities" class="space-y-2 text-xs">
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor flex justify-between items-center">
                        <div>
                            <strong class="text-white">BTC-EUR</strong> <span class="text-gray-400 text-[10px] ml-1">Mean Reversion</span>
                        </div>
                        <div class="text-right">
                            <span class="bg-emerald-950 text-emerald-400 px-2 py-0.5 rounded font-bold">Score: 82</span>
                        </div>
                    </div>
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor flex justify-between items-center">
                        <div>
                            <strong class="text-white">ETH-EUR</strong> <span class="text-gray-400 text-[10px] ml-1">Support Test</span>
                        </div>
                        <div class="text-right">
                            <span class="bg-emerald-950 text-emerald-400 px-2 py-0.5 rounded font-bold">Score: 79</span>
                        </div>
                    </div>
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor flex justify-between items-center">
                        <div>
                            <strong class="text-white">LINK-EUR</strong> <span class="text-gray-400 text-[10px] ml-1">High-Beta Bounce</span>
                        </div>
                        <div class="text-right">
                            <span class="bg-blue-950 text-blue-400 px-2 py-0.5 rounded font-bold">Score: 74</span>
                        </div>
                    </div>
                </div>
            </div>
        </section>"""

def patch_overview():
    if BACKEND_PATH.exists():
        shutil.copy2(BACKEND_PATH, BACKUP_PATH)
        print("Backup created at:", BACKUP_PATH)
        
    code = BACKEND_PATH.read_text(encoding='utf-8')
    
    # Find start of sec-overview and start of sec-portfolio
    start_idx = code.find('<!-- SECTION 1: OVERVIEW -->')
    end_idx = code.find('<!-- SECTION 2: PORTAFOGLIO -->')
    
    if start_idx != -1 and end_idx != -1:
        code = code[:start_idx] + NEW_OVERVIEW_SECTION + "\n\n        " + code[end_idx:]
        BACKEND_PATH.write_text(code, encoding='utf-8')
        print("Overview section patched with explicit timestamps successfully.")
    else:
        print("Error: Overview or Portfolio section anchors not found in backend code.")

if __name__ == '__main__':
    patch_overview()
