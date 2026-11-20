# REPORT DI INTEGRAZIONE E COLLAUDO END-TO-END MULTI-ASSET (STAGING)

**Data/Ora:** 2026-11-18  
**Coordinatore:** Trading Office Manager (`@trading-office-manager`)  
**Stato Operativo:** STAGING ISOLATO / TEST END-TO-END / NESSUNA ATTIVAZIONE LIVE  

---

## 1. Top 20 Reale e Motivi Tecnici del Fail-Closed
- **Verifica API Pubbliche Coinbase:**
  - L'endpoint `/products` espone 33 coppie EUR spot online (`status="online"` e `trading_disabled=false`).
  - L'endpoint order book `/products/<id>/book?level=2` include sequence e timestamp di fonte (`time`).
  - L'endpoint statistiche 24h `/products/<id>/stats` (volume 24h e last price) **non include un timestamp di fonte emesso da Coinbase**.
- **Perché la Top 20 è mantenuta in stato `insufficient_data` (Fail-Closed):**
  1. **Mancanza di sincronizzazione temporale alla fonte:** Non è possibile accertare la simultaneità temporale tra l'order book e le statistiche a 24 ore fornite da endpoint distinti di Coinbase Exchange.
  2. **Copertura storica incompleta:** La specifica quantitativa richiede la volatilità storica realizzata su 720 barre orarie chiuse (30 giorni). Gli archivi locali dispongono solo di BTC ed ETH (con lacune storiche di circa 38 ore su BTC e 35 ore su ETH rispetto al cutoff corrente) e non includono le altre 31 coppie EUR. Il download massivo è espressamente vietato.
  3. **Comportamento Rigoroso:** Il motore rifiuta classifiche basate su proxy di volume o dati non sincronizzati. Conformemente alla direttiva, viene restituito `ranking_status="insufficient_data"` con `top20=[]`.

---

## 2. Architettura di Integrazione e Passaggio Dati
Gli artefatti di staging sono stati collegati nel modulo `/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/e2e_integration.py`:
1. **Market Data Engine (`engine-review-r4`):**
   - Fornisce l'osservazione di mercato strutturata (`PUBLIC_MARKET`), validando rigorosamente envelope HTTP, cutoff delle candele chiuse e assenza di redirect.
2. **Ufficio Portfolio e Governance Versionata (`portfolio-paper-isolated`):**
   - Gestisce i tre insiemi (`holdings` distinte in `CONFIGURED`/`SYNTHETIC`/`PENDING_PORTFOLIO`, `opportunities` e `custom`).
   - Le modifiche applicano il ciclo: `PROPOSED` (proposta) $\to$ `APPROVED` (approvazione distinta) $\to$ `PUBLISHED` (pubblicazione con digest verificato).
   - Il rollback crea una nuova versione `PROPOSED` con audit append-only su trigger SQLite immutabili.
3. **Analisti e Advisory Packet:**
   - Strutturato con le valutazioni di Market Analyst, Bear Analyst (con potere di veto) e Trading Strategist.
4. **Deterministic Risk Engine:**
   - Verifica: stato dati, veto Bear Analyst, decisione del Trading Director, numero massimo di posizioni aperte (1), limite di esposizione (60 EUR) e budget di perdita giornaliera.
5. **Paper Execution Guard:**
   - Nel contratto di integrazione, `paper` è rigidamente `DISABLED` (`can_execute=false`) e `risk` restituisce `DENY`. Nessun ordine può essere inviato.
   - Il motore paper virtuale in memoria (`:memory:`) gestisce l'atomicità tra cassa, posizione, ledger, fee (0.1%), slippage e registro giornaliero `Europe/Rome`.

---

## 3. Analisi di Sicurezza: `OS_BLOCKED` e Isolamento Filesystem
- **Causa di `OS_BLOCKED`:**
  - Nel runtime attuale, tutti i profili operano sotto l'utente Linux condiviso `hermes` (UID 1001).
  - La creazione di file di staging su percorsi disco condivisi (`create_stage`) non dispone di confini POSIX tra profili. Esiste un rischio teorico di race condition (ad es. sostituzione di symlink o percorsi tra `O_CREAT|O_EXCL` e la successiva connessione SQLite).
- **Soluzione di Isolamento Definita:**
  1. **Modalità Attuale (Staging):** Mantenimento rigoroso di `OS_BLOCKED` per le scritture non isolate su disco; le esecuzioni avvengono esclusivamente in database in memoria (`:memory:`) o file temporanei effimeri in scratch protetto.
  2. **Soluzione Operativa Target (Produzione futura):**
     - Separazione dei processi tramite Linux User Namespace o container dedicati con UID/GID distinti non sovrapposti.
     - Filesystem con mount namespace privati e directory ad accesso esclusivo `0700` con risoluzione sicura via file descriptor (`O_NOFOLLOW` / `openat`).
     - Apertura degli archivi storici sempre in sola lettura con `PRAGMA query_only=ON`.

---

## 4. Separazione Configurazione: Parametri di Test vs Operativi
- **Separazione Netta:**
  - I parametri del test (capitale 100 EUR, rischio 1 EUR/trade, esposizione 60 EUR, limite giornaliero 3 EUR) sono vincoli sintetici di collaudo e **non devono essere interpretati come limiti operativi imposti per decreto**.
  - Eventuali valori operativi definitivi dovranno essere approvati esplicitamente dall'utente e registrati tramite la governance versionata con policy id formale.

---

## 5. Esito del Collaudo End-to-End
Il modulo `e2e_integration.py` testa la catena completa:
1. `market_engine_contract`: **PASS** (schema coerente, `insufficient_data` e `top20=[]`).
2. `portfolio_governance_lifecycle`: **PASS** (proposta $\to$ approvazione $\to$ pubblicazione $\to$ rollback come proposta $\to$ ri-approvazione).
3. `risk_gate_and_veto`: **PASS** (il veto attivo del Bear Analyst blocca categoricamente il gate con `DENY`; la rimozione del veto consente il `PASS`).
4. `paper_execution_guard`: **PASS** (`paper=DISABLED` e `can_execute=False` impediscono qualsiasi esecuzione anche a fronte di gate positivo).
5. `paper_settlement_atomicity`: **PASS** (apertura atomica, deduplicazione idempotente, chiusura con calcolo P&L da fill/fee e rilascio riserva).

---

## 6. Vincoli di Sistema Confermati
- Cron Trading: Tutti i 5 job (`22cd985ad4f8`, `94deabba09b5`, `816674406c22`, `7b4b90be5563`, `3e162fa9f571`) restano **paused**.
- Paper Trading: **DISABLED**.
- Archivi Originali: Intatti, non modificati e aperti solo `mode=ro`.
- Connessione Coinbase Privata: **PENDING_AUTH**.
