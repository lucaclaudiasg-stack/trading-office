"""
Extracts latest reply from docky session database.
"""
import sqlite3
from pathlib import Path

def get_docky_reply():
    db_path = Path('/opt/data/profiles/docky/state.db')
    if not db_path.exists():
        return "No state.db found for docky"
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.execute("SELECT id FROM sessions ORDER BY started_at DESC LIMIT 1")
    r = c.fetchone()
    if not r:
        conn.close()
        return "No sessions found for docky"
    sid = r[0]
    c.execute("SELECT role, content FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT 2", (sid,))
    msgs = c.fetchall()
    conn.close()
    out = []
    for m in reversed(msgs):
        out.append(f"[{m[0]}]: {m[1]}")
    return "\n".join(out)

if __name__ == '__main__':
    print(get_docky_reply())
