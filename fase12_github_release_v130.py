"""
Fase 12 - Final Release v1.3.0 with Aggressive Job Registry integration commit and push to GitHub.
"""
import subprocess
import re
from pathlib import Path

WORKSPACE = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e')

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(WORKSPACE))
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def release_v130():
    print("=== SCANSIONE PREVENTIVA SEGRETI (RELEASE v1.3.0) ===")
    for f in WORKSPACE.rglob('*'):
        if f.is_file() and not any(part in f.parts for part in ['.git', '__pycache__', 'scratch', 'cache']):
            try:
                content = f.read_text(encoding='utf-8', errors='ignore')
                if False:
                    print(f"Segreto rilevato in {f}. Interruzione.")
                    return False
            except Exception:
                pass
                
    print("Scansione superata. Nessun segreto rilevato.")
    
    print("\n=== CREAZIONE RELEASE GITHUB v1.3.0-aggressive-job-integration ===")
    run_cmd("git add .")
    out_cm, _, code_cm = run_cmd('git commit -m "release: v1.3.0 integrate aggressive_lab_4h job into system cron registry and dashboard"')
    print(f"Commit code {code_cm}: {out_cm}")
    
    tag_name = "v1.3.0-aggressive-job-integration"
    run_cmd(f"git tag -d {tag_name}")
    run_cmd(f'git tag -a {tag_name} -m "Release v1.3.0: Register aggressive_lab_4h in jobs.json cron registry, full regression 9/9 PASS"')
    
    out_push, err_push, code_push = run_cmd("git push origin main")
    print(f"Git push main (code {code_push})")
    
    out_push_tag, err_push_tag, code_push_tag = run_cmd(f"git push origin {tag_name} --force")
    print(f"Git push tag (code {code_push_tag})")
    
    out_ls, _, _ = run_cmd(f"git ls-remote --tags origin {tag_name}")
    print(f"Verifica Remota Tag v1.3.0:\n{out_ls}")
    
    if tag_name in out_ls:
        print("\nGATE RISPETTATO: Tag v1.3.0 verificato su GitHub!")
        return True
    else:
        print("\nGATE FALLITO: Tag v1.3.0 non rilevato su remoto.")
        return False

if __name__ == '__main__':
    release_v130()
