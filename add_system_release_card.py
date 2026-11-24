"""
Adds Release & Versioning Info Card to the System page (#sec-system) of dashboard_backend.py.
"""
from pathlib import Path
import shutil

BACKEND_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py')
BACKUP_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py.bak_sys_release')

def add_system_release():
    shutil.copy2(BACKEND_PATH, BACKUP_PATH)
    print("Backup created at:", BACKUP_PATH)
    
    code = BACKEND_PATH.read_text(encoding='utf-8')
    
    target = '        </section>\n\n    </main>'
    release_card = """            <!-- Release & Build Versioning Card (v1.8.0) -->
            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow space-y-2">
                <div class="flex justify-between items-center border-b border-bordercolor pb-2">
                    <h3 class="text-xs font-semibold text-gray-200 flex items-center gap-1.5">
                        <i class="fa-solid fa-code-branch text-accentblue"></i>
                        <span>Versione e Rilascio di Sistema</span>
                    </h3>
                    <span class="bg-emerald-950 text-emerald-300 border border-emerald-800 text-[9px] px-2 py-0.5 rounded font-bold font-mono">v1.8.0-continuous-mark-to-market</span>
                </div>
                <div class="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs">
                    <div class="bg-darkbg p-2 rounded border border-bordercolor">
                        <span class="text-gray-400 block text-[10px]">Build ID</span>
                        <strong class="text-white font-mono text-[11px]">BUILD V2-20261120-FINAL</strong>
                    </div>
                    <div class="bg-darkbg p-2 rounded border border-bordercolor">
                        <span class="text-gray-400 block text-[10px]">Commit Git</span>
                        <code class="text-accentblue font-mono text-[11px]">e689e7d</code>
                    </div>
                    <div class="bg-darkbg p-2 rounded border border-bordercolor">
                        <span class="text-gray-400 block text-[10px]">Ticker MTM</span>
                        <span class="text-emerald-400 font-mono text-[11px]">Attivo (10 min)</span>
                    </div>
                </div>
                <div class="text-[10px] text-gray-400 pt-1 border-t border-bordercolor/60 flex justify-between">
                    <span>Repository Privato: <strong class="text-gray-300">lucaclaudiasg-stack/trading-office</strong></span>
                    <span class="text-gray-400">Branch: <strong class="text-white">main</strong></span>
                </div>
            </div>
        </section>

    </main>"""

    if target in code and 'v1.8.0-continuous-mark-to-market' not in code:
        code = code.replace(target, release_card)
        BACKEND_PATH.write_text(code, encoding='utf-8')
        print("Release & Versioning Card added to System page successfully.")
    else:
        print("Release card already present or target not found.")

if __name__ == '__main__':
    add_system_release()
