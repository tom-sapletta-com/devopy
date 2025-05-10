# Katalog bin

Ten katalog zawiera skrypty wykonywalne, które są używane do uruchamiania głównych komponentów projektu Devopy.

## Dostępne skrypty

- `run_api.sh` - Uruchamia API REST projektu Devopy
- `run_cli.sh` - Uruchamia interfejs wiersza poleceń (CLI) projektu Devopy
- `run_integration_tests.sh` - Uruchamia testy integracyjne sprawdzające współpracę między modułami

## Użycie

Skrypty można uruchamiać bezpośrednio z katalogu głównego projektu:

```bash
./bin/run_api.sh
./bin/run_cli.sh
./bin/run_integration_tests.sh
```

Wszystkie skrypty posiadają uprawnienia wykonywania i mogą być uruchamiane bezpośrednio z powłoki.
