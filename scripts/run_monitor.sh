#!/bin/bash
# Skrypt do uruchamiania monitora zasobów dla projektu devopy

# Przejdź do katalogu głównego projektu
cd "$(dirname "$0")/.." || exit 1

# Aktywuj środowisko wirtualne, jeśli istnieje
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Uruchom monitor zasobów z odpowiednimi parametrami
if [ "$1" == "--background" ] || [ "$1" == "-b" ]; then
    python -m devopy.utils.resource_monitor --background
    echo "Monitor zasobów uruchomiony w tle"
elif [ "$1" == "--report" ] || [ "$1" == "-r" ]; then
    python -m devopy.utils.resource_monitor --report
elif [ "$1" == "--clean" ] || [ "$1" == "-c" ]; then
    python -m devopy.utils.resource_monitor --clean
elif [ "$1" == "--test" ] || [ "$1" == "-t" ]; then
    python -m devopy.utils.resource_monitor --test
else
    echo "Uruchamianie monitora zasobów w trybie interaktywnym..."
    python -m devopy.utils.resource_monitor
fi
