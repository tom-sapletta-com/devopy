#!/bin/bash
# Skrypt instalacyjny dla projektu Devopy
# Konfiguruje środowisko i strukturę projektu

# Kolory dla lepszej czytelności
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Instalacja projektu Devopy ===${NC}"

# Sprawdzenie, czy Python jest zainstalowany
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Python jest zainstalowany: ${PYTHON_VERSION}${NC}"
else
    echo -e "${RED}✗ Python 3 nie jest zainstalowany. Proszę zainstalować Python 3.8 lub nowszy.${NC}"
    exit 1
fi

# Tworzenie środowiska wirtualnego
echo -e "${BLUE}Tworzenie środowiska wirtualnego...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}Katalog venv już istnieje. Używam istniejącego środowiska.${NC}"
else
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Nie udało się utworzyć środowiska wirtualnego.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Środowisko wirtualne zostało utworzone.${NC}"
fi

# Aktywacja środowiska wirtualnego
echo -e "${BLUE}Aktywacja środowiska wirtualnego...${NC}"
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Nie udało się aktywować środowiska wirtualnego.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Środowisko wirtualne zostało aktywowane.${NC}"

# Instalacja projektu w trybie deweloperskim
echo -e "${BLUE}Instalacja projektu w trybie deweloperskim...${NC}"
pip install -e .
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Nie udało się zainstalować projektu.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Projekt został zainstalowany w trybie deweloperskim.${NC}"

# Nadanie uprawnień wykonywania dla skryptów
echo -e "${BLUE}Nadawanie uprawnień wykonywania dla skryptów...${NC}"
chmod +x bin/*.sh tools/docker/*.sh tools/monitoring/*.sh tools/scripts/*.sh 2>/dev/null
echo -e "${GREEN}✓ Uprawnienia wykonywania zostały nadane.${NC}"

# Sprawdzenie, czy Docker jest dostępny
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Docker jest zainstalowany${NC}"
    if docker info &> /dev/null; then
        echo -e "${GREEN}✓ Usługa Docker jest uruchomiona${NC}"
    else
        echo -e "${YELLOW}⚠ Usługa Docker nie jest uruchomiona - niektóre funkcje będą niedostępne${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Docker nie jest zainstalowany - niektóre funkcje będą niedostępne${NC}"
fi

# Sprawdzenie, czy Ollama jest dostępny
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓ Ollama jest zainstalowana${NC}"
    if curl -s http://localhost:11434/api/version &> /dev/null; then
        echo -e "${GREEN}✓ Usługa Ollama jest uruchomiona${NC}"
    else
        echo -e "${YELLOW}⚠ Usługa Ollama nie jest uruchomiona - zostanie użyty tryb fallback${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Ollama nie jest zainstalowana - zostanie użyty tryb fallback${NC}"
fi

echo -e "${BLUE}=== Instalacja zakończona ===${NC}"
echo -e "${GREEN}Projekt Devopy został pomyślnie zainstalowany!${NC}"
echo -e "${YELLOW}Aby aktywować środowisko wirtualne, użyj: source venv/bin/activate${NC}"
echo -e "${YELLOW}Aby uruchomić API, użyj: ./bin/run_api.sh${NC}"
echo -e "${YELLOW}Aby uruchomić CLI, użyj: ./bin/run_cli.sh \"twoje polecenie\"${NC}"
echo -e "${YELLOW}Aby uruchomić testy integracyjne, użyj: ./bin/run_integration_tests.sh${NC}"
