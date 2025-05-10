#!/bin/bash
# Skrypt do uruchamiania testów integracyjnych dla projektu devopy

# Przejście do katalogu głównego projektu
cd "$(dirname "$0")/.." || exit 1

# Kolory dla lepszej czytelności
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Uruchamianie testów integracyjnych dla projektu devopy ===${NC}"

# Sprawdzenie, czy Docker jest dostępny
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Docker jest zainstalowany${NC}"
    if docker info &> /dev/null; then
        echo -e "${GREEN}✓ Usługa Docker jest uruchomiona${NC}"
        DOCKER_AVAILABLE=true
    else
        echo -e "${YELLOW}⚠ Usługa Docker nie jest uruchomiona - niektóre testy zostaną pominięte${NC}"
        DOCKER_AVAILABLE=false
    fi
else
    echo -e "${YELLOW}⚠ Docker nie jest zainstalowany - niektóre testy zostaną pominięte${NC}"
    DOCKER_AVAILABLE=false
fi

# Sprawdzenie, czy Ollama jest dostępny
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓ Ollama jest zainstalowana${NC}"
    if curl -s http://localhost:11434/api/version &> /dev/null; then
        echo -e "${GREEN}✓ Usługa Ollama jest uruchomiona${NC}"
        OLLAMA_AVAILABLE=true
    else
        echo -e "${YELLOW}⚠ Usługa Ollama nie jest uruchomiona - zostanie użyty tryb fallback${NC}"
        OLLAMA_AVAILABLE=false
    fi
else
    echo -e "${YELLOW}⚠ Ollama nie jest zainstalowana - zostanie użyty tryb fallback${NC}"
    OLLAMA_AVAILABLE=false
fi

# Sprawdzenie zmiennej środowiskowej OPENAI_API_KEY
if [ -n "$OPENAI_API_KEY" ]; then
    echo -e "${GREEN}✓ Zmienna OPENAI_API_KEY jest ustawiona${NC}"
    OPENAI_AVAILABLE=true
else
    echo -e "${YELLOW}⚠ Zmienna OPENAI_API_KEY nie jest ustawiona - testy OpenAI zostaną pominięte${NC}"
    OPENAI_AVAILABLE=false
fi

echo -e "${BLUE}=== Uruchamianie testów integracyjnych ===${NC}"

# Uruchomienie testów integracyjnych
python -m unittest discover -s tests/integration

# Sprawdzenie wyniku testów
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Wszystkie testy integracyjne zakończone pomyślnie${NC}"
else
    echo -e "${RED}✗ Niektóre testy integracyjne nie powiodły się${NC}"
    exit 1
fi

echo -e "${BLUE}=== Testy zakończone ===${NC}"
