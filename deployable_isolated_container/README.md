# Configurazione Deployabile per Market Data Engine Isolato

**Finalità:** Fornire un modello pronto per il deployment su container o host separato che soddisfi tutti i criteri di sicurezza definiti dall'architettura senza alterare l'installazione corrente.

## Misure di Sicurezza Implementate:
1. **UID/GID Distinti:**
   - Esecuzione sotto l'utente `hermes-market` (`uid=1002`, `gid=1002`), eliminando la condivisione dell'UID 1001 con gli altri agenti.
2. **Confinamento Filesystem & RootFS Read-Only:**
   - `read_only: true`: L'intero filesystem del container è montato in sola lettura.
   - Solo `/app/staging` è montato in lettura/scrittura su un volume dedicato esclusivo (`mode=0700`).
   - Gli archivi originali BTC ed ETH sono montati con flag esplicito `:ro` (read-only vincolato a livello di kernel mount namespace).
   - `/tmp` è un `tmpfs` isolato da 64MB senza persistenza.
3. **Privilege & Capability Drop:**
   - `cap_drop: ALL`: Rimozione totale di tutte le capabilities Linux.
   - `security_opt: no-new-privileges:true`: Prevenzione di qualsiasi escalation dei privilegi.
4. **Isolamento da Race Condition:**
   - La separazione dell'UID impedisce a qualsiasi altro profilo di sistema o bot di accedere, creare symlink o manipolare i file della directory `/app/staging`.
5. **Stato:**
   - **CONFIGURAZIONE DOCUMENTALE DEPLOYABILE — NON AVVIATA.**
   - Nel runtime locale corrente, `OS_BLOCKED` rimane rigorosamente attivo.
