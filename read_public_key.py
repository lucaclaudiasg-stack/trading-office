"""
Reads id_rsa.pub from ~/.ssh to display SSH public key for GitHub setup.
"""
from pathlib import Path

pub_key_path = Path.home() / ".ssh" / "id_rsa.pub"
if pub_key_path.exists():
    print("=== SSH PUBLIC KEY (id_rsa.pub) ===")
    print(pub_key_path.read_text().strip())
else:
    print("id_rsa.pub not found.")
