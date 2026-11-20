"""
Ensures JavaScript fetchData() in dashboard_backend.py parses and renders all sections independently
with resilient error handling so no tab freezes or stays blank.
"""
from pathlib import Path
import shutil

BACKEND_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py')

def verify_and_patch_js():
    code = BACKEND_PATH.read_text(encoding='utf-8')
    
    # Check if fetchData handles system data parsing cleanly
    if "fetch('/api/system')" not in code:
        old_js_fetch = "async function fetchData() {"
        new_js_fetch = """async function fetchData() {
            // System Data
            try {
                const sysRes = await fetch('/api/system');
                const sysData = await sysRes.json();
                const sysBody = document.getElementById('sys-jobs-body');
                if (sysBody && sysData.jobs) {
                    sysBody.innerHTML = '';
                    sysData.jobs.forEach(j => {
                        const tr = document.createElement('tr');
                        tr.className = 'border-b border-bordercolor';
                        tr.innerHTML = `
                            <td class="p-2 font-mono text-[10px] text-white">${j.name || j.job_id || 'Job'}</td>
                            <td class="p-2 font-mono text-[9px] text-gray-300">${j.expr || j.schedule || 'Cron'}</td>
                            <td class="p-2 text-gray-400 text-[10px]">${j.timezone || 'Europe/Rome'}</td>
                            <td class="p-2"><span class="bg-emerald-950 text-emerald-300 border border-emerald-900 px-1.5 py-0.5 rounded text-[9px]">ATTIVO</span></td>
                        `;
                        sysBody.appendChild(tr);
                    });
                }
            } catch(e) {
                console.error("System fetch error:", e);
            }
"""
        code = code.replace(old_js_fetch, new_js_fetch)
        BACKEND_PATH.write_text(code, encoding='utf-8')
        print("fetchData() patched with robust system parser.")
    else:
        print("fetchData() already includes system fetch.")

if __name__ == '__main__':
    verify_and_patch_js()
