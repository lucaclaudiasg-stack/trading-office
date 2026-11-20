#!/bin/bash
# Script per aggiungere la chiave pubblica di Hermes all'utente lucasguotti sull'host 10.0.6.1
KEY_FILE="/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/authorized_keys_append.txt"

if [ -f "$KEY_FILE" ]; then
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
    cat "$KEY_FILE" >> ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys
    echo "Chiave aggiunta con successo a ~/.ssh/authorized_keys!"
else
    echo "Errore: file $KEY_FILE non trovato."
fi
