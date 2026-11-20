"""
Extracts latest replies from devqa and docky session databases.
"""
import sqlite3
import json
from pathlib import Path

def get_latest_reply(profile_name):
    db_path = Path(f'/opt/data/profiles/{profile_name}/state.db')
    if not db_path.exists():
        return f"No state.db found for {profile_name}"
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM sessions ORDER BY updated_at DESC LIMIT 1")
    row = cursor.fetchone()
    if not row:
        conn.close()
        return f"No sessions found for {profile_name}"
    session_id = row[0]
    
    cursor.execute("SELECT role, content FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT 4", (session_id,))
    msgs = cursor.fetchall()
    conn.close()
    
    res = []
    for m in reversed(msgs):
        res.append(f"[{m[0]}]: {m[1][:300]}...")
    return "\n".join(res)

if __name__ == '__main__':
    print("=== DEVQA LATEST REPLY ===")
    print(get_latest_reply("devqa"))
    print("\n=== DOCKY LATEST REPLY ===")
    print(get_latest_reply("docky"))
