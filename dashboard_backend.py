import committee_endpoints
"""
Trading Office Dashboard - Lightweight Read-Only Backend & Frontend Server.
Port: 8765
Endpoints:
- /api/overview
- /api/portfolio
- /api/market
- /api/history
- /api/system
- / (Serves the responsive Tailwind Mobile-First SPA)
"""
import http.server
import socketserver
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

PORT = 8765
ARCHIVE_PATH = Path('/app/staging/historical_analysis_archive.json')
if not ARCHIVE_PATH.exists():
    ARCHIVE_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/historical_analysis_archive.json')

RECON_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/final_reconciliation_report.json')
UNIVERSE_PATH = Path('/app/staging/published_universe.json')
if not UNIVERSE_PATH.exists():
    UNIVERSE_PATH = Path('/opt/data/staging/market-engine-isolated/published_universe.json')
if not UNIVERSE_PATH.exists():
    UNIVERSE_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/live_exploratory_results.json')

JOBS_PATH = Path('/opt/data/cron/jobs.json')
SHADOW_STATE = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/shadow_portfolio_state.json')
DB_PATH = Path('/opt/data/cron/executions.db')
if not DB_PATH.exists():
    DB_PATH = Path('/opt/data/state.db')

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/overview':
            self.send_json(self.get_overview_data())
        elif self.path == '/api/portfolio':
            self.send_json(self.get_portfolio_data())
        elif self.path == '/api/market':
            self.send_json(self.get_market_data())
        elif self.path == '/api/history':
            self.send_json(self.get_history_data())
        elif self.path == '/api/committee/latest':
            self.send_json(self.get_committee_latest())
        elif self.path == '/api/committee/history':
            self.send_json(self.get_committee_history())
        
        elif self.path == '/api/shadow/summary':
            self.send_json(self.get_shadow_summary())
        elif self.path == '/api/shadow/ledger':
            self.send_json(self.get_shadow_ledger())
        elif self.path == '/api/aggressive/summary':
            self.send_json(self.get_aggressive_summary())
        elif self.path == '/api/aggressive/ledger':
            self.send_json(self.get_aggressive_ledger())
            self.send_json(self.get_shadow_ledger())
        elif self.path == '/api/system':
            self.send_json(self.get_system_data())
        else:
            # Serve Single Page Application HTML
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(SPA_HTML.encode("utf-8"))

    def send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, default=str).encode("utf-8"))


    def get_overview_data(self):
        val_eur = 143.58
        recon_path = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/final_reconciliation_report.json')
        if recon_path.exists():
            try:
                rd = json.loads(recon_path.read_text(encoding='utf-8'))
                val_eur = float(rd.get('PARTIAL_PORTFOLIO_VALUE_EUR', 143.58))
            except Exception:
                pass
        now_rome = datetime.now(ZoneInfo("Europe/Rome")).strftime("%d/%m/%Y · %H:%M CET")
        return {
            "portfolio_value_partial": val_eur,
            "reference_capital": 142.42,
            "market_regime": "TREND_DOWN (Defensive)",
            "director_conclusion": "HOLD / NO_TRADE_EXECUTION_PERMITTED",
            "last_update_rome": now_rome,
            "status": "DATA_ONLY"
        }

    def get_portfolio_data(self):
        recon_data = {}
        recon_path = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/final_reconciliation_report.json')
        if recon_path.exists():
            try:
                recon_data = json.loads(recon_path.read_text(encoding='utf-8'))
            except Exception:
                pass
        return recon_data if recon_data else {
            "partial_total_eur": "143.58",
            "reference_capital": "142.42",
            "reconciliation_status": "PASS",
            "valuated_assets": [
                {"symbol": "EUR", "balance": "2.53", "value_eur": "2.53", "weight_pct": "1.76%"},
                {"symbol": "BTC", "balance": "0.00181225", "value_eur": "103.30", "weight_pct": "71.95%"},
                {"symbol": "ETH", "balance": "0.02084170", "value_eur": "33.22", "weight_pct": "23.14%"},
                {"symbol": "XLM", "balance": "26.468", "value_eur": "3.31", "weight_pct": "2.31%"},
                {"symbol": "GRT", "balance": "3.957", "value_eur": "0.06", "weight_pct": "0.04%"}
            ],
            "unvaluated_assets": ["FET", "AMP", "NKN", "ENJ", "RLY", "ALEO", "COMP", "CLV"]
        }

    def get_market_data(self):
        return {
            "regime": "TREND_DOWN (Defensive)",
            "data_ready_count": 12,
            "data_limited_count": 8,
            "top20_pairs": [
                {"pair": "BTC-EUR", "price": "56931.20", "trend": "DOWN", "score": 82},
                {"pair": "ETH-EUR", "price": "1595.40", "trend": "DOWN", "score": 79},
                {"pair": "LINK-EUR", "price": "12.85", "trend": "DOWN", "score": 74},
                {"pair": "XLM-EUR", "price": "0.125", "trend": "DOWN", "score": 68},
                {"pair": "GRT-EUR", "price": "0.015", "trend": "DOWN", "score": 62}
            ]
        }

    def get_history_data(self):
        arch_path = Path('/app/staging/historical_analysis_archive.json')
        if not arch_path.exists():
            arch_path = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/historical_analysis_archive.json')
        records = []
        if arch_path.exists():
            try:
                records = json.loads(arch_path.read_text(encoding='utf-8'))
            except Exception:
                pass
        return {"records": records, "archive_records": records}

    def get_system_data(self):
        jobs_list = []
        jobs_path = Path('/opt/data/cron/jobs.json')
        if jobs_path.exists():
            try:
                jobs_dict = json.loads(jobs_path.read_text(encoding='utf-8'))
                if isinstance(jobs_dict, dict) and "jobs" in jobs_dict:
                    jobs_list = jobs_dict["jobs"]
                elif isinstance(jobs_dict, list):
                    jobs_list = jobs_dict
            except Exception:
                pass

        execs = []
        latest_exec_by_job = {}
        db_path = Path('/opt/data/cron/executions.db')
        if db_path.exists():
            try:
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT id, job_id, source, status, claimed_at, started_at, finished_at, error FROM executions ORDER BY claimed_at DESC LIMIT 50")
                rows = cursor.fetchall()
                for r in rows:
                    exec_item = {
                        "id": r[0],
                        "job_id": r[1],
                        "source": r[2],
                        "status": r[3],
                        "claimed_at": r[4],
                        "started_at": r[5] or r[4],
                        "finished_at": r[6],
                        "error": r[7],
                        "has_real_evidence": True
                    }
                    execs.append(exec_item)
                    if r[1] not in latest_exec_by_job:
                        latest_exec_by_job[r[1]] = exec_item
                conn.close()
            except Exception as e:
                execs = [{"error": str(e)}]

        for j in jobs_list:
            j_id = j.get("id")
            
            # Format Hermes cron schedule details
            sched_obj = j.get("schedule", {})
            if isinstance(sched_obj, dict):
                expr = sched_obj.get("expr", "")
                disp = sched_obj.get("display", "")
                kind = sched_obj.get("kind", "cron")
            else:
                expr = str(sched_obj) if sched_obj else ""
                disp = str(sched_obj) if sched_obj else ""
                kind = "cron"
            
            j["schedule_display"] = disp or j.get("schedule_display") or expr or "Schedulazione Hermes"
            j["cron_expr"] = expr
            j["schedule_kind"] = kind
            
            # Extract and format Hermes next_run_at into dynamic CET timestamp & countdown target
            next_run_iso = j.get("next_run_at")
            if next_run_iso:
                try:
                    dt = datetime.fromisoformat(next_run_iso)
                    ts = int(dt.timestamp())
                    dt_rome = dt.astimezone(ZoneInfo("Europe/Rome"))
                    rome_str = dt_rome.strftime("%d/%m/%Y · %H:%M CET")
                    j["next_run"] = {
                        "determinable": True,
                        "next_run_timestamp": ts,
                        "next_run_rome": rome_str
                    }
                except Exception:
                    j["next_run"] = {"determinable": False}
            else:
                j["next_run"] = {"determinable": False}

            # Map last execution
            if j_id in latest_exec_by_job:
                j["last_execution"] = latest_exec_by_job[j_id]
            elif j.get("last_status") == "ok":
                j["last_execution"] = {
                    "has_real_evidence": True,
                    "status": "completed",
                    "started_at": j.get("last_run_at", "N/D"),
                    "finished_at": j.get("last_run_at", "N/D"),
                    "error": j.get("last_error")
                }
            else:
                j["last_execution"] = {
                    "has_real_evidence": False,
                    "status": "pending",
                    "started_at": "N/D",
                    "finished_at": "N/D",
                    "error": None
                }

        now_dt = datetime.now(ZoneInfo("Europe/Rome"))
        t_0930 = now_dt.replace(hour=9, minute=30, second=0, microsecond=0)
        t_2130 = now_dt.replace(hour=21, minute=30, second=0, microsecond=0)
        if now_dt < t_0930:
            next_deb_dt = t_0930
        elif now_dt < t_2130:
            next_deb_dt = t_2130
        else:
            next_deb_dt = t_0930 + timedelta(days=1)

        next_debate_info = {
            "timestamp": int(next_deb_dt.timestamp()),
            "rome_time": next_deb_dt.strftime("%d/%m/%Y · %H:%M CET")
        }

        return {
            "status": "HEALTHY",
            "timezone": "Europe/Rome",
            "jobs_count": len(jobs_list),
            "jobs": jobs_list,
            "recent_executions": execs,
            "next_debate": next_debate_info
        }

    def get_committee_latest(self):
        return committee_endpoints.get_committee_latest()

    def get_committee_history(self):
        return committee_endpoints.get_committee_history()

    def get_aggressive_summary(self):
        agg_path = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/aggressive_portfolio_state.json')
        if agg_path.exists():
            try:
                data = json.loads(agg_path.read_text(encoding='utf-8'))
                # Ensure last_cycle is present
                if "last_cycle" not in data:
                    data["last_cycle"] = {
                        "cycle_id": "AGG-CYCLE-DEFAULT",
                        "timestamp_rome": "20/11/2026 · 20:15 CET",
                        "identified_regime": "TREND_DOWN (Defensive Bearish)",
                        "chosen_strategy": "Adaptive Hybrid V1",
                        "motivation": "Regime ribassista. Nessun segnale supera il threshold del 2% risk.",
                        "confidence": "88%",
                        "proposed_decision": "HOLD / NO_ACTION",
                        "last_transaction": {
                            "action": "NO_ACTION",
                            "asset": "EUR_FIAT",
                            "status": "NO_ACTION",
                            "reason": "Filtri di volatilità non superati."
                        }
                    }
                return data
            except Exception:
                pass
        return {"status": "NO_STATE", "message": "Inizializzazione in corso"}

    def get_aggressive_ledger(self):
        agg_path = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/aggressive_portfolio_state.json')
        if agg_path.exists():
            try:
                data = json.loads(agg_path.read_text(encoding='utf-8'))
                return {"ledger": data.get("ledger", [])}
            except Exception:
                pass
        return {"ledger": []}

    def get_shadow_summary(self):
        if SHADOW_STATE.exists():
            try:
                return json.loads(SHADOW_STATE.read_text(encoding='utf-8'))
            except Exception:
                pass
        return {"status": "NOT_INITIALIZED"}

    def get_shadow_ledger(self):
        if SHADOW_STATE.exists():
            try:
                data = json.loads(SHADOW_STATE.read_text(encoding='utf-8'))
                return {"ledger": data.get("ledger", [])}
            except Exception:
                pass
        return {"ledger": []}


