"""
Extracts latest replies from devqa and docky session databases.
"""
import sqlite3
from pathlib import Path

def get_latest(profile):
    db_path = Path(f'/opt/data/profiles/{profile}/state.db')
    if not db_path.exists():
        return "N/A"
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.execute("SELECT id FROM sessions ORDER BY updated_at DESC LIMIT 1")
    r = c.fetchone()
    if not r:
        conn.close()
        return "N/A"
    sid = r[0]
    c.execute("SELECT role, content FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT 2", (sid,))
    msgs = c.fetchall()
    conn.close()
    out = []
    for m in reversed(msgs):
        out.append(f"[{m[0]}]: {m[1][:300]}...")
    return "\n".join(out)

if __name__ == '__main__':
    print("=== DEVQA V2 CERTIFICATION ===")
    print(get_latest("devqa"))
    print("\n=== DOCKY V2 CERTIFICATION ===")
    print(get_latest("docky"))
