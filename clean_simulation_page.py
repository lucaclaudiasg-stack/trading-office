"""
Clean targeted update for dashboard_backend.py:
1. Keeps Simulation section focused strictly on the 3 original portfolios (Hermes AI, Buy & Hold, Defensive EUR).
2. Removes all Aggressive Lab panels and boxes from #sec-simulation.
3. Updates Chart 1 dataset to plot only the 3 original lines.
4. Preserves #sec-aggressive and nav-aggressive untouched.
"""
from pathlib import Path
import shutil

BACKEND_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py')
BACKUP_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py.bak_clean_simulation')

def clean_simulation():
    shutil.copy2(BACKEND_PATH, BACKUP_PATH)
    print("Backup created at:", BACKUP_PATH)
    
    code = BACKEND_PATH.read_text(encoding='utf-8')
    
    # 1. Restore Simulation cards grid to 3 columns and remove Hermes Aggressive card
    old_grid_4col = '<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">'
    new_grid_3col = '<div class="grid grid-cols-1 md:grid-cols-3 gap-3">'
    if old_grid_4col in code:
        code = code.replace(old_grid_4col, new_grid_3col)
        
    # Remove Hermes Aggressive Box from simulation grid
    agg_box_start = '<!-- Hermes Aggressive Box -->'
    agg_box_end = '</div>\n            </div>'
    idx_agg_start = code.find(agg_box_start)
    if idx_agg_start != -1:
        # Find the next </div>\n            </div> corresponding to this card and the container
        idx_agg_end = code.find(agg_box_end, idx_agg_start)
        if idx_agg_end != -1:
            code = code[:idx_agg_start] + '</div>' + code[idx_agg_end + len(agg_box_end):]
            print("Removed Hermes Aggressive box from simulation grid.")

    # 2. Remove bottom sec-aggressive-lab-panel from simulation section if present
    panel_start = '<!-- AGGRESSIVE LAB PANEL (V2) - BOTTOM -->'
    panel_end = '</section>\n\n        <!-- SECTION: AGGRESSIVE LAB -->'
    if panel_start in code:
        idx_p_start = code.find(panel_start)
        idx_p_end = code.find('</section>', idx_p_start)
        if idx_p_start != -1 and idx_p_end != -1:
            code = code[:idx_p_start] + code[idx_p_end:]
            print("Removed bottom aggressive panel from simulation section.")

    # 3. Update Chart 1 in JS to keep only 3 lines
    old_chart_datasets = """datasets: [
                            { label: 'Hermes AI', data: [142.42, 143.10, 143.58, 143.20, 143.58, 143.58], borderColor: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.05)', tension: 0.3 },
                            { label: 'Hermes Aggressive', data: [142.42, 143.10, 143.58, 143.58, 143.58, 143.58], borderColor: '#a855f7', backgroundColor: 'rgba(168, 85, 247, 0.15)', tension: 0.3, fill: true },
                            { label: 'Buy & Hold', data: [142.42, 143.10, 143.58, 143.20, 143.58, 143.58], borderColor: '#10b981', borderDash: [4, 4], tension: 0.3 },
                            { label: 'Defensive EUR', data: [142.42, 142.42, 142.42, 142.42, 142.42, 142.42], borderColor: '#f59e0b', tension: 0.1 }
                        ]"""
                        
    new_chart_datasets = """datasets: [
                            { label: 'Hermes AI', data: [142.42, 143.10, 143.58, 143.20, 143.58, 143.58], borderColor: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.1)', tension: 0.3, fill: true },
                            { label: 'Buy & Hold', data: [142.42, 143.10, 143.58, 143.20, 143.58, 143.58], borderColor: '#10b981', borderDash: [4, 4], tension: 0.3 },
                            { label: 'Defensive EUR', data: [142.42, 142.42, 142.42, 142.42, 142.42, 142.42], borderColor: '#f59e0b', tension: 0.1 }
                        ]"""
    if old_chart_datasets in code:
        code = code.replace(old_chart_datasets, new_chart_datasets)
        print("Chart 1 datasets updated to 3 original portfolios.")

    BACKEND_PATH.write_text(code, encoding='utf-8')
    print("Simulation page cleaned successfully.")

if __name__ == '__main__':
    clean_simulation()
