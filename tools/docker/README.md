# Narzędzia Docker

Ten katalog zawiera skrypty i narzędzia związane z konteneryzacją i piaskownicą Docker używane w projekcie Devopy.

## Dostępne skrypty

- `run_docker_sandbox.sh` - Skrypt do uruchamiania piaskownicy Docker dla bezpiecznego wykonywania kodu

## Przeznaczenie

Narzędzia w tym katalogu służą do:

1. Uruchamiania izolowanych środowisk Docker do bezpiecznego wykonywania kodu
2. Zarządzania kontenerami Docker używanymi przez projekt Devopy
3. Konfiguracji i monitorowania usług uruchamianych w kontenerach

## Użycie

```bash
./tools/docker/run_docker_sandbox.sh [kod_do_wykonania]
```

Skrypty mogą być również importowane jako moduły w kodzie Python poprzez moduł `devopy.sandbox.docker_sandbox`.
