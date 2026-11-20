# PIANO TECNICO DI ISOLAMENTO FILESYSTEM E PROCESSI

**Documento:** Architettura di Isolamento e Risoluzione `OS_BLOCKED`  
**Autori:** Trading Office Manager (`@trading-office-manager`), con audit di Linu (`@linu`) e Docky (`@docky`)  
**Data:** 2026-11-18  
**Stato Operativo Attuale:** `OS_BLOCKED` **CONFERMATO E MANTENUTO ATTIVO**  

---

## 1. Analisi dello Stato Attuale e Causa di `OS_BLOCKED`

### A. Condivisione dell'Identità Utente (UID 1001)
- Tutti i profili Hermes (`trading-office-manager`, `docky`, `botty`, `linu`, `market-analyst`, ecc.) sono eseguiti all'interno dello stesso container/host sotto il medesimo utente non privilegiato:
  ```text
  uid=1001(hermes) gid=1001(hermes) groups=1001(hermes)
  ```
- **Assenza di confini POSIX tra agenti:** Poiché i file di tutti i profili risiedono sotto `/opt/data/profiles/` e condividono lo stesso proprietario `hermes:hermes` con permessi tipici `0755` o `0644`, a livello di sistema operativo qualsiasi processo eseguito da un agente ha i permessi di lettura e scrittura sui file degli altri agenti.

### B. Vincoli del Kernel e Capabilities
- Il processo opera con `CapEff = 0000000000000000` (nessuna capability Linux abilitata).
- Il tentativo di creare un namespace utente separato non privilegiato tramite `os.unshare(CLONE_NEWUSER)` restituisce:
  ```text
  PermissionError: [Errno 1] Operation not permitted
  ```
  a causa delle policy di sicurezza imposte dall'host container/LXC (ad es. `kernel.unprivileged_userns_clone = 0` o seccomp profile).

### C. Vulnerabilità alle Race Condition su Filesystem Condiviso
- La primitiva originaria `create_stage()` tentava di creare file di staging aprendo percorsi su filesystem condiviso con `O_CREAT | O_EXCL` e successivamente invocando `sqlite3.connect()`.
- Su un filesystem condiviso tra processi a pari UID, sussiste il rischio di TOCTOU (Time-of-Check to Time-of-Use):
  - Sostituzione di directory genitrici con symlink prima della connessione SQLite.
  - Mancanza di isolamento delle lock file di SQLite.
- **Decisione di sicurezza:** Lo stato `OS_BLOCKED` è stato imposto e rimane attivo, bloccando qualsiasi scrittura su disco non confinata.

---

## 2. Proposta Concreta di Isolamento per la Produzione Futura

Per consentire l'ingestione persistente su disco rimuovendo in sicurezza `OS_BLOCKED`, viene definita la seguente architettura a 3 livelli:

### Livello 1: Segregazione delle Identità di Sistema (UID/GID Distinti)
- Creazione a livello host/container di account POSIX dedicati per i diversi domini:
  - `uid=1001(hermes-core)`: Gateway e orchestratore.
  - `uid=1002(hermes-market)`: Acquisizione dati e downloader pubblici.
  - `uid=1003(hermes-risk)`: Risk Engine e Paper Trading Ledger.
  - `uid=1004(hermes-analysts)`: Esecuzione consultiva degli agenti LLM.
- Assegnazione dei workspace con permessi stretti `0700` (`rwx------`), impedendo a qualunque altro processo la lettura/scrittura dei dati sensibili o dei database.

### Livello 2: Confinamento Filesystem e Mount Namespaces
- Abilitazione da parte dell'amministratore host del supporto ai container rootless o User Namespaces (`unshare --user --mount`).
- Esecuzione dei processi del Market Data Engine all'interno di un Mount Namespace privato con:
  - Filesystem radice in sola lettura (`pivot_root` o `chroot`).
  - `/opt/data/trading-office-data/` montato esclusivamente in **`read-only`** (`MS_RDONLY`).
  - Directory `/tmp` e scratch effimero allocate su `tmpfs` isolato e distrutto all'uscita del processo.
- Apertura sicura dei file mediante descrittori relativi:
  - Utilizzo di `openat(dirfd, filename, O_RDWR | O_CREAT | O_EXCL | O_NOFOLLOW)` per azzerare qualsiasi rischio di symlink traversal.

### Livello 3: Confinamento di Rete (Network Egress Allowlist)
- Isolamento dello stack di rete per i processi di esecuzione e paper trading:
  - Network namespace privato privo di interfaccia esterna (`--net=none`) per il motore paper, impedendo qualsiasi connessione accidentale a internet o all'exchange.
  - Per il downloader pubblico, network namespace con firewall `nftables`/`iptables` configurato per consentire traffico in uscita esclusivamente verso l'endpoint autorizzato `api.exchange.coinbase.com` sulla porta 443.

---

## 3. Gestione nello Stato Attuale (Transitorio Sicuro)
- Fino alla configurazione dell'infrastruttura di Livello 1-3 da parte dell'amministratore:
  1. **`OS_BLOCKED` rimane formalmente attivo nel codice operativo.**
  2. Tutte le manipolazioni e simulazioni multi-valuta avvengono rigorosamente in memoria (`:memory:`), garantendo la totale assenza di persistenza non controllata o conflitti su disco.
  3. Gli archivi storici rimangono aperti esclusivamente con flag `mode=ro` e direttiva `PRAGMA query_only=ON`.
