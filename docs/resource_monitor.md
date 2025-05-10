# Monitor Zasobów Systemowych dla Devopy

Monitor zasobów systemowych to narzędzie, które automatycznie monitoruje i zarządza zasobami systemowymi używanymi przez projekt Devopy. Pomaga zapobiegać problemom związanym z wyczerpaniem zasobów i utrzymuje system w optymalnym stanie.

## Funkcje

1. **Monitorowanie zużycia RAM**
   - Wykrywanie wysokiego zużycia pamięci (powyżej 90%)
   - Automatyczne działania naprawcze w przypadku niskiej dostępności pamięci

2. **Monitorowanie zużycia dysku**
   - Śledzenie zużycia dysku przez projekt Devopy
   - Ograniczanie rozmiaru plików logów
   - Automatyczne czyszczenie starych plików logów

3. **Zarządzanie kontenerami Docker**
   - Wykrywanie i usuwanie nieużywanych kontenerów Docker
   - Czyszczenie nieużywanych obrazów Docker

4. **Wykrywanie procesów zombie**
   - Identyfikacja i usuwanie procesów zombie
   - Zapobieganie wyciekom zasobów

5. **Generowanie raportów**
   - Tworzenie szczegółowych raportów o stanie zasobów systemowych
   - Śledzenie trendów zużycia zasobów

## Instalacja

Monitor zasobów jest wbudowany w projekt Devopy i nie wymaga dodatkowej instalacji. Wymagane zależności:

```bash
pip install psutil
```

## Użycie

Monitor zasobów można uruchomić za pomocą skryptu `run_monitor.sh` z katalogu `scripts`:

```bash
# Uruchomienie w trybie interaktywnym
./scripts/run_monitor.sh

# Uruchomienie w tle
./scripts/run_monitor.sh --background

# Wygenerowanie raportu o stanie zasobów
./scripts/run_monitor.sh --report

# Czyszczenie nieużywanych zasobów
./scripts/run_monitor.sh --clean

# Wykonanie testu monitora
./scripts/run_monitor.sh --test
```

Alternatywnie, można użyć modułu bezpośrednio:

```bash
python -m devopy.utils.resource_monitor [opcje]
```

## Konfiguracja

Konfiguracja monitora zasobów znajduje się na początku pliku `devopy/utils/resource_monitor.py`. Główne parametry konfiguracyjne:

```python
# Konfiguracja
MAX_RAM_PERCENT = 90  # Maksymalne zużycie RAM w procentach
MAX_DISK_USAGE = 100 * 1024 * 1024 * 1024  # 100GB w bajtach
LOG_ROTATION_SIZE = 100 * 1024 * 1024  # 100MB
LOG_ROTATION_COUNT = 5  # Liczba plików rotacji
CHECK_INTERVAL = 60  # Interwał sprawdzania w sekundach
```

Można dostosować te parametry do własnych potrzeb, edytując plik.

## Automatyczne uruchamianie

Aby monitor zasobów uruchamiał się automatycznie przy starcie systemu, można dodać go do zadań cron:

```bash
# Dodanie do crontab
(crontab -l 2>/dev/null; echo "@reboot cd /ścieżka/do/devopy && ./scripts/run_monitor.sh --background") | crontab -
```

## Raporty

Raporty generowane przez monitor zasobów są zapisywane w katalogu `reports` w formacie JSON. Każdy raport zawiera szczegółowe informacje o:

- Zużyciu CPU i RAM
- Zużyciu dysku
- Procesach systemowych
- Kontenerach Docker
- Plikach logów

Przykład wygenerowanego raportu:

```json
{
  "timestamp": "2025-05-10T15:30:00",
  "system": {
    "cpu_count": 8,
    "cpu_percent": 12.5,
    "ram_total": 16000000000,
    "ram_available": 8000000000,
    "ram_percent": 50.0
  },
  "disk": {
    "/": {
      "total": 500000000000,
      "used": 250000000000,
      "free": 250000000000,
      "percent": 50.0
    }
  },
  "processes": {
    "total": 100,
    "running": 10,
    "sleeping": 85,
    "stopped": 0,
    "zombie": 5
  }
}
```

## Rozwiązywanie problemów

Jeśli monitor zasobów nie działa poprawnie, sprawdź:

1. Czy wszystkie zależności są zainstalowane (`psutil`)
2. Czy katalog `logs` istnieje i ma odpowiednie uprawnienia
3. Czy użytkownik ma uprawnienia do zarządzania kontenerami Docker

Logi monitora zasobów są zapisywane w pliku `logs/resource_monitor.log`.

## Integracja z API i CLI

Monitor zasobów może być zintegrowany z API i CLI Devopy. Aby uzyskać informacje o stanie zasobów z poziomu API:

```python
from devopy.utils.resource_monitor import ResourceMonitor, generate_report

# Utworzenie instancji monitora
monitor = ResourceMonitor()

# Pobranie informacji o zasobach
ram_usage = monitor.get_ram_usage()
disk_usage = monitor.get_disk_usage()

# Wygenerowanie raportu
report_file = generate_report()
```

## Rozszerzanie funkcjonalności

Monitor zasobów można łatwo rozszerzyć o dodatkowe funkcje. Aby dodać nową funkcję monitorowania:

1. Dodaj nową metodę do klasy `ResourceMonitor`
2. Zintegruj ją z metodą `check_and_manage_resources`
3. Zaktualizuj dokumentację

Przykład dodania monitorowania temperatury CPU:

```python
def get_cpu_temperature(self):
    """Pobiera temperaturę CPU"""
    # Implementacja
    pass
```