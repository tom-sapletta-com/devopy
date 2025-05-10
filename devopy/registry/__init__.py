"""
Pakiet registry zawiera moduły do interakcji z różnymi rejestrami pakietów i zasobów.
"""

from devopy.registry.pypi import PyPIRegistry, search, install, get_info

__all__ = ['PyPIRegistry', 'search', 'install', 'get_info']
