# Dockerfile per Market Data Engine Isolato (Non avviato, deployable)
# Implementa separazione UID/GID e isolamento filesystem/rete
FROM debian:12-slim

# Crea utente di servizio non privilegiato dedicato con UID/GID specifico
RUN groupadd -g 1002 hermes-market && \
    useradd -u 1002 -g hermes-market -m -s /bin/bash -d /home/hermes-market hermes-market

# Installa solo dipendenze minime
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-minimal \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Crea directory protette con permessi 0700
RUN mkdir -p /app /app/staging /app/readonly_archives && \
    chown -R hermes-market:hermes-market /app && \
    chmod 0700 /app/staging

COPY --chown=1002:1002 service_runner.py container_acquirer.py dynamic_universe_engine.py /app/

USER hermes-market
WORKDIR /app

# Variabili d'ambiente per forzare isolamento
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["python3", "-B"]