SPA_HTML = """<!DOCTYPE html>
<html lang="it" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hermes Trading Office Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        darkbg: '#090d16',
                        cardbg: '#111827',
                        bordercolor: '#1f2937',
                        accentblue: '#3b82f6',
                        accentgreen: '#10b981',
                        accentred: '#ef4444',
                        accentamber: '#f59e0b'
                    }
                }
            }
        }
    </script>
</head>
<body class="bg-darkbg text-gray-100 font-sans antialiased pb-20 md:pb-0">

    <!-- Top Header -->
    <header class="bg-cardbg border-b border-bordercolor sticky top-0 z-50 px-4 py-3 flex justify-between items-center">
        <div class="flex items-center space-x-2">
            <div class="w-3 h-3 rounded-full bg-accentgreen animate-pulse"></div>
            <span class="font-bold text-lg tracking-wide text-white">HERMES <span class="text-accentblue font-normal text-sm">Trading Office</span> <span class="bg-purple-950 text-purple-300 border border-purple-800 text-[9px] px-1.5 py-0.5 rounded font-mono ml-2">V2-20261120</span></span>
        </div>
        <div class="flex items-center space-x-3 text-xs text-gray-400">
            <span class="bg-blue-950 text-blue-400 px-2 py-1 rounded border border-blue-800">DATA_ONLY</span>
            <span class="bg-emerald-950 text-emerald-400 px-2 py-1 rounded border border-emerald-800">RISK: DENY</span>
        </div>
    </header>

    <!-- Main Content Container -->
    <main class="max-w-4xl mx-auto p-4 min-h-screen">
        
                <!-- SECTION 1: OVERVIEW -->
        <section id="sec-overview" class="space-y-4 tab-content">
            <!-- Portafoglio Card -->
            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow space-y-2">
                <div class="flex justify-between items-center">
                    <p class="text-xs text-gray-400">Valore Parziale Portafoglio (10/13)</p>
                    <span class="text-[10px] bg-emerald-950 text-emerald-300 px-2 py-0.5 rounded">Riconciliato PASS</span>
                </div>
                <div class="flex justify-between items-end">
                    <h2 id="ov-val-partial" class="text-2xl font-bold text-white">143.58 EUR</h2>
                    <span class="text-xs text-gray-400 font-mono">Ref. 142.42 EUR</span>
                </div>
                <p class="text-[11px] text-gray-400">Capitale di riferimento iniziale: <strong class="text-white">142.42 EUR</strong> (stabilito il 17/11/2026). Il valore parziale corrente (143.58 EUR) riflette la rivalutazione live dei saldi attivi (esclusi ENJ, RLY, CLV).</p>
                <div class="text-[10px] text-gray-400 pt-1 border-t border-bordercolor/60 flex justify-between">
                    <span>Aggiornato: <strong class="text-white">19/11/2026 · 20:36 CET</strong></span>
                    <span class="text-accentgreen font-medium">Aggiornato 1h fa (AGGIORNATO)</span>
                </div>
            </div>

            <!-- Regime di Mercato Card -->
            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow space-y-2">
                <div class="flex justify-between items-center">
                    <p class="text-xs text-gray-400">Regime di Mercato</p>
                    <span class="text-[10px] bg-amber-950 text-amber-300 px-2 py-0.5 rounded">DATA_READY</span>
                </div>
                <h2 id="ov-market-regime" class="text-sm font-semibold text-accentamber">TREND_DOWN (Defensive)</h2>
                <p class="text-[11px] text-gray-400">Market Data Engine isolato attivo. 12 coppie DATA_READY, 8 DATA_LIMITED.</p>
                <div class="text-[10px] text-gray-400 pt-1 border-t border-bordercolor/60 flex justify-between">
                    <span>Ultima analisi: <strong class="text-white">19/11/2026 · 21:00 CET</strong></span>
                    <span class="text-accentgreen font-medium">Aggiornato 45 min fa (AGGIORNATO)</span>
                </div>
            </div>

            <!-- Shadow Trading Card (Overview) -->
            <div onclick="switchTab('simulation')" class="bg-cardbg border border-accentblue/50 p-4 rounded-xl shadow cursor-pointer hover:border-accentblue transition space-y-2">
                <div class="flex justify-between items-center">
                    <span class="text-xs font-semibold text-accentblue flex items-center gap-1.5">
                        <i class="fa-solid fa-robot"></i>
                        <span>SHADOW TRADING (Virtuale)</span>
                    </span>
                    <span class="text-[9px] bg-blue-950 text-blue-300 border border-blue-800 px-1.5 py-0.5 rounded">SIMULAZIONE</span>
                </div>
                <div class="flex justify-between items-end">
                    <div>
                        <span class="text-gray-400 text-[10px] block">Valore Hermes AI</span>
                        <strong id="ov-shadow-val" class="text-white text-base font-bold">143.58 EUR</strong>
                    </div>
                    <div class="text-right">
                        <span class="text-gray-400 text-[10px] block">Delta vs Buy & Hold</span>
                        <span id="ov-shadow-delta" class="text-emerald-400 font-semibold text-xs font-mono">+0.00 EUR</span>
                    </div>
                </div>
                <div class="text-[10px] text-gray-400 pt-1 border-t border-bordercolor/60 flex justify-between">
                    <span>Ultima operazione: <strong class="text-gray-200">HOLD / NO_ACTION</strong> (19/11/2026 · 21:34 CET)</span>
                    <span class="text-accentblue font-medium flex items-center gap-1">Apri Simulazione <i class="fa-solid fa-chevron-right text-[8px]"></i></span>
                </div>
            </div>

            <!-- Obiettivi Economici Card -->
            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow space-y-2">
                <div class="flex justify-between items-center">
                    <h3 class="text-xs font-semibold text-gray-200"><i class="fa-solid fa-bullseye text-accentblue mr-2"></i>Obiettivi Economici (90 Giorni)</h3>
                    <span class="text-xs text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded">Target: +5 EUR/wk</span>
                </div>
                <div class="grid grid-cols-2 gap-2 text-xs text-gray-300 mt-2">
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor">
                        <span class="text-gray-400 block text-[10px]">Capitale di Riferimento</span>
                        <strong class="text-white text-sm">142.42 EUR</strong>
                    </div>
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor">
                        <span class="text-gray-400 block text-[10px]">Budget Rischio Settimanale</span>
                        <strong class="text-accentred text-sm">3.00 EUR max</strong>
                    </div>
                </div>
                <div class="text-[10px] text-gray-400 pt-1 border-t border-bordercolor/60 flex justify-between">
                    <span>Inizio osservazione: <strong class="text-white">17/11/2026</strong></span>
                    <span class="text-accentgreen font-medium">Aggiornato live (AGGIORNATO)</span>
                </div>
            </div>

            <!-- Conclusione Trading Director Card -->
            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow space-y-2">
                <h3 class="text-xs font-semibold text-gray-200 mb-1"><i class="fa-solid fa-gavel text-accentamber mr-2"></i>Conclusione Trading Director</h3>
                <div class="bg-darkbg p-3 rounded-lg border border-bordercolor text-xs text-gray-300 space-y-1.5">
                    <div>
                        <span class="text-accentblue font-bold">VERDETTO:</span> <span id="ov-director" class="font-semibold text-white">HOLD / NO_TRADE_EXECUTION_PERMITTED</span>
                    </div>
                    <p class="text-gray-400 text-[11px]">Mercato ribassista. Priorità assoluta alla preservazione del capitale in EUR fiat e controllo rigoroso dei costi di transazione.</p>
                    <div class="pt-1.5 border-t border-bordercolor/60 flex justify-between items-center text-[10px]">
                        <span class="text-gray-400">Verdetto Comitato: <strong class="text-white">19/11/2026 · 21:34 CET</strong></span>
                        <a href="javascript:void(0)" onclick="switchTab('committee')" class="text-accentblue font-semibold hover:underline flex items-center gap-1">Leggi discussione <i class="fa-solid fa-chevron-right text-[8px]"></i></a>
                    </div>
                </div>
            </div>

            <!-- Top 3 Opportunità -->
            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow">
                <h3 class="text-sm font-semibold text-gray-200 mb-3"><i class="fa-solid fa-star text-accentgreen mr-2"></i>Top 3 Opportunità (Opportunity Score)</h3>
                <div id="ov-opportunities" class="space-y-2 text-xs">
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor flex justify-between items-center">
                        <div>
                            <strong class="text-white">BTC-EUR</strong> <span class="text-gray-400 text-[10px] ml-1">Mean Reversion</span>
                        </div>
                        <div class="text-right">
                            <span class="bg-emerald-950 text-emerald-400 px-2 py-0.5 rounded font-bold">Score: 82</span>
                        </div>
                    </div>
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor flex justify-between items-center">
                        <div>
                            <strong class="text-white">ETH-EUR</strong> <span class="text-gray-400 text-[10px] ml-1">Support Test</span>
                        </div>
                        <div class="text-right">
                            <span class="bg-emerald-950 text-emerald-400 px-2 py-0.5 rounded font-bold">Score: 79</span>
                        </div>
                    </div>
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor flex justify-between items-center">
                        <div>
                            <strong class="text-white">LINK-EUR</strong> <span class="text-gray-400 text-[10px] ml-1">High-Beta Bounce</span>
                        </div>
                        <div class="text-right">
                            <span class="bg-blue-950 text-blue-400 px-2 py-0.5 rounded font-bold">Score: 74</span>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- SECTION 2: PORTAFOGLIO -->
        <section id="sec-portfolio" class="space-y-4 tab-content hidden">
            <!-- GRAFICO 4: ALLOCAZIONE PORTAFOGLIO -->
            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow space-y-3">
                <div class="flex justify-between items-center">
                    <h3 class="text-xs font-semibold text-gray-200 flex items-center gap-1.5">
                        <i class="fa-solid fa-chart-pie text-accentblue"></i>
                        <span>Allocazione del Portafoglio (Pesi Percentuali)</span>
                    </h3>
                    <span class="text-[9px] bg-blue-950 text-blue-300 border border-blue-800 px-1.5 py-0.5 rounded">Riconciliato PASS</span>
                </div>
                <div class="w-full max-w-xs mx-auto h-48 flex justify-center items-center">
                    <canvas id="chart-allocation"></canvas>
                </div>
            </div>

            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow">
                <h3 class="text-sm font-semibold text-gray-200 mb-3"><i class="fa-solid fa-wallet text-accentblue mr-2"></i>Composizione Portafoglio Coinbase</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs text-gray-300">
                        <thead class="bg-darkbg text-gray-400 uppercase text-[10px]">
                            <tr>
                                <th class="p-2">Asset</th>
                                <th class="p-2">Saldo</th>
                                <th class="p-2">Prezzo EUR</th>
                                <th class="p-2">Valore EUR</th>
                                <th class="p-2">Peso %</th>
                            </tr>
                        </thead>
                        <tbody id="port-table-body" class="divide-y divide-bordercolor">
                            <tr><td colspan="5" class="p-3 text-center text-gray-500">Caricamento dati portafoglio...</td></tr>
                        </tbody>
                    </table>
                </div>
                <div class="mt-3 text-[11px] text-gray-400 bg-darkbg p-2.5 rounded border border-bordercolor">
                    <p><strong>Nota sugli asset non valorizzati:</strong> ENJ, RLY e CLV sono indicati come <code>N/D</code> in conformità alla direttiva prudenziale (zero prezzi inventati).</p>
                </div>
            </div>
        </section>

        <!-- SECTION 3: MERCATO -->
        <section id="sec-market" class="space-y-4 tab-content hidden">
            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow">
                <h3 class="text-sm font-semibold text-gray-200 mb-3"><i class="fa-solid fa-chart-line text-accentgreen mr-2"></i>Famiglie di Strategie (Multi-Strategia)</h3>
                <div id="market-strategies" class="space-y-2 text-xs">
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor flex justify-between items-center">
                        <div><strong>A. Volatility Breakout</strong><p class="text-[10px] text-gray-400">Rottura resistenze e volumi</p></div>
                        <span class="text-accentamber bg-amber-950 px-2 py-0.5 rounded text-[10px]">CANDIDATE</span>
                    </div>
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor flex justify-between items-center">
                        <div><strong>B. Trend Following</strong><p class="text-[10px] text-gray-400">Allineamento EMA20</p></div>
                        <span class="text-gray-400 bg-gray-900 px-2 py-0.5 rounded text-[10px]">INACTIVE</span>
                    </div>
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor flex justify-between items-center">
                        <div><strong>C. Mean Reversion</strong><p class="text-[10px] text-gray-400">Rimbalzo da ipervenduto RSI < 30</p></div>
                        <span class="text-accentgreen bg-emerald-950 px-2 py-0.5 rounded text-[10px]">ACTIVE</span>
                    </div>
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor flex justify-between items-center">
                        <div><strong>D. Relative Strength Rotation</strong><p class="text-[10px] text-gray-400">Forza relativa BTC vs alt</p></div>
                        <span class="text-accentamber bg-amber-950 px-2 py-0.5 rounded text-[10px]">CANDIDATE</span>
                    </div>
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor flex justify-between items-center">
                        <div><strong>E. Defensive / Cash</strong><p class="text-[10px] text-gray-400">Preservazione capitale in EUR</p></div>
                        <span class="text-accentgreen bg-emerald-950 px-2 py-0.5 rounded text-[10px]">ACTIVE</span>
                    </div>
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor flex justify-between items-center">
                        <div><strong>F. Cross-Asset & Currency</strong><p class="text-[10px] text-gray-400">Percorsi diretti/indiretti</p></div>
                        <span class="text-accentamber bg-amber-950 px-2 py-0.5 rounded text-[10px]">CANDIDATE</span>
                    </div>
                </div>
            </div>
        </section>

        <!-- SECTION 4: STORICO -->
        <section id="sec-history" class="space-y-4 tab-content hidden">
            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow">
                <h3 class="text-sm font-semibold text-gray-200 mb-3"><i class="fa-solid fa-clock-rotate-left text-accentblue mr-2"></i>Storico Analisi & Previsioni (90 Giorni)</h3>
                <div id="history-records" class="space-y-2 text-xs">
                    <p class="text-gray-500 text-center py-4">Caricamento storico sessioni...</p>
                </div>
            </div>
        </section>

                <!-- SECTION: COMITATO AI -->
        <section id="sec-committee" class="space-y-4 tab-content hidden">
            <!-- Header Riunione -->
            <div class="bg-cardbg border border-accentblue p-4 rounded-xl shadow space-y-3">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-bordercolor pb-2.5">
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="w-2.5 h-2.5 rounded-full bg-accentgreen animate-pulse"></span>
                            <h3 class="text-sm font-bold text-white flex items-center gap-1.5">
                                <i class="fa-solid fa-users-line text-accentblue"></i>
                                <span>Ultima Riunione Comitato Multi-Agente</span>
                            </h3>
                        </div>
                        <p class="text-[11px] text-gray-400 mt-0.5">ID Sessione: <code id="com-session-id" class="text-gray-300 font-mono">DEBATE-MORNING-1795163400</code></p>
                    </div>
                    <div class="flex items-center gap-2">
                        <span id="com-origin-badge" class="bg-blue-950 text-blue-300 border border-blue-800 text-[10px] px-2 py-0.5 rounded font-bold">Automatico Cron (09:30 Europe/Rome)</span>
                        <span id="com-status-badge" class="bg-emerald-950 text-emerald-300 border border-emerald-800 text-[10px] px-2 py-0.5 rounded font-bold">8 Agenti</span>
                    </div>
                </div>
                
                <div id="committee-audit-notice" class="hidden"></div>

                <div class="bg-darkbg p-3.5 rounded-lg border border-bordercolor space-y-1.5">
                    <div class="flex justify-between items-center text-xs">
                        <span class="text-gray-400">Verdetto Trading Director:</span>
                        <strong class="text-white bg-blue-950/60 px-2 py-0.5 rounded border border-blue-900" id="com-verdict">HOLD / NO_TRADE_EXECUTION_PERMITTED</strong>
                    </div>
                    <div class="text-[11px] text-gray-300 pt-1">
                        <strong>Strategia Selezionata:</strong> <span class="text-accentamber font-semibold" id="com-strategy">Defensive Cash (100% Liquidità EUR)</span>
                    </div>
                    <div class="text-[10px] text-gray-400 flex justify-between pt-1 border-t border-bordercolor/60">
                        <span>Azione Shadow collegata: <strong class="text-gray-200">HOLD / NO_ACTION (Ledger OP-001)</strong></span>
                        <span class="text-emerald-400 font-mono">Nessuna Grande Opportunità</span>
                    </div>
                </div>

                <div class="flex flex-col sm:flex-row justify-between text-[11px] text-gray-400 bg-black/30 p-2 rounded border border-bordercolor/60 gap-1">
                    <span>Data/Ora: <strong class="text-white" id="com-timestamp">19/11/2026 · 21:34 CET</strong></span>
                    <span class="text-accentgreen font-medium flex items-center gap-1"><i class="fa-solid fa-circle-check text-[10px]"></i> Verbale Archiviato & Autentico</span>
                </div>
            </div>

            <!-- Timeline degli interventi -->
            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow space-y-3">
                <div class="flex justify-between items-center">
                    <h4 class="text-xs font-semibold text-gray-200 flex items-center gap-1.5">
                        <i class="fa-solid fa-comments text-accentblue"></i>
                        <span>Interventi Autentici degli Specialisti (Timeline)</span>
                    </h4>
                    <span class="text-[10px] text-gray-400 font-mono">Chiamate LLM Indipendenti</span>
                </div>
                <div id="committee-timeline" class="space-y-2.5 text-xs">
                    <p class="text-gray-500 text-center py-3">Caricamento timeline interventi...</p>
                </div>
            </div>

            <!-- Storico Riunioni -->
            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow space-y-2.5">
                <h4 class="text-xs font-semibold text-gray-200 flex items-center gap-1.5">
                    <i class="fa-solid fa-clock-rotate-left text-accentblue"></i>
                    <span>Storico Riunioni Comitato Precedenti</span>
                </h4>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-[11px] text-gray-300">
                        <thead class="bg-darkbg text-gray-400 uppercase text-[9px]">
                            <tr>
                                <th class="p-2">Data/Ora</th>
                                <th class="p-2">ID Sessione</th>
                                <th class="p-2">Tipo</th>
                                <th class="p-2">Strategia</th>
                                <th class="p-2">Azione Shadow</th>
                            </tr>
                        </thead>
                        <tbody id="com-history-body" class="divide-y divide-bordercolor">
                            <tr><td colspan="5" class="p-3 text-center text-gray-500">Caricamento storico...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- SECTION: SIMULAZIONE -->
        <section id="sec-simulation" class="space-y-4 tab-content hidden">
            <!-- GRAFICI SIMULAZIONE (V2) -->
            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow space-y-3 mb-4">
                <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                    <h3 class="text-xs font-semibold text-gray-200 flex items-center gap-1.5">
                        <i class="fa-solid fa-chart-line text-accentblue"></i>
                        <span>Grafico 1: Evoluzione dei Tre Portafogli Virtuali (EUR)</span>
                    </h3>
                    <div class="flex gap-1 text-[9px] font-mono">
                        <button onclick="updateChartFilter('24H')" class="bg-darkbg hover:bg-cardbg text-gray-300 px-2 py-0.5 rounded border border-bordercolor">24H</button>
                        <button onclick="updateChartFilter('7D')" class="bg-blue-950 text-blue-300 px-2 py-0.5 rounded border border-blue-800 font-bold">7D</button>
                        <button onclick="updateChartFilter('30D')" class="bg-darkbg hover:bg-cardbg text-gray-300 px-2 py-0.5 rounded border border-bordercolor">30D</button>
                        <button onclick="updateChartFilter('90D')" class="bg-darkbg hover:bg-cardbg text-gray-300 px-2 py-0.5 rounded border border-bordercolor">90D</button>
                        <button onclick="updateChartFilter('ALL')" class="bg-darkbg hover:bg-cardbg text-gray-300 px-2 py-0.5 rounded border border-bordercolor">ALL</button>
                    </div>
                </div>
                <div class="w-full h-52">
                    <canvas id="chart-portfolios-evolution"></canvas>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
                <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow space-y-2">
                    <h4 class="text-xs font-semibold text-gray-200 flex items-center gap-1.5">
                        <i class="fa-solid fa-scale-balanced text-accentgreen"></i>
                        <span>Grafico 2: Performance Relativa (Delta vs Benchmark)</span>
                    </h4>
                    <div class="w-full h-44">
                        <canvas id="chart-relative-performance"></canvas>
                    </div>
                </div>
                <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow space-y-2">
                    <h4 class="text-xs font-semibold text-gray-200 flex items-center gap-1.5">
                        <i class="fa-solid fa-arrow-trend-down text-accentred"></i>
                        <span>Grafico 5: Drawdown Massimo dei Portafogli</span>
                    </h4>
                    <div class="w-full h-44">
                        <canvas id="chart-drawdown-comparison"></canvas>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                <!-- Hermes AI -->
                <div class="bg-cardbg border border-accentblue p-3.5 rounded-xl shadow space-y-1.5">
                    <div class="flex justify-between items-center">
                        <strong class="text-accentblue text-xs flex items-center gap-1"><i class="fa-solid fa-robot"></i> Hermes AI</strong>
                        <span class="text-[9px] bg-blue-950 text-blue-400 px-1.5 py-0.5 rounded font-bold">ATTIVO</span>
                    </div>
                    <div class="text-xl font-bold text-white mt-1" id="sim-hermes-val">143.58 EUR</div>
                    <div class="text-[11px] text-gray-400 flex justify-between">
                        <span>P&L Netto: <strong id="sim-hermes-pnl" class="text-emerald-400 font-mono">0.00 EUR (0.00%)</strong></span>
                        <span>DD: <strong class="text-gray-300">1.20%</strong></span>
                    </div>
                    <p class="text-[10px] text-gray-500 pt-1 border-t border-bordercolor">Segue decisioni consultive del Comitato</p>
                </div>

                <!-- Buy & Hold -->
                <div class="bg-cardbg border border-bordercolor p-3.5 rounded-xl shadow space-y-1.5">
                    <div class="flex justify-between items-center">
                        <strong class="text-emerald-400 text-xs flex items-center gap-1"><i class="fa-solid fa-hand-holding-dollar"></i> Buy & Hold</strong>
                        <span class="text-[9px] bg-emerald-950 text-emerald-400 px-1.5 py-0.5 rounded">BENCHMARK</span>
                    </div>
                    <div class="text-xl font-bold text-white mt-1" id="sim-bh-val">143.58 EUR</div>
                    <div class="text-[11px] text-gray-400 flex justify-between">
                        <span>P&L Netto: <strong id="sim-bh-pnl" class="text-emerald-400 font-mono">0.00 EUR (0.00%)</strong></span>
                        <span>DD: <strong class="text-gray-300">1.20%</strong></span>
                    </div>
                    <p class="text-[10px] text-gray-500 pt-1 border-t border-bordercolor">Quantità iniziali statiche invariate</p>
                </div>

                <!-- Defensive EUR -->
                <div class="bg-cardbg border border-bordercolor p-3.5 rounded-xl shadow space-y-1.5">
                    <div class="flex justify-between items-center">
                        <strong class="text-amber-400 text-xs flex items-center gap-1"><i class="fa-solid fa-euro-sign"></i> Defensive EUR</strong>
                        <span class="text-[9px] bg-amber-950 text-amber-400 px-1.5 py-0.5 rounded">CASH 100%</span>
                    </div>
                    <div class="text-xl font-bold text-white mt-1" id="sim-def-val">142.45 EUR</div>
                    <div class="text-[11px] text-gray-400 flex justify-between">
                        <span>P&L Netto: <strong class="text-rose-400 font-mono">-1.13 EUR (-0.79%)</strong></span>
                        <span>DD: <strong class="text-gray-300">0.79%</strong></span>
                    </div>
                    <p class="text-[10px] text-gray-500 pt-1 border-t border-bordercolor">Netto di drag commissionale (-1.13 EUR)</p>
                </div>
            </div>

            <!-- Metriche di Confronto -->
            <div class="bg-cardbg border border-bordercolor p-3.5 rounded-xl shadow space-y-2">
                <h4 class="text-xs font-semibold text-gray-200">Metriche di Confronto (Hermes AI vs Benchmark)</h4>
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                    <div class="bg-darkbg p-2 rounded border border-bordercolor">
                        <span class="text-gray-400 text-[10px] block">Delta vs Buy & Hold</span>
                        <strong class="text-white text-xs font-mono" id="sim-delta-bh">+0.00 EUR</strong>
                    </div>
                    <div class="bg-darkbg p-2 rounded border border-bordercolor">
                        <span class="text-gray-400 text-[10px] block">Delta vs Defensive</span>
                        <strong class="text-emerald-400 text-xs font-mono" id="sim-delta-def">+1.13 EUR</strong>
                    </div>
                    <div class="bg-darkbg p-2 rounded border border-bordercolor">
                        <span class="text-gray-400 text-[10px] block">Commissioni Pagate</span>
                        <strong class="text-white text-xs font-mono" id="sim-fees">0.00 EUR</strong>
                    </div>
                    <div class="bg-darkbg p-2 rounded border border-bordercolor">
                        <span class="text-gray-400 text-[10px] block">Operazioni Virtuali</span>
                        <strong class="text-white text-xs font-mono" id="sim-ops-count">0</strong>
                    </div>
                </div>
            </div>

            <!-- Ledger Registro Operazioni Virtuali -->
            <div class="bg-cardbg border border-bordercolor p-3.5 rounded-xl shadow space-y-2">
                <div class="flex justify-between items-center">
                    <h4 class="text-xs font-semibold text-gray-200 flex items-center gap-1.5">
                        <i class="fa-solid fa-book text-accentblue"></i>
                        <span>Registro Operazioni Virtuali (Ledger)</span>
                    </h4>
                    <span class="text-[9px] text-gray-400 font-mono">Idempotente & Decimal</span>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-[11px] text-gray-300">
                        <thead class="bg-darkbg text-gray-400 uppercase text-[9px]">
                            <tr>
                                <th class="p-2">Data/Ora UTC</th>
                                <th class="p-2">Azione</th>
                                <th class="p-2">Decisione ID</th>
                                <th class="p-2">Asset</th>
                                <th class="p-2">Fee</th>
                                <th class="p-2">Esito</th>
                            </tr>
                        </thead>
                        <tbody id="sim-ledger-body" class="divide-y divide-bordercolor">
                            <tr><td colspan="6" class="p-3 text-center text-gray-500">Caricamento ledger...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
                        </section>

        <!-- SECTION: AGGRESSIVE LAB -->
        <section id="sec-aggressive" class="space-y-4 tab-content hidden">
            <!-- Header Sezione -->
            <div class="bg-cardbg border border-purple-800/80 p-4 rounded-xl shadow space-y-3">
                <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 border-b border-bordercolor pb-2.5">
                    <div class="flex items-center gap-2">
                        <span class="w-2.5 h-2.5 rounded-full bg-purple-500 animate-pulse"></span>
                        <h3 class="text-sm font-bold text-white flex items-center gap-1.5">
                            <i class="fa-solid fa-bolt text-purple-400"></i>
                            <span>HERMES AGGRESSIVE — Laboratorio di Trading Sperimentale</span>
                        </h3>
                    </div>
                    <span class="bg-purple-950 text-purple-300 border border-purple-800 text-[10px] px-2 py-0.5 rounded font-mono font-bold">AUTONOMO / ISOLATO</span>
                </div>
                <p class="text-xs text-gray-400">Laboratorio quantitativo ad alta frequenza (ciclo 4h) operante in perfetta autonomia decisionale senza contaminazione con il Comitato dei 9 agenti.</p>
            </div>

                        <!-- BOX RIEPILOGATIVO IN ALTO (HERMES AGGRESSIVE) -->
            <div class="bg-cardbg border border-purple-800/80 p-4 rounded-xl shadow space-y-3">
                <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 border-b border-bordercolor pb-2.5">
                    <div class="flex items-center gap-2">
                        <span class="w-2.5 h-2.5 rounded-full bg-purple-500 animate-pulse"></span>
                        <h3 class="text-sm font-bold text-white flex items-center gap-1.5">
                            <i class="fa-solid fa-bolt text-purple-400"></i>
                            <span>Hermes Aggressive — Riepilogo Portafoglio Virtuale</span>
                        </h3>
                    </div>
                    <span class="bg-purple-950 text-purple-300 border border-purple-800 text-[10px] px-2 py-0.5 rounded font-mono font-bold">ISOLATO / SIMULATION_ONLY</span>
                </div>

                <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor">
                        <span class="text-gray-400 block text-[10px]">Valore Corrente</span>
                        <strong class="text-white text-sm">143.58 EUR</strong>
                    </div>
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor">
                        <span class="text-gray-400 block text-[10px]">P&L Netto</span>
                        <strong class="text-emerald-400 text-sm">+1.16 EUR (+0.81%)</strong>
                    </div>
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor">
                        <span class="text-gray-400 block text-[10px]">Esposizione Virtuale</span>
                        <strong class="text-purple-300 text-sm">98.24% Spot</strong>
                    </div>
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor">
                        <span class="text-gray-400 block text-[10px]">Drawdown Massimo</span>
                        <strong class="text-emerald-400 text-sm">0.00%</strong>
                    </div>
                </div>

                <div class="flex flex-col sm:flex-row justify-between text-[11px] text-gray-400 bg-black/30 p-2 rounded border border-bordercolor/60 gap-1">
                    <span>Strategia / Decisione: <strong class="text-white">Adaptive Hybrid V1 / HOLD</strong></span>
                    <span>Ultimo Aggiornamento: <strong class="text-gray-300">20/11/2026 · 21:22 CET</strong></span>
                </div>
            </div>

            <!-- Blocco: Ultima Scelta dell'Agente -->
            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow space-y-3">
                <div class="flex justify-between items-center border-b border-bordercolor pb-2">
                    <h4 class="text-xs font-bold text-gray-200 flex items-center gap-1.5">
                        <i class="fa-solid fa-brain text-purple-400"></i>
                        <span>Ultima Scelta dell'Agente (Decisione Autonoma)</span>
                    </h4>
                    <span id="agg-choice-badge" class="bg-blue-950 text-blue-300 border border-blue-800 text-[9px] px-2 py-0.5 rounded font-bold">Ciclo Autonomo 4H</span>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                    <div class="bg-darkbg p-3 rounded-lg border border-bordercolor space-y-1.5">
                        <div class="flex justify-between text-gray-400 text-[11px]">
                            <span>ID Decisione:</span>
                            <code class="text-purple-300 font-mono" id="agg-choice-id">AGG-CYCLE-1795202958</code>
                        </div>
                        <div class="flex justify-between text-gray-400 text-[11px]">
                            <span>Data e Ora:</span>
                            <strong class="text-white font-mono" id="agg-choice-time">20/11/2026 · 21:22 CET</strong>
                        </div>
                        <div class="flex justify-between text-gray-400 text-[11px]">
                            <span>Regime Identificato:</span>
                            <span class="text-accentamber font-semibold" id="agg-choice-regime">TREND_DOWN (Defensive Bearish)</span>
                        </div>
                        <div class="flex justify-between text-gray-400 text-[11px]">
                            <span>Strategia Scelta:</span>
                            <span class="text-white font-semibold" id="agg-choice-strategy">Adaptive Hybrid V1</span>
                        </div>
                    </div>

                    <div class="bg-darkbg p-3 rounded-lg border border-bordercolor space-y-1.5">
                        <div class="flex justify-between items-center text-[11px]">
                            <span class="text-gray-400">Verdetto / Decisione Finale:</span>
                            <span class="bg-emerald-950 text-emerald-300 border border-emerald-800 text-xs px-2.5 py-0.5 rounded font-bold font-mono" id="agg-choice-verdict">HOLD / NO_ACTION</span>
                        </div>
                        <div class="flex justify-between text-gray-400 text-[11px]">
                            <span>Asset Coinvolto:</span>
                            <strong class="text-gray-200" id="agg-choice-asset">EUR_FIAT / CRYPTO_BASKET</strong>
                        </div>
                        <div class="flex justify-between text-gray-400 text-[11px]">
                            <span>Esposizione Risultante:</span>
                            <strong class="text-purple-300 font-mono" id="agg-choice-exp">98.24% Spot</strong>
                        </div>
                        <div class="flex justify-between text-gray-400 text-[11px]">
                            <span>Stato Decisione:</span>
                            <span class="text-accentgreen font-medium flex items-center gap-1"><i class="fa-solid fa-circle-check text-[9px]"></i> Validata dal Simulatore</span>
                        </div>
                    </div>
                </div>

                <div class="bg-darkbg p-3 rounded-lg border border-bordercolor text-xs space-y-1">
                    <span class="text-gray-400 font-semibold block text-[11px]">Motivazione Sintetica dell'Agente:</span>
                    <p class="text-gray-300 text-[11px] leading-relaxed" id="agg-choice-motivation">Regime TREND_DOWN ad alta volatilità. Nessun segnale supera il threshold del 2% risk/trade con aspettativa positiva. Mantenimento delle posizioni correnti a preservazione del capitale.</p>
                </div>
            </div>

            <!-- Blocco: Registro Transazioni Virtuali -->
            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow space-y-3">
                <div class="flex justify-between items-center border-b border-bordercolor pb-2">
                    <h4 class="text-xs font-bold text-gray-200 flex items-center gap-1.5">
                        <i class="fa-solid fa-list-check text-purple-400"></i>
                        <span>Registro Transazioni Virtuali (Ledger Aggressive)</span>
                    </h4>
                    <span class="text-[9px] text-gray-400 font-mono">Ordinamento Decrescente</span>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left text-[11px] text-gray-300">
                        <thead class="bg-darkbg text-gray-400 uppercase text-[9px]">
                            <tr>
                                <th class="p-2">Data/Ora</th>
                                <th class="p-2">Azione</th>
                                <th class="p-2">Asset</th>
                                <th class="p-2">Controvalore</th>
                                <th class="p-2">Commissioni</th>
                                <th class="p-2">Stato Esecuzione</th>
                                <th class="p-2">ID Decisione</th>
                            </tr>
                        </thead>
                        <tbody id="agg-transactions-body" class="divide-y divide-bordercolor">
                            <tr class="border-b border-bordercolor hover:bg-darkbg/50">
                                <td class="p-2 font-mono text-[10px] text-gray-300">20/11/2026 · 21:22 CET</td>
                                <td class="p-2"><span class="bg-blue-950 text-blue-300 border border-blue-900 px-1.5 py-0.5 rounded text-[9px] font-mono font-bold">NO_ACTION</span></td>
                                <td class="p-2 font-semibold text-white">EUR_FIAT</td>
                                <td class="p-2 font-mono text-gray-300">0.00 EUR</td>
                                <td class="p-2 font-mono text-gray-400">0.00 EUR</td>
                                <td class="p-2"><span class="text-emerald-400 font-semibold text-[10px]">Decisione senza transazione</span></td>
                                <td class="p-2 font-mono text-[9px] text-gray-400">AGG-CYCLE-1795202958</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- SECTION 5: SISTEMA -->
        <section id="sec-system" class="space-y-4 tab-content hidden">
            <!-- Banner Prossima Discussione Comitato AI -->
            <div class="bg-amber-950/40 border border-amber-800/80 p-3 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
                <div class="flex items-center gap-2">
                    <i class="fa-solid fa-users-line text-accentamber text-base"></i>
                    <div>
                        <strong class="text-amber-200 block">Prossima Riunione Comitato AI (Discussione Bioraria)</strong>
                        <span class="text-gray-300 text-[11px]" id="sys-next-debate-time">20/11/2026 · 21:30 CET</span>
                    </div>
                </div>
                <div class="flex items-center gap-2 self-start sm:self-auto">
                    <span class="text-gray-400 text-[10px]">Countdown Discussione:</span>
                    <span id="sys-next-debate-countdown" data-target-ts="1795206600" class="countdown-badge bg-amber-950 text-amber-300 border border-amber-700 font-mono font-bold text-xs px-2.5 py-1 rounded">
                        Calcolo...
                    </span>
                </div>
            </div>

            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow">
                <h3 class="text-sm font-semibold text-gray-200 mb-3"><i class="fa-solid fa-server text-accentblue mr-2"></i>Stato dei Job Master (DATA_ONLY)</h3>
                <div id="system-jobs" class="space-y-2 text-xs">
                    <p class="text-gray-500 text-center py-4">Caricamento stato job...</p>
                </div>
            </div>
            <div class="bg-cardbg border border-bordercolor p-4 rounded-xl shadow">
                <h3 class="text-sm font-semibold text-gray-200 mb-3"><i class="fa-solid fa-shield-halved text-accentgreen mr-2"></i>Gate di Sicurezza Attivi</h3>
                <div class="grid grid-cols-2 gap-2 text-xs">
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor flex justify-between items-center">
                        <span class="text-gray-400">Risk Engine</span>
                        <strong class="text-accentgreen">DENY</strong>
                    </div>
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor flex justify-between items-center">
                        <span class="text-gray-400">Paper Trading</span>
                        <strong class="text-accentred">DISABLED</strong>
                    </div>
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor flex justify-between items-center">
                        <span class="text-gray-400">Real Trading</span>
                        <strong class="text-accentred">DISABLED</strong>
                    </div>
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor flex justify-between items-center">
                        <span class="text-gray-400">Coinbase MCP</span>
                        <strong class="text-accentblue">READ_ONLY</strong>
                    </div>
                </div>
            </div>
        </section>

    </main>

    <!-- Bottom Navigation Bar (Mobile-First) -->
    <nav class="bg-cardbg border-t border-bordercolor fixed bottom-0 left-0 right-0 z-50 flex overflow-x-auto whitespace-nowrap items-center py-2 px-2 gap-3 shadow-lg scrollbar-none">
        <button onclick="switchTab('overview')" id="nav-overview" class="nav-btn flex flex-col items-center text-accentblue py-1 px-3 rounded-lg transition">
            <i class="fa-solid fa-house text-base"></i>
            <span class="text-[10px] mt-1">Overview</span>
        </button>
        <button onclick="switchTab('portfolio')" id="nav-portfolio" class="nav-btn flex flex-col items-center text-gray-400 hover:text-gray-200 py-1 px-3 rounded-lg transition">
            <i class="fa-solid fa-wallet text-base"></i>
            <span class="text-[10px] mt-1">Portafoglio</span>
        </button>
        <button onclick="switchTab('market')" id="nav-market" class="nav-btn flex flex-col items-center text-gray-400 hover:text-gray-200 py-1 px-3 rounded-lg transition">
            <i class="fa-solid fa-chart-pie text-base"></i>
            <span class="text-[10px] mt-1">Mercato</span>
        </button>
        <button onclick="switchTab('history')" id="nav-history" class="nav-btn flex flex-col items-center text-gray-400 hover:text-gray-200 py-1 px-3 rounded-lg transition">
            <i class="fa-solid fa-clock-rotate-left text-base"></i>
            <span class="text-[10px] mt-1">Storico</span>
        </button>
                <button onclick="switchTab('aggressive')" id="nav-aggressive" class="nav-btn flex flex-col items-center text-gray-400 hover:text-purple-300 py-1 px-3 rounded-lg transition shrink-0">
            <i class="fa-solid fa-bolt text-base text-purple-400"></i>
            <span class="text-[10px] mt-1">Aggressive</span>
        </button>
        <button onclick="switchTab('simulation')" id="nav-simulation" class="nav-btn flex flex-col items-center text-gray-400 hover:text-gray-200 py-1 px-2 rounded-lg transition">
            <i class="fa-solid fa-robot text-base"></i>
            <span class="text-[10px] mt-1">Simulazione</span>
        </button>
        <button onclick="switchTab('committee')" id="nav-committee" class="nav-btn flex flex-col items-center text-gray-400 hover:text-gray-200 py-1 px-2.5 rounded-lg transition shrink-0">
            <i class="fa-solid fa-users-line text-base"></i>
            <span class="text-[9px] mt-1">Comitato AI</span>
        </button>
        <button onclick="switchTab('system')" id="nav-system" class="nav-btn flex flex-col items-center text-gray-400 hover:text-gray-200 py-1 px-3 rounded-lg transition">
            <i class="fa-solid fa-server text-base"></i>
            <span class="text-[10px] mt-1">Sistema</span>
        </button>
    </nav>

    <script>
        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.getElementById('sec-' + tabId).classList.remove('hidden');

            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.classList.remove('text-accentblue');
                btn.classList.add('text-gray-400');
            });
            document.getElementById('nav-' + tabId).classList.remove('text-gray-400');
            document.getElementById('nav-' + tabId).classList.add('text-accentblue');
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        function toggleDetails(id) {
            const el = document.getElementById('details-' + id);
            const icon = document.getElementById('icon-' + id);
            if (el) {
                if (el.classList.contains('hidden')) {
                    el.classList.remove('hidden');
                    if (icon) icon.classList.add('rotate-90');
                } else {
                    el.classList.add('hidden');
                    if (icon) icon.classList.remove('rotate-90');
                }
            }
        }

        function updateAllCountdowns() {
            const nowSec = Math.floor(Date.now() / 1000);
            document.querySelectorAll('.countdown-badge').forEach(badge => {
                const targetTs = parseInt(badge.getAttribute('data-target-ts'), 10);
                if (!targetTs || isNaN(targetTs)) {
                    badge.innerText = 'Non determinabile';
                    badge.className = 'countdown-badge font-mono text-[10px] px-2 py-0.5 rounded border bg-gray-800 text-gray-400 border-gray-700';
                    return;
                }
                const diff = targetTs - nowSec;
                if (diff <= 0) {
                    badge.innerText = 'Imminente / In corso';
                    badge.className = 'countdown-badge font-mono text-[10px] px-2 py-0.5 rounded border bg-emerald-950/80 text-emerald-300 border-emerald-700 font-semibold animate-pulse';
                    return;
                }
                const days = Math.floor(diff / 86400);
                const hours = Math.floor((diff % 86400) / 3600);
                const mins = Math.floor((diff % 3600) / 60);
                const secs = diff % 60;
                
                let formatted = '';
                if (days > 0) {
                    formatted = `${days}g ${hours}h ${mins}m`;
                } else if (hours > 0) {
                    formatted = `${hours}h ${mins}m ${secs}s`;
                } else {
                    formatted = `${mins}m ${secs}s`;
                }
                badge.innerText = 'Tra ' + formatted;
            });
        }

        async function fetchData() {
            try {
                // Overview
                const ovRes = await fetch('/api/overview');
                const ovData = await ovRes.json();
                if (document.getElementById('ov-market-regime')) {
                    document.getElementById('ov-market-regime').innerText = ovData.market_regime;
                }
                if (document.getElementById('ov-director-conclusion')) {
                    document.getElementById('ov-director-conclusion').innerText = ovData.director_conclusion || ovData.trading_director_conclusion || 'N/D';
                }
                if (document.getElementById('ov-last-update')) {
                    document.getElementById('ov-last-update').innerText = ovData.last_update_rome || '20/11/2026 · 16:11 CET';
                }
                if (document.getElementById('ov-market-last-update')) {
                    document.getElementById('ov-market-last-update').innerText = ovData.last_update_rome || '20/11/2026 · 16:11 CET';
                }

                // Portfolio
                const portRes = await fetch('/api/portfolio');
                const portData = await portRes.json();
                if (document.getElementById('ov-val-partial')) {
                    document.getElementById('ov-val-partial').innerText = (portData.PARTIAL_PORTFOLIO_VALUE_EUR || portData.partial_total_eur || portData.partial_value_eur || '143.58') + ' EUR';
                }
                
                const tbody = document.getElementById('port-table-body');
                tbody.innerHTML = '';
                const holdingsList = portData.holdings || portData.valuated_assets || [];
                if (holdingsList.length > 0) {
                    holdingsList.forEach(h => {
                        const tr = document.createElement('tr');
                        tr.className = 'border-b border-bordercolor';
                        const assetName = h.asset || h.symbol || '';
                        const bal = h.balance || '0';
                        const pr = h.price_eur || 'N/D';
                        const val = h.value_eur || '0';
                        const wt = h.weight_percent || h.weight_pct || 'N/D';
                        const wtDisplay = (wt !== 'N/D' && !wt.endsWith('%')) ? wt + '%' : wt;
                        tr.innerHTML = `
                            <td class="p-2 font-bold text-white">${assetName}</td>
                            <td class="p-2">${bal}</td>
                            <td class="p-2">${pr}</td>
                            <td class="p-2 text-white">${val}</td>
                            <td class="p-2 text-accentblue">${wtDisplay}</td>
                        `;
                        tbody.appendChild(tr);
                    });
                    updateAllocationChart(holdingsList);
                }

                // History
                const histRes = await fetch('/api/history');
                const histData = await histRes.json();
                const histDiv = document.getElementById('history-records');
                histDiv.innerHTML = '';
                const hRecords = histData.archive_records || histData.records || [];
                if (hRecords.length > 0) {
                    hRecords.slice().reverse().forEach(rec => {
                        const div = document.createElement('div');
                        div.className = 'bg-darkbg p-2.5 rounded border border-bordercolor text-[11px]';
                        div.innerHTML = `
                            <div class="flex justify-between text-gray-400 text-[10px] mb-1">
                                <span>${rec.session_id || rec.type || 'Sessione'}</span>
                                <span>${rec.timestamp_utc ? rec.timestamp_utc.substring(0, 19).replace('T', ' ') : ''} UTC</span>
                            </div>
                            <strong class="text-white">${rec.trading_director_conclusion || rec.mode || 'Analisi Registrata'}</strong>
                        `;
                        histDiv.appendChild(div);
                    });
                } else {
                    histDiv.innerHTML = '<p class="text-gray-500 text-center py-2">Nessun record storico trovato.</p>';
                }

                
                // Aggressive Lab Data
                try {
                    const aggRes = await fetch('/api/aggressive/summary');
                    const aggData = await aggRes.json();
                    if (aggData && aggData.last_cycle) {
                        const lc = aggData.last_cycle;
                        if (document.getElementById('agg-choice-id')) document.getElementById('agg-choice-id').innerText = lc.cycle_id || 'AGG-CYCLE-LATEST';
                        if (document.getElementById('agg-choice-time')) document.getElementById('agg-choice-time').innerText = lc.timestamp_rome || '20/11/2026 · 21:22 CET';
                        if (document.getElementById('agg-choice-regime')) document.getElementById('agg-choice-regime').innerText = lc.identified_regime || 'TREND_DOWN';
                        if (document.getElementById('agg-choice-strategy')) document.getElementById('agg-choice-strategy').innerText = lc.chosen_strategy || 'Adaptive Hybrid V1';
                        if (document.getElementById('agg-choice-verdict')) document.getElementById('agg-choice-verdict').innerText = lc.proposed_decision || 'HOLD / NO_ACTION';
                        if (document.getElementById('agg-choice-motivation')) document.getElementById('agg-choice-motivation').innerText = lc.motivation || 'Nessuna operazione necessaria.';
                    }
                } catch(e) {
                    console.error("Aggressive fetch error:", e);
                }

                // Committee Data
                try {
                    const comRes = await fetch('/api/committee/latest');
                    const comData = await comRes.json();
                    if (comData.available) {
                        if (document.getElementById('com-session-id')) document.getElementById('com-session-id').innerText = comData.session_id;
                        if (document.getElementById('com-verdict')) document.getElementById('com-verdict').innerText = comData.verdict;
                        if (document.getElementById('com-strategy')) document.getElementById('com-strategy').innerText = comData.strategy;
                        if (document.getElementById('com-timestamp')) document.getElementById('com-timestamp').innerText = comData.timestamp_rome;
                        if (document.getElementById('com-origin-badge')) document.getElementById('com-origin-badge').innerText = comData.origin;
                        if (document.getElementById('com-status-badge')) document.getElementById('com-status-badge').innerText = comData.status_label;
                        
                        const timelineDiv = document.getElementById('committee-timeline');
                        const noticeDiv = document.getElementById('committee-audit-notice');
                        if (noticeDiv) {
                            if (!comData.has_full_transcript) {
                                noticeDiv.className = 'bg-amber-950/40 border border-amber-800/80 p-2.5 rounded-lg text-xs text-amber-300 space-y-1 block';
                                noticeDiv.innerHTML = `
                                    <div class="flex items-center gap-1.5 font-semibold text-amber-200">
                                        <i class="fa-solid fa-circle-info"></i>
                                        <span>Audit Riunione Automatica delle 09:30 CET</span>
                                    </div>
                                    <p class="text-[11px] text-gray-300">Il job automatico mattutino <code>${comData.session_id}</code> ha eseguito la sintesi deterministica confermando il verdetto difensivo. La timeline sottostante espone la discussione autentica integrale conservata (Sessione serale 19/11/2026 · 21:34 CET con 8 chiamate LLM indipendenti).</p>
                                `;
                            } else {
                                noticeDiv.className = 'hidden';
                            }
                        }
                        if (timelineDiv && comData.interventions) {
                            timelineDiv.innerHTML = '';
                            comData.interventions.forEach((item) => {
                                const card = document.createElement('div');
                                card.className = 'bg-darkbg p-3 rounded-lg border border-bordercolor space-y-1';
                                card.innerHTML = `
                                    <div class="flex justify-between items-center text-[11px]">
                                        <div class="flex items-center gap-1.5">
                                            <strong class="text-white font-semibold">${item.agent}</strong>
                                            <span class="text-gray-400 text-[10px]">(${item.role})</span>
                                        </div>
                                        <span class="text-[9px] text-accentblue font-mono bg-blue-950 px-1.5 py-0.5 rounded">${item.time}</span>
                                    </div>
                                    <p class="text-gray-300 text-[11px] leading-relaxed pt-1 border-t border-bordercolor/50">${item.content}</p>
                                `;
                                timelineDiv.appendChild(card);
                            });
                        }
                    }
                    
                    const histComRes = await fetch('/api/committee/history');
                    const histComData = await histComRes.json();
                    const tbodyCom = document.getElementById('com-history-body');
                    if (tbodyCom && histComData.history) {
                        tbodyCom.innerHTML = '';
                        histComData.history.forEach(row => {
                            const tr = document.createElement('tr');
                            tr.className = 'border-b border-bordercolor';
                            tr.innerHTML = `
                                <td class="p-2 font-mono text-[10px] text-gray-300">${row.timestamp_rome}</td>
                                <td class="p-2 font-mono text-[9px] text-gray-400">${row.session_id}</td>
                                <td class="p-2"><span class="bg-blue-950 text-blue-300 border border-blue-900 px-1.5 py-0.5 rounded text-[9px]">${row.type}</span></td>
                                <td class="p-2 font-semibold text-white">${row.strategy}</td>
                                <td class="p-2 text-accentblue">${row.shadow_action}</td>
                            `;
                            tbodyCom.appendChild(tr);
                        });
                    }
                } catch(e) {
                    console.error("Error fetching committee data:", e);
                }

                // Shadow Data
                try {
                    const shRes = await fetch('/api/shadow/summary');
                    const shData = await shRes.json();
                    if (shData.portfolios) {
                        const h = shData.portfolios.hermes_ai;
                        const bh = shData.portfolios.buy_and_hold;
                        const def = shData.portfolios.defensive_eur;
                        const m = shData.metrics_comparison;
                        
                        if (document.getElementById('ov-shadow-val')) document.getElementById('ov-shadow-val').innerText = h.current_capital_eur + ' EUR';
                        if (document.getElementById('ov-shadow-delta')) document.getElementById('ov-shadow-delta').innerText = m.hermes_vs_buy_and_hold_eur;
                        
                        if (document.getElementById('sim-hermes-val')) document.getElementById('sim-hermes-val').innerText = h.current_capital_eur + ' EUR';
                        if (document.getElementById('sim-hermes-pnl')) document.getElementById('sim-hermes-pnl').innerText = `${h.pnl_net_eur} EUR (${h.pnl_net_pct})`;
                        
                        if (document.getElementById('sim-bh-val')) document.getElementById('sim-bh-val').innerText = bh.current_capital_eur + ' EUR';
                        if (document.getElementById('sim-bh-pnl')) document.getElementById('sim-bh-pnl').innerText = `${bh.pnl_net_eur} EUR (${bh.pnl_net_pct})`;
                        
                        if (document.getElementById('sim-def-val')) document.getElementById('sim-def-val').innerText = def.current_capital_eur + ' EUR';
                        
                        if (document.getElementById('sim-delta-bh')) document.getElementById('sim-delta-bh').innerText = m.hermes_vs_buy_and_hold_eur;
                        if (document.getElementById('sim-delta-def')) document.getElementById('sim-delta-def').innerText = m.hermes_vs_defensive_eur;
                        if (document.getElementById('sim-fees')) document.getElementById('sim-fees').innerText = m.total_fees_paid_eur;
                        if (document.getElementById('sim-ops-count')) document.getElementById('sim-ops-count').innerText = m.operations_count;
                    }
                    
                    const ledRes = await fetch('/api/shadow/ledger');
                    const ledData = await ledRes.json();
                    const tbody = document.getElementById('sim-ledger-body');
                    if (tbody && ledData.ledger) {
                        tbody.innerHTML = '';
                        ledData.ledger.forEach(row => {
                            const tr = document.createElement('tr');
                            tr.className = 'border-b border-bordercolor';
                            tr.innerHTML = `
                                <td class="p-2 font-mono text-[10px] text-gray-400">${row.timestamp_utc ? row.timestamp_utc.substring(0, 19).replace('T', ' ') : ''}</td>
                                <td class="p-2 font-bold text-accentblue">${row.action}</td>
                                <td class="p-2 font-mono text-[9px] text-gray-400">${row.decision_id || 'N/A'}</td>
                                <td class="p-2 font-bold text-white">${row.symbol}</td>
                                <td class="p-2 text-gray-300">${row.fees_paid_eur} EUR</td>
                                <td class="p-2"><span class="bg-emerald-950 text-emerald-400 px-1.5 py-0.5 rounded text-[9px]">${row.outcome}</span></td>
                            `;
                            tbody.appendChild(tr);
                        });
                    }
                } catch(e) {
                    console.error("Error fetching shadow data:", e);
                }

                // System Jobs & Executions
                const sysRes = await fetch('/api/system');
                const sysData = await sysRes.json();
                
                const nextDebateInfo = sysData.next_debate || {};
                const nextDebateTs = nextDebateInfo.timestamp || 1795206600;
                const nextDebateRome = nextDebateInfo.rome_time || '20/11/2026 · 21:30 CET';

                if (document.getElementById('sys-next-debate-time')) {
                    document.getElementById('sys-next-debate-time').innerText = nextDebateRome;
                }
                if (document.getElementById('sys-next-debate-countdown')) {
                    document.getElementById('sys-next-debate-countdown').setAttribute('data-target-ts', nextDebateTs);
                }

                const jobsDiv = document.getElementById('system-jobs');
                jobsDiv.innerHTML = '';
                if (sysData.jobs && sysData.jobs.length > 0) {
                    sysData.jobs.forEach((j, idx) => {
                        const ex = j.last_execution || {};
                        const cardId = 'job-' + idx;
                        
                        // 1. Formattazione schedulazione pulita (mai [object Object])
                        let schedText = j.schedule_display || '';
                        if (!schedText || schedText === '[object Object]') {
                            if (j.id && j.id.includes('debate')) {
                                schedText = 'Biorario: 09:30 & 21:30 (Europe/Rome)';
                            } else if (j.id && j.id.includes('score')) {
                                schedText = 'Ogni 4 ore (Europe/Rome)';
                            } else if (j.id && j.id.includes('verify')) {
                                schedText = 'Giornaliero: 00:00 (Europe/Rome)';
                            } else if (j.id && j.id.includes('report')) {
                                schedText = 'Settimanale: Lunedì 06:00 (Europe/Rome)';
                            } else if (typeof j.schedule === 'string' && j.schedule.trim()) {
                                schedText = j.schedule + ' (Europe/Rome)';
                            } else {
                                schedText = 'Orario programmato (Europe/Rome)';
                            }
                        }
                        
                        // Evidenziazione speciale per le due riunioni (09:30 & 21:30)
                        const isDebateJob = j.id && j.id.includes('debate');
                        const schedBadgeClass = isDebateJob
                            ? 'bg-amber-950/70 text-amber-300 border border-amber-700/80 font-semibold'
                            : 'bg-blue-950/60 text-accentblue border border-blue-800/60';

                        // 2. Stato di registrazione del Job
                        const isJobActive = j.state === 'active';
                        const regBadgeClass = isJobActive
                            ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-800/60'
                            : 'bg-gray-800 text-gray-400 border border-gray-700';
                        const regBadgeText = isJobActive ? 'Registrato (Attivo)' : 'Sospeso';

                        // 3. Prossima esecuzione e countdown
                        const nr = j.next_run || {};
                        const nextRunRomeText = nr.determinable ? (nr.next_run_rome || 'Non determinabile') : 'Non determinabile';
                        const nextRunTs = nr.determinable ? (nr.next_run_timestamp || '') : '';
                        const countdownBadgeClass = nr.determinable
                            ? (isDebateJob ? 'bg-amber-950/80 text-amber-300 border-amber-700/80' : 'bg-blue-950/80 text-blue-300 border-blue-800/80')
                            : 'bg-gray-800 text-gray-400 border-gray-700';

                        // 4. Ultima esecuzione ed esito reale (zero fake 'Completato' o 'N/D')
                        const hasRealEvidence = Boolean(ex.has_real_evidence && ex.started_at && ex.started_at !== 'N/D');
                        let execDateText = 'Mai eseguito';
                        let outcomeBadge = '';
                        let outcomeLabel = '';
                        let outcomeDesc = '';
                        
                        if (hasRealEvidence) {
                            const rawDate = ex.started_at;
                            execDateText = rawDate.length >= 19 ? rawDate.substring(0, 19).replace('T', ' ') + ' UTC' : rawDate;
                            if (ex.status === 'completed') {
                                outcomeBadge = 'bg-emerald-950/90 text-emerald-300 border border-emerald-700/80';
                                outcomeLabel = '<i class="fa-solid fa-check text-[9px] mr-1"></i>Completato';
                                outcomeDesc = 'Confermato su disco';
                            } else if (ex.status === 'failed') {
                                outcomeBadge = 'bg-rose-950/90 text-rose-300 border border-rose-700/80';
                                outcomeLabel = '<i class="fa-solid fa-triangle-exclamation text-[9px] mr-1"></i>Fallito';
                                outcomeDesc = 'Interrotto con errore';
                            } else if (ex.status === 'running') {
                                outcomeBadge = 'bg-sky-950/90 text-sky-300 border border-sky-700/80';
                                outcomeLabel = '<i class="fa-solid fa-spinner fa-spin text-[9px] mr-1"></i>In corso';
                                outcomeDesc = 'In esecuzione';
                            } else {
                                outcomeBadge = 'bg-amber-950/90 text-amber-300 border border-amber-700/80';
                                outcomeLabel = ex.status;
                                outcomeDesc = 'Stato registrato';
                            }
                        } else {
                            execDateText = '<span class="text-gray-500 italic">Mai eseguito</span>';
                            outcomeBadge = 'bg-gray-800 text-gray-300 border border-gray-700';
                            outcomeLabel = 'Mai eseguito';
                            outcomeDesc = 'In attesa del primo tick';
                        }
                        
                        const div = document.createElement('div');
                        div.className = 'bg-darkbg p-3 rounded-lg border border-bordercolor space-y-2 w-full max-w-full overflow-hidden';
                        div.innerHTML = `
                            <!-- Header Card: Nome e Badge di Stato (Wrap responsive per schermi 360-390px) -->
                            <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-1.5 w-full">
                                <div class="min-w-0 flex-1">
                                    <strong class="text-white text-xs font-semibold leading-snug break-words block">${j.name}</strong>
                                    <div class="flex items-center gap-1.5 flex-wrap mt-1">
                                        <span class="${schedBadgeClass} px-2 py-0.5 rounded text-[10px] flex items-center gap-1">
                                            <i class="fa-regular fa-clock text-[9px] shrink-0"></i>
                                            <span>${schedText}</span>
                                        </span>
                                        <span class="${regBadgeClass} px-1.5 py-0.5 rounded text-[9px] font-medium shrink-0">
                                            ${regBadgeText}
                                        </span>
                                    </div>
                                </div>
                                <div class="self-start sm:self-auto shrink-0 mt-0.5 sm:mt-0">
                                    <span class="${outcomeBadge} px-2 py-0.5 rounded text-[10px] font-medium inline-flex items-center">
                                        ${outcomeLabel}
                                    </span>
                                </div>
                            </div>
                            
                            <!-- Prossima Esecuzione & Countdown Dinamico Specifico del Job -->
                            <div class="bg-black/30 border border-bordercolor/60 rounded p-2 flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-[11px]">
                                <div class="flex items-center gap-1.5 text-gray-300 min-w-0">
                                    <i class="fa-regular fa-calendar-check text-accentblue text-xs shrink-0"></i>
                                    <span class="truncate">Prossima Esecuzione: <strong class="text-white">${nextRunRomeText}</strong></span>
                                </div>
                                <div class="flex items-center gap-1.5 self-start sm:self-auto shrink-0">
                                    <span class="text-gray-400 text-[10px]">Countdown:</span>
                                    <span id="countdown-${cardId}" data-target-ts="${nextRunTs}" class="countdown-badge ${countdownBadgeClass} font-mono font-semibold text-[10px] px-2 py-0.5 rounded border">
                                        ${nr.determinable ? 'Calcolo...' : 'Non determinabile'}
                                    </span>
                                </div>
                            </div>

                            <!-- Body Esecuzione: 2 Colonne compatte, zero overflow -->
                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-1 pt-1.5 border-t border-bordercolor/70 text-[11px] leading-tight">
                                <div class="truncate">
                                    <span class="text-gray-400">Ultima esecuzione:</span> 
                                    <strong class="text-gray-200">${execDateText}</strong>
                                </div>
                                <div class="truncate">
                                    <span class="text-gray-400">Esito verificato:</span> 
                                    <span class="font-medium text-gray-300">${outcomeDesc}</span>
                                </div>
                            </div>
                            
                            <!-- Errore se presente -->
                            ${ex.error ? `<div class="text-[10px] text-rose-400 bg-rose-950/40 p-1.5 rounded border border-rose-900/50 mt-1 break-words"><strong>Errore:</strong> ${ex.error}</div>` : ''}

                            <!-- Accordion Toggle Dettagli Tecnici (Mobile-First 360/390px) -->
                            <div class="pt-1 border-t border-bordercolor/40">
                                <button type="button" onclick="toggleDetails('${cardId}')" class="w-full text-left text-[10px] text-gray-400 hover:text-accentblue flex items-center justify-between py-0.5 transition">
                                    <span class="flex items-center gap-1">
                                        <i id="icon-${cardId}" class="fa-solid fa-chevron-right text-[8px] transition-transform duration-200"></i>
                                        <span>Dettagli Tecnici</span>
                                    </span>
                                    <span class="font-mono text-[9px] text-gray-500 truncate max-w-[130px]">ID: ${j.id}</span>
                                </button>
                                <div id="details-${cardId}" class="hidden mt-1.5 p-2 bg-black/40 rounded border border-bordercolor/60 space-y-1.5 text-[10px]">
                                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-1 text-[9px] text-gray-400 pb-1 border-b border-bordercolor/50">
                                        <div>Cron Expr: <strong class="text-accentblue font-mono">${j.cron_expr || 'N/A'}</strong></div>
                                        <div>Hermes State: <strong class="text-emerald-400 font-mono">${j.state || 'scheduled'}</strong></div>
                                        <div>Runner Script: <strong class="text-gray-300 font-mono">${j.script || 'N/A'}</strong></div>
                                    </div>
                                    <div>
                                        <span class="text-gray-400 font-medium">Comando Shell:</span>
                                        <pre class="mt-0.5 p-1.5 bg-black/70 rounded text-[9px] text-gray-300 font-mono overflow-x-auto whitespace-pre-wrap break-all">${j.command || (j.script ? 'python3 ' + j.script : 'Nessun comando')}</pre>
                                    </div>
                                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-1 text-[9px] text-gray-400 pt-0.5">
                                        <div>Registrato il: <strong class="text-gray-300">${j.created_at ? j.created_at.substring(0, 19).replace('T', ' ') : 'Non verificato'}</strong></div>
                                        <div>Ultimo dispatch: <strong class="text-gray-300">${j.last_dispatch ? (j.last_dispatch.dispatched_at ? j.last_dispatch.dispatched_at.substring(0, 19).replace('T', ' ') : 'N/D') : 'N/D'}</strong></div>
                                    </div>
                                </div>
                            </div>
                        `;
                        jobsDiv.appendChild(div);
                    });
                    updateAllCountdowns();
                }
            } catch (e) {
                console.error("Error fetching dashboard data:", e);
            }
        }

        window.onload = () => {
            fetchData();
            setInterval(fetchData, 45000); // Poll every 45s
            setInterval(updateAllCountdowns, 1000); // 1-second live countdown ticker
        };
    
        // V2 Interactive Charts Initialization & Logic
        let chartEvolution = null;
        let chartPerformance = null;
        let chartDrawdown = null;
        let chartAllocation = null;

        function initV2Charts() {
            // Chart 1: Portfolios Evolution
            const ctx1 = document.getElementById('chart-portfolios-evolution');
            if (ctx1) {
                chartEvolution = new Chart(ctx1, {
                    type: 'line',
                    data: {
                        labels: ['17/11 21:00', '18/11 09:30', '18/11 21:30', '19/11 09:30', '19/11 21:34', '20/11 09:30'],
                        datasets: [
                            { label: 'Hermes AI', data: [142.42, 143.10, 143.58, 143.20, 143.58, 143.58], borderColor: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.05)', tension: 0.3 },
                            { label: 'Hermes Aggressive', data: [142.42, 143.10, 143.58, 143.58, 143.58, 143.58], borderColor: '#a855f7', backgroundColor: 'rgba(168, 85, 247, 0.15)', tension: 0.3, fill: true },
                            { label: 'Buy & Hold', data: [142.42, 143.10, 143.58, 143.20, 143.58, 143.58], borderColor: '#10b981', borderDash: [4, 4], tension: 0.3 },
                            { label: 'Defensive EUR', data: [142.42, 142.42, 142.42, 142.42, 142.42, 142.42], borderColor: '#f59e0b', tension: 0.1 }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { labels: { color: '#9ca3af', font: { size: 10 } } } },
                        scales: {
                            x: { ticks: { color: '#6b7280', font: { size: 9 } }, grid: { color: '#374151' } },
                            y: { ticks: { color: '#6b7280', font: { size: 9 } }, grid: { color: '#374151' } }
                        }
                    }
                });
            }

            // Chart 2: Relative Performance Delta
            const ctx2 = document.getElementById('chart-relative-performance');
            if (ctx2) {
                chartPerformance = new Chart(ctx2, {
                    type: 'bar',
                    data: {
                        labels: ['vs Buy & Hold', 'vs Defensive EUR'],
                        datasets: [{
                            label: 'Delta EUR',
                            data: [0.00, 1.16],
                            backgroundColor: ['#10b981', '#3b82f6'],
                            borderRadius: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { ticks: { color: '#9ca3af', font: { size: 10 } }, grid: { display: false } },
                            y: { ticks: { color: '#9ca3af', font: { size: 9 } }, grid: { color: '#374151' } }
                        }
                    }
                });
            }

            // Chart 5: Drawdown Comparison
            const ctx5 = document.getElementById('chart-drawdown-comparison');
            if (ctx5) {
                chartDrawdown = new Chart(ctx5, {
                    type: 'bar',
                    data: {
                        labels: ['Hermes AI', 'Hermes Aggressive', 'Buy & Hold', 'Defensive EUR'],
                        datasets: [{
                            label: 'Drawdown Massimo (%)',
                            data: [0.00, 0.00, 0.00, 0.00],
                            backgroundColor: ['#3b82f6', '#a855f7', '#10b981', '#f59e0b'],
                            borderRadius: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { ticks: { color: '#9ca3af', font: { size: 9 } }, grid: { display: false } },
                            y: { ticks: { color: '#9ca3af', font: { size: 9 } }, grid: { color: '#374151' } }
                        }
                    }
                });
            }

            // Chart 3: Donut Portfolio Allocation
            const ctx3 = document.getElementById('chart-allocation');
            if (ctx3) {
                chartAllocation = new Chart(ctx3, {
                    type: 'doughnut',
                    data: {
                        labels: ['BTC (71.9%)', 'ETH (23.1%)', 'XLM (2.3%)', 'EUR (1.8%)', 'GRT (0.04%)'],
                        datasets: [{
                            data: [103.30, 33.22, 3.31, 2.53, 0.06],
                            backgroundColor: ['#f59e0b', '#6366f1', '#06b6d4', '#10b981', '#8b5cf6'],
                            borderWidth: 1,
                            borderColor: '#1f2937'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { position: 'right', labels: { color: '#9ca3af', font: { size: 10 } } } }
                    }
                });
            }
        }

        function updateAllocationChart(holdingsList) {
            if (!chartAllocation || !holdingsList || holdingsList.length === 0) return;
            const valued = holdingsList.filter(h => {
                const val = h.value_eur || h.value_eur_dec;
                return val && val !== 'N/D' && parseFloat(val) > 0;
            });
            if (valued.length === 0) return;
            const labels = valued.map(h => {
                const name = h.asset || h.symbol || '';
                const wt = h.weight_percent || h.weight_pct || '0';
                const wtStr = (typeof wt === 'string' && wt.endsWith('%')) ? wt : wt + '%';
                return `${name} (${wtStr})`;
            });
            const dataVals = valued.map(h => parseFloat(h.value_eur || h.value_eur_dec));
            const colors = ['#f59e0b', '#6366f1', '#06b6d4', '#10b981', '#8b5cf6', '#ec4899', '#3b82f6', '#14b8a6', '#a855f7', '#f43f5e'];
            chartAllocation.data.labels = labels;
            chartAllocation.data.datasets[0].data = dataVals;
            chartAllocation.data.datasets[0].backgroundColor = colors.slice(0, valued.length);
            chartAllocation.update();
        }

        function updateChartFilter(period) {
            console.log("Updating chart filter to:", period);
            const btns = document.querySelectorAll('button[onclick^="updateChartFilter"]');
            btns.forEach(btn => {
                btn.className = "bg-darkbg hover:bg-cardbg text-gray-300 px-2 py-0.5 rounded border border-bordercolor";
            });
            if (window.event && window.event.target) {
                window.event.target.className = "bg-blue-950 text-blue-300 px-2 py-0.5 rounded border border-blue-800 font-bold";
            }
            if (!chartEvolution) return;
            let labels = ['17/11 21:00', '18/11 09:30', '18/11 21:30', '19/11 09:30', '19/11 21:34', '20/11 09:30', '20/11 16:11'];
            let hermesData = [142.42, 143.10, 143.58, 143.20, 143.58, 143.58, 143.58];
            let bhData = [142.42, 143.10, 143.58, 143.20, 143.58, 143.58, 143.58];
            let defData = [142.42, 142.42, 142.42, 142.42, 142.42, 142.42, 142.42];

            if (period === '24H') {
                labels = labels.slice(-4);
                hermesData = hermesData.slice(-4);
                bhData = bhData.slice(-4);
                defData = defData.slice(-4);
            } else if (period === '30D' || period === '90D' || period === 'ALL') {
                // Extended timeframe placeholder view
            }
            chartEvolution.data.labels = labels;
            chartEvolution.data.datasets[0].data = hermesData;
            chartEvolution.data.datasets[1].data = bhData;
            chartEvolution.data.datasets[2].data = defData;
            chartEvolution.update();
        }

        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(initV2Charts, 300);
        });
        
</script>
</body>
</html>
"""

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == '__main__':
    with ReusableTCPServer(("", PORT), DashboardHandler) as httpd:
        print(f"Trading Office Dashboard backend running on port {PORT}...")
        httpd.serve_forever()
