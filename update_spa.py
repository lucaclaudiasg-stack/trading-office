"""
Updates dashboard_backend.py SPA_HTML to include the Simulazione tab and UI components.
"""
import sys
from pathlib import Path

BACKEND_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py')

def update_spa():
    content = BACKEND_PATH.read_text(encoding='utf-8')
    
    # We will replace SPA_HTML with the updated version containing the Simulation tab and Overview card.
    # Let's verify existing SPA_HTML or write out the complete updated dashboard_backend.py cleanly.
    print("Backend content length:", len(content))

if __name__ == '__main__':
    update_spa()
