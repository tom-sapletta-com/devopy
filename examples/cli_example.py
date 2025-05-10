#!/usr/bin/env python3
from devopy.cli import main

# Przykład użycia CLI bezpośrednio z kodu Python
if __name__ == "__main__":
    task = "pobierz dane z api i zapisz do excela"
    main(["run", task])
