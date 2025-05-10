#!/bin/bash
# Skrypt do uruchamiania konwertera tekstu na kod Python

# Sprawdź, czy podano parametry
if [ $# -eq 0 ]; then
    echo "Użycie: $0 \"<opis zadania>\" [opcje]"
    echo ""
    echo "Opcje:"
    echo "  --output <plik>    Zapisz wygenerowany kod do pliku"
    echo "  --explain          Dodaj wyjaśnienie kodu"
    echo "  --improve <plik>   Ulepsz istniejący kod z pliku"
    echo "  --model <nazwa>    Użyj określonego modelu (domyślnie: codellama:7b-code)"
    echo ""
    echo "Przykłady:"
    echo "  $0 \"Napisz funkcję, która sortuje listę\" --output sort.py"
    echo "  $0 \"Napisz funkcję, która oblicza n-ty wyraz ciągu Fibonacciego\" --explain"
    echo "  $0 --improve existing_code.py --output improved_code.py"
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

# Sprawdź, czy Ollama jest zainstalowane
if ! command -v ollama &> /dev/null; then
    echo "Błąd: Ollama nie jest zainstalowane."
    echo "Zainstaluj Ollama, aby używać konwertera tekstu na kod:"
    echo "curl -fsSL https://ollama.com/install.sh | sh"
    exit 1
fi

# Sprawdź, czy model jest dostępny
MODEL="codellama:7b-code"
if ! ollama list | grep -q "$MODEL"; then
    echo "Model $MODEL nie jest dostępny. Pobieranie..."
    ollama pull $MODEL
fi

# Uruchom konwerter tekstu na kod
cd "$PROJECT_DIR"
python -m devopy.converters.text2python "$@"

# Wyświetl informację o zakończeniu
echo ""
echo "Konwersja zakończona."
