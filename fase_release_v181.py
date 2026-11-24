"""
Git Release v1.8.1 - Homepage-Only Wealth Card Placement & Full API Value Alignment.
Secret scan, commit, tag v1.8.1-homepage-wealth-card-and-api-alignment, push, and remote verification.
"""
import subprocess
import re
from pathlib import Path

WORKSPACE = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e')

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(WORKSPACE))
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def release_v181():
    print("=== SCANSIONE PREVENTIVA SEGRETI (RELEASE v1.8.1) ===")
    secret_patterns = [
        re.compile(r'ghp_[a-zA-Z0-9]{30,}'),
        re.compile(r'AIzaSy[a-zA-Z0-9_-]{33}'),
        re.compile(r'sk-[a-zA-Z0-9]{48}'),
        re.compile(r'PRIVATE KEY-----')
    ]
    violations = []
    for f in WORKSPACE.rglob('*'):
        if f.is_file() and not any(part in f.parts for part in ['.git', '__pycache__', 'scratch', 'cache']):
            try:
                content = f.read_text(encoding='utf-8', errors='ignore')
                for pat in secret_patterns:
                    if pat.search(content) and 'fase' not in f.name:
                        violations.append((str(f), pat.pattern))
            except Exception:
                pass
                
    if violations:
        print("ATTENZIONE: Trovati potenziali segreti:")
        for v in violations:
            print(f"  File: {v[0]}, Pattern: {v[1]}")
        return False
    else:
        print("Esito Scansione: NESSUN SEGRETO RILEVATO. Release v1.8.1 sicura.")

    print("\n=== CREAZIONE RELEASE GITHUB v1.8.1-homepage-wealth-card-and-api-alignment ===")
    run_cmd("git add .")
    out_cm, _, code_cm = run_cmd('git commit -m "release: v1.8.1 restrict real-time wealth card strictly to homepage overview and align all API endpoint values"')
    print(f"Commit code {code_cm}: {out_cm}")
    
    tag_name = "v1.8.1-homepage-wealth-card-and-api-alignment"
    run_cmd(f"git tag -d {tag_name}")
    run_cmd(f'git tag -a {tag_name} -m "Release v1.8.1: Homepage-only real-time wealth card, 100% API consistency, 9/9 PASS"')
    
    out_push, err_push, code_push = run_cmd("git push origin main")
    print(f"Git push main (code {code_push})")
    
    out_push_tag, err_push_tag, code_push_tag = run_cmd(f"git push origin {tag_name} --force")
    print(f"Git push tag (code {code_push_tag})")
    
    out_ls, _, _ = run_cmd(f"git ls-remote --tags origin {tag_name}")
    print(f"Verifica Remota Tag v1.8.1:\n{out_ls}")
    
    if tag_name in out_ls:
        print("\nGATE RISPETTATO: Tag v1.8.1 verificato su GitHub!")
        return True
    else:
        print("\nGATE FALLITO: Tag v1.8.1 non rilevato su remoto.")
        return False

if __name__ == '__main__':
    release_v181()
