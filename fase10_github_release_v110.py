"""
Fase 10 - Secret Scanning, Commit, Tag v1.1.0-aggressive-lab, Push, and Remote Verification on GitHub.
"""
import subprocess
import re
from pathlib import Path

WORKSPACE = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e')

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(WORKSPACE))
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def scan_secrets():
    print("=== SCANSIONE PREVENTIVA DEI SEGRETI (RELEASE v1.1.0) ===")
    secret_patterns = [
        re.compile(r'ghp_[a-zA-Z0-9]{30,}'),
        re.compile(r'AIzaSy[a-zA-Z0-9_-]{33}'),
        re.compile(r'sk-[a-zA-Z0-9]{48}'),
        re.compile(r'-----BEGIN (?:RSA|EC|DSA|OPENSSH) PRIVATE KEY-----')
    ]
    violations = []
    for f in WORKSPACE.rglob('*'):
        if f.is_file() and not any(part in f.parts for part in ['.git', '__pycache__', 'scratch', 'cache']):
            try:
                content = f.read_text(encoding='utf-8', errors='ignore')
                for pat in secret_patterns:
                    if pat.search(content):
                        violations.append((str(f), pat.pattern))
            except Exception:
                pass
                
    if violations:
        print("ATTENZIONE: Trovati potenziali segreti:")
        for v in violations:
            print(f"  File: {v[0]}, Pattern: {v[1]}")
        return False
    else:
        print("Esito Scansione: NESSUN SEGRETO RILEVATO. Release v1.1.0 sicura.")
        return True

def release_v110():
    if not scan_secrets():
        print("BLOCCO: Scansione segreti fallita. Interruzione.")
        return False
        
    print("\n=== CREAZIONE RELEASE GITHUB v1.1.0-aggressive-lab ===")
    # 1. Git add
    run_cmd("git add .")
    
    # 2. Commit
    st_out, _, _ = run_cmd("git status --porcelain")
    if st_out:
        out_cm, err_cm, code_cm = run_cmd('git commit -m "release: v1.1.0-aggressive-lab integration with 4 portfolios and ruin risk analysis"')
        print(f"Commit output (code {code_cm}): {out_cm}")
    else:
        print("Working tree already clean, tagging current HEAD.")

    # 3. Create Tag v1.1.0-aggressive-lab
    tag_name = "v1.1.0-aggressive-lab"
    run_cmd(f"git tag -d {tag_name}")
    out_tag, err_tag, code_tag = run_cmd(f'git tag -a {tag_name} -m "Release v1.1.0: Aggressive Lab integration, 4 portfolios comparative view, and time-to-ruin analysis"')
    print(f"Tag creation (code {code_tag}): {out_tag} {err_tag}")

    # 4. Push commit and tag
    out_push, err_push, code_push = run_cmd("git push origin main")
    print(f"Git push main (code {code_push}): {out_push} {err_push}")
    
    out_push_tag, err_push_tag, code_push_tag = run_cmd(f"git push origin {tag_name} --force")
    print(f"Git push tag (code {code_push_tag}): {out_push_tag} {err_push_tag}")

    # 5. Verify Tag exists on remote
    out_ls_remote, _, _ = run_cmd(f"git ls-remote --tags origin {tag_name}")
    print(f"Verifica Remota Tag su GitHub:\n{out_ls_remote}")
    
    if tag_name in out_ls_remote:
        print(f"\nGATE RISPETTATO: Tag {tag_name} verificato con successo su GitHub!")
        return True
    else:
        print("\nGATE FALLITO: Tag non rilevato sul repository remoto.")
        return False

if __name__ == '__main__':
    release_v110()
