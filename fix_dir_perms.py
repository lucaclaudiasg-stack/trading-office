import os
import stat

paths = [
    '/opt/data/trading-office-data',
    '/opt/data/profiles/linu/workspace/eth-history'
]

for p in paths:
    if os.path.exists(p):
        os.chmod(p, 0o755)
        st = os.stat(p)
        print(f"{p}: mode={oct(st.st_mode)[-3:]}, uid={st.st_uid}")
