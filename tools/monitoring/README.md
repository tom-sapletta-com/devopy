# Narzędzia monitorowania

Ten katalog zawiera skrypty i narzędzia do monitorowania zasobów i wydajności używane w projekcie Devopy.

## Dostępne skrypty

- `run_monitor.sh` - Skrypt do uruchamiania monitora zasobów systemowych

## Przeznaczenie

Narzędzia w tym katalogu służą do:

1. Monitorowania zużycia zasobów (CPU, pamięć, dysk) podczas wykonywania kodu
2. Zbierania metryk wydajnościowych
3. Generowania raportów z monitoringu

## Użycie

```bash
./tools/monitoring/run_monitor.sh [opcje]
```

Skrypty mogą być również importowane jako moduły w kodzie Python poprzez moduł `devopy.utils.resource_monitor`.
