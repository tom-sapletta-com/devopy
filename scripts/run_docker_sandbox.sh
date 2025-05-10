#!/bin/bash
# Skrypt do uruchamiania piaskownicy Docker

# Sprawdź, czy podano parametry
if [ $# -eq 0 ]; then
    echo "Użycie: $0 [opcje]"
    echo ""
    echo "Opcje:"
    echo "  --code \"<kod>\"       Kod Python do wykonania"
    echo "  --file <plik>       Plik z kodem Python do wykonania"
    echo "  --service           Uruchom jako usługę"
    echo "  --port <port>       Port dla usługi (domyślnie: 8000)"
    echo "  --stop <kontener>   Zatrzymaj usługę o podanej nazwie kontenera"
    echo "  --timeout <sek>     Limit czasu wykonania w sekundach (domyślnie: 30)"
    echo ""
    echo "Przykłady:"
    echo "  $0 --file skrypt.py"
    echo "  $0 --code \"print('Hello from sandbox!')\""
    echo "  $0 --file server.py --service --port 8080"
    echo "  $0 --stop devopy-service-12345678"
    exit 1
fi

# Aktywuj środowisko wirtualne, jeśli istnieje
if [ -d "../.venv" ]; then
    source ../.venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Ustal ścieżkę do projektu
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Sprawdź, czy Docker jest zainstalowany
if ! command -v docker &> /dev/null; then
    echo "Błąd: Docker nie jest zainstalowany."
    echo "Zainstaluj Docker, aby używać piaskownicy:"
    echo "https://docs.docker.com/get-docker/"
    exit 1
fi

# Sprawdź, czy Docker działa
if ! docker info &> /dev/null; then
    echo "Błąd: Docker nie działa."
    echo "Uruchom usługę Docker i spróbuj ponownie."
    exit 1
fi

# Uruchom piaskownicę Docker
cd "$PROJECT_DIR"
python -m devopy.sandbox.docker_sandbox "$@"

# Wyświetl informację o zakończeniu
if [ $? -eq 0 ]; then
    echo ""
    echo "Operacja zakończona pomyślnie."
else
    echo ""
    echo "Operacja zakończona z błędem."
fi
