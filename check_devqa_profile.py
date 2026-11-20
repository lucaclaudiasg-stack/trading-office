"""
Checks if devqa is registered in Hermes profiles and inspects its status.
"""
from tui_gateway.server import handle_request

def check():
    reply = handle_request({"jsonrpc": "2.0", "id": 1, "method": "profiles.list", "params": {}})
    profiles = reply.get("result", {}).get("profiles", [])
    print(f"Total profiles: {len(profiles)}")
    for p in profiles:
        if p["name"] == "devqa":
            print("devqa profile FOUND:", p)
            return
    print("devqa profile NOT found in profiles.list")

if __name__ == '__main__':
    check()
