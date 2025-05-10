# Testy Integracyjne Devopy

Ten katalog zawiera testy integracyjne dla projektu Devopy, które sprawdzają współpracę między różnymi modułami systemu.

## Cel testów integracyjnych

Testy integracyjne mają na celu sprawdzenie, czy różne moduły systemu Devopy współpracują ze sobą poprawnie. W przeciwieństwie do testów jednostkowych, które testują poszczególne komponenty w izolacji, testy integracyjne weryfikują interakcje między modułami.

## Testowane moduły

Testy integracyjne sprawdzają współpracę między następującymi modułami:

1. **Menedżer zależności** (`dependency_manager`) - odpowiedzialny za analizę kodu i zarządzanie zależnościami
2. **Konwerter tekstu na kod** (`text2python`) - konwertuje opisy w języku naturalnym na kod Python
3. **Piaskownica Docker** (`docker_sandbox`) - umożliwia bezpieczne uruchamianie kodu w kontenerach Docker

## Wymagania

Do uruchomienia pełnego zestawu testów integracyjnych potrzebne są:

- Python 3.8 lub nowszy
- Docker (opcjonalnie, ale zalecane)
- Ollama z zainstalowanym modelem `codellama:7b-code` (opcjonalnie)
- Klucz API OpenAI (opcjonalnie)

## Uruchamianie testów

Testy integracyjne można uruchomić za pomocą skryptu `run_integration_tests.sh` znajdującego się w katalogu `scripts`:

```bash
./scripts/run_integration_tests.sh
```

Skrypt automatycznie wykryje dostępność Dockera, Ollamy i klucza API OpenAI, i odpowiednio dostosuje uruchamiane testy.

Alternatywnie, można uruchomić testy bezpośrednio za pomocą Pythona:

```bash
python -m unittest discover -s tests/integration
```

## Struktura testów

Testy integracyjne są zorganizowane w następujący sposób:

- `test_modules_integration.py` - testy integracji między modułami menedżera zależności, konwertera tekstu na kod i piaskownicy Docker

## Dodawanie nowych testów

Aby dodać nowe testy integracyjne:

1. Utwórz nowy plik w katalogu `tests/integration` z prefixem `test_`.
2. Zaimplementuj testy jako klasy dziedziczące po `unittest.TestCase`.
3. Użyj dekoratora `@unittest.skipIf` dla testów, które wymagają opcjonalnych zależności (np. Docker, Ollama).

Przykład:

```python
import unittest
from devopy.sandbox.docker_sandbox import check_docker_available

@unittest.skipIf(not check_docker_available()[0], "Docker nie jest dostępny")
def test_my_docker_feature(self):
    # Test kodu wymagającego Dockera
    pass
```

## Interpretacja wyników

Po uruchomieniu testów integracyjnych, wyniki będą wyświetlone w konsoli. Każdy test może zakończyć się jednym z trzech statusów:

- `.` - test zakończony sukcesem
- `F` - test zakończony niepowodzeniem
- `s` - test pominięty (np. z powodu braku Dockera)

W przypadku niepowodzenia testu, zostanie wyświetlony szczegółowy opis błędu, który pomoże zidentyfikować problem.
