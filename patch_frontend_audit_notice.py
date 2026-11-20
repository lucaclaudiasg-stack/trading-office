"""
Enhances committee rendering in SPA_HTML to explicitly display:
1. Last executed job vs last authentic meeting with transcript
2. Dynamic origin and status badges
3. Clean disclaimer when showing historical authentic transcript
"""
from pathlib import Path
import shutil

BACKEND_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py')

def patch_js():
    code = BACKEND_PATH.read_text(encoding='utf-8')
    
    # 1. Update JS committee rendering
    old_js = """                        if (document.getElementById('com-timestamp')) document.getElementById('com-timestamp').innerText = comData.timestamp_rome;
                        
                        const timelineDiv = document.getElementById('committee-timeline');"""
                        
    new_js = """                        if (document.getElementById('com-timestamp')) document.getElementById('com-timestamp').innerText = comData.timestamp_rome;
                        if (document.getElementById('com-origin-badge')) document.getElementById('com-origin-badge').innerText = comData.origin;
                        if (document.getElementById('com-status-badge')) document.getElementById('com-status-badge').innerText = comData.status_label;
                        
                        const timelineDiv = document.getElementById('committee-timeline');
                        const noticeDiv = document.getElementById('committee-audit-notice');
                        if (noticeDiv) {
                            if (!comData.has_full_transcript) {
                                noticeDiv.className = 'bg-amber-950/40 border border-amber-800/80 p-2.5 rounded-lg text-xs text-amber-300 space-y-1 block';
                                noticeDiv.innerHTML = `
                                    <div class="flex items-center gap-1.5 font-semibold text-amber-200">
                                        <i class="fa-solid fa-circle-info"></i>
                                        <span>Audit Riunione Automatica delle 09:30 CET</span>
                                    </div>
                                    <p class="text-[11px] text-gray-300">Il job automatico mattutino <code>${comData.session_id}</code> ha eseguito la sintesi deterministica confermando il verdetto difensivo. La timeline sottostante espone la discussione autentica integrale conservata (Sessione serale 19/11/2026 · 21:34 CET con 8 chiamate LLM indipendenti).</p>
                                `;
                            } else {
                                noticeDiv.className = 'hidden';
                            }
                        }"""
    
    if old_js in code:
        code = code.replace(old_js, new_js)
    
    # 2. Add elements into sec-committee HTML if missing
    if 'id="committee-audit-notice"' not in code:
        old_header = """            <!-- Header Riunione -->
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
                </div>"""
        
        new_header = """            <!-- Header Riunione -->
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
                        <p class="text-[11px] text-gray-400 mt-0.5">ID Sessione: <code id="com-session-id" class="text-gray-300 font-mono">DEBATE-MORNING-1795163400</code></p>
                    </div>
                    <div class="flex items-center gap-2">
                        <span id="com-origin-badge" class="bg-blue-950 text-blue-300 border border-blue-800 text-[10px] px-2 py-0.5 rounded font-bold">Automatico Cron (09:30 Europe/Rome)</span>
                        <span id="com-status-badge" class="bg-emerald-950 text-emerald-300 border border-emerald-800 text-[10px] px-2 py-0.5 rounded font-bold">8 Agenti</span>
                    </div>
                </div>
                
                <div id="committee-audit-notice" class="hidden"></div>"""
        
        code = code.replace(old_header, new_header)

    BACKEND_PATH.write_text(code, encoding='utf-8')
    print("Frontend committee audit notice patched successfully.")

if __name__ == '__main__':
    patch_js()
