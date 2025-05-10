#!/bin/bash
cd "$(dirname "$0")/.."

if [ ! -d ".venv" ]; then
  echo "[SETUP] Tworzę środowisko wirtualne (.venv)..."
  python3 -m venv .venv
fi

source .venv/bin/activate

if [ -f "requirements.txt" ]; then
  echo "[SETUP] Instaluję zależności z requirements.txt..."
  pip install --upgrade pip
  pip install -r requirements.txt
else
  echo "[SETUP] Instaluję podstawowe zależności..."
  pip install flask matplotlib openpyxl requests
fi

if [ -z "$1" ]; then
  echo "[ERROR] Podaj zadanie do wykonania!"
  echo "Przykład: ./run_cli.sh \"pobierz dane z api i zapisz do excela\""
  exit 1
fi

echo "[RUN] Uruchamiam devopy CLI z zadaniem: $1"
python -m devopy.cli run "$1"
