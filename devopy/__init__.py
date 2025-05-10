"""Devopy - Modularny asystent AI do automatyzacji kodu i środowisk Python"""

__version__ = "0.1.0"
__author__ = "tom-sapletta-com"

# Importy będą dostępne po zainstalowaniu paczki
try:
    # Próbujemy zaimportować główne komponenty
    from devopy.api import app
    from devopy.cli import main as cli_main
    from devopy.orchestrator import Orchestrator
except ImportError:
    # W przypadku błędu importu (np. podczas instalacji) nie robimy nic
    pass
