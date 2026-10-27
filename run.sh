#!/usr/bin/env bash
# ==============================================================================
# PulseCare AI - Launch Script
# System: PulseCare AI - Intelligent Emergency Healthcare & Telemetry System
# ==============================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=================================================================="
echo "    PulseCare AI - Intelligent Emergency Healthcare System        "
echo "    Clinical Telemetry & Hospital Operations Platform             "
echo "=================================================================="

# 1. Ensure data/db directory exists
mkdir -p ./data/db

# 2. Check if MongoDB is running on port 27017
if ! nc -z 127.0.0.1 27017 2>/dev/null; then
    echo "Starting local MongoDB 7.0 daemon..."
    mongod --dbpath ./data/db --nounixsocket --bind_ip 127.0.0.1 --port 27017 --fork --logpath ./data/mongod.log --setParameter diagnosticDataCollectionEnabled=false
    sleep 1
else
    echo "✔ MongoDB is already running on port 27017."
fi

# 3. Seed database if not populated
echo "Verifying database collections and $jsonSchema rules..."
./venv/bin/python3 backend/seed_data.py

# 4. Start Flask Application
echo "Starting PulseCare AI Web Server on http://127.0.0.1:5000 ..."
exec ./venv/bin/python3 backend/app.py
