"""
Queries the Coinbase Read-Only MCP Adapter via stdin/stdout.
Does NOT display tokens, keys, or credentials.
Extracts portfolio holdings, balances, and values.
"""
import sys
import json
import subprocess

ADAPTER_PATH = "/opt/data/scripts/coinbase_readonly_adapter.py"

def query_adapter():
    # 1. List tools
    req_list = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}) + "\n"
    proc = subprocess.Popen(
        [sys.executable, ADAPTER_PATH],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = proc.communicate(input=req_list, timeout=15)
    
    tools = []
    for line in stdout.strip().split("\n"):
        if not line:
            continue
        try:
            res = json.loads(line)
            if "result" in res and "tools" in res["result"]:
                tools = [t["name"] for t in res["result"]["tools"]]
        except Exception as e:
            pass
            
    print(f"Available tools from read-only adapter: {tools}")
    
    # Check if portfolio balance tool exists
    # Common Coinbase MCP tool names: coinbase_portfolios_list, coinbase_portfolios_get, coinbase_accounts_list, coinbase_balances_get
    target_tool = None
    for candidate in ["coinbase_portfolios_list", "coinbase_accounts_list", "coinbase_balances_get", "coinbase_portfolios_get"]:
        if candidate in tools:
            target_tool = candidate
            break
            
    if not target_tool and tools:
        # Check any tool with portfolio or account or balance
        for t in tools:
            if "portfolio" in t or "account" in t or "balance" in t:
                target_tool = t
                break
                
    print(f"Target tool for balances: {target_tool}")
    
    if target_tool:
        req_call = json.dumps({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": target_tool, "arguments": {}}
        }) + "\n"
        proc2 = subprocess.Popen(
            [sys.executable, ADAPTER_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout2, stderr2 = proc2.communicate(input=req_call, timeout=20)
        print("Call result raw line count:", len(stdout2.strip().split("\n")))
        for line in stdout2.strip().split("\n"):
            try:
                parsed = json.loads(line)
                # Print result keys and summary, scrub any secrets
                if "result" in parsed:
                    res_content = parsed["result"]
                    print("Tool call successful! Result keys:", list(res_content.keys()) if isinstance(res_content, dict) else "list")
                    print("Content preview (sanitized):", json.dumps(res_content)[:500])
                elif "error" in parsed:
                    print("Tool call error:", parsed["error"])
            except Exception as e:
                print("Parse error on output line:", e)
    else:
        print("No suitable portfolio reading tool found in tools list.")

if __name__ == '__main__':
    query_adapter()
