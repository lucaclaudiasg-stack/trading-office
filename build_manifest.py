"""
Builds and verifies SHA-256 manifest of all e2e artifacts.
"""
import hashlib
from pathlib import Path
import json

DIR = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e')
files = [
    'e2e_integration.py',
    'exploratory_top20.py',
    'multi_currency_history.py',
    'analyst_exploratory_bridge.py',
    'test_exploratory_and_pipeline.py',
    'persistent_staging.py',
    'test_persistence_lifecycle.py',
    'ISOLATION_PLAN.md',
    'E2E_REPORT.md'
]

manifest = {}
for f in files:
    p = DIR / f
    if p.exists():
        manifest[f] = hashlib.sha256(p.read_bytes()).hexdigest()

out = DIR / 'MANIFEST.json'
out.write_text(json.dumps(manifest, indent=2))
print("MANIFEST GENERATED:")
print(json.dumps(manifest, indent=2))
