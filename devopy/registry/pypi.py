"""
Moduł do interakcji z rejestrem PyPI (Python Package Index).
Umożliwia wyszukiwanie, pobieranie informacji i instalację pakietów Python.
"""

import subprocess
import sys
import json
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional, Union


class PyPIRegistry:
    """Klasa do interakcji z rejestrem PyPI."""
    
    BASE_URL = "https://pypi.org/pypi"
    
    def __init__(self):
        """Inicjalizacja rejestru PyPI."""
        self.session = requests.Session()
    
    def search_package(self, query: str) -> List[Dict[str, Any]]:
        """
        Wyszukuje pakiety w PyPI na podstawie zapytania.
        
        Args:
            query: Zapytanie do wyszukania.
            
        Returns:
            Lista pasujących pakietów.
        """
        url = f"https://pypi.org/search/?q={query}&format=json"
        response = self.session.get(url)
        response.raise_for_status()
        
        try:
            data = response.json()
            return data.get("results", [])
        except json.JSONDecodeError:
            return []
    
    def get_package_info(self, package_name: str, version: Optional[str] = None) -> Dict[str, Any]:
        """
        Pobiera informacje o pakiecie z PyPI.
        
        Args:
            package_name: Nazwa pakietu.
            version: Opcjonalna wersja pakietu.
            
        Returns:
            Słownik z informacjami o pakiecie.
        """
        url = f"{self.BASE_URL}/{package_name}"
        if version:
            url += f"/{version}"
        url += "/json"
        
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.json()
    
    def install_package(self, package_name: str, version: Optional[str] = None, 
                        upgrade: bool = False, user: bool = False, venv_path: Optional[str] = None) -> bool:
        """
        Instaluje pakiet z PyPI.
        
        Args:
            package_name: Nazwa pakietu do zainstalowania.
            version: Opcjonalna wersja pakietu.
            upgrade: Czy aktualizować pakiet, jeśli jest już zainstalowany.
            user: Czy instalować w trybie użytkownika.
            venv_path: Opcjonalna ścieżka do środowiska wirtualnego, w którym ma być zainstalowany pakiet.
            
        Returns:
            True, jeśli instalacja się powiodła, False w przeciwnym razie.
        """
        if venv_path:
            # Użyj pip z podanego środowiska wirtualnego
            pip_path = Path(venv_path) / ("Scripts\pip.exe" if sys.platform == "win32" else "bin/pip")
            cmd = [str(pip_path), "install"]
        else:
            # Użyj pip z bieżącego interpretera
            cmd = [sys.executable, "-m", "pip", "install"]
        
        if upgrade:
            cmd.append("--upgrade")
        
        if user:
            cmd.append("--user")
        
        if version:
            cmd.append(f"{package_name}=={version}")
        else:
            cmd.append(package_name)
        
        try:
            subprocess.check_call(cmd)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def check_installed_version(self, package_name: str) -> Optional[str]:
        """
        Sprawdza zainstalowaną wersję pakietu.
        
        Args:
            package_name: Nazwa pakietu.
            
        Returns:
            Wersja pakietu lub None, jeśli pakiet nie jest zainstalowany.
        """
        cmd = [sys.executable, "-m", "pip", "show", package_name]
        
        try:
            output = subprocess.check_output(cmd, text=True)
            for line in output.splitlines():
                if line.startswith("Version:"):
                    return line.split(":", 1)[1].strip()
            return None
        except subprocess.CalledProcessError:
            return None
    
    def get_package_dependencies(self, package_name: str, version: Optional[str] = None) -> List[str]:
        """
        Pobiera zależności pakietu.
        
        Args:
            package_name: Nazwa pakietu.
            version: Opcjonalna wersja pakietu.
            
        Returns:
            Lista zależności pakietu.
        """
        info = self.get_package_info(package_name, version)
        
        if "info" in info and "requires_dist" in info["info"]:
            return info["info"]["requires_dist"] or []
        
        return []


# Funkcje pomocnicze do użycia bez tworzenia instancji klasy

def search(query: str) -> List[Dict[str, Any]]:
    """
    Wyszukuje pakiety w PyPI.
    
    Args:
        query: Zapytanie do wyszukania.
        
    Returns:
        Lista pasujących pakietów.
    """
    registry = PyPIRegistry()
    return registry.search_package(query)

def install(package_name: str, version: Optional[str] = None, upgrade: bool = False, venv_path: Optional[str] = None) -> bool:
    """
    Instaluje pakiet z PyPI.
    
    Args:
        package_name: Nazwa pakietu do zainstalowania.
        version: Opcjonalna wersja pakietu.
        upgrade: Czy aktualizować pakiet, jeśli jest już zainstalowany.
        venv_path: Opcjonalna ścieżka do środowiska wirtualnego, w którym ma być zainstalowany pakiet.
        
    Returns:
        True, jeśli instalacja się powiodła, False w przeciwnym razie.
    """
    registry = PyPIRegistry()
    return registry.install_package(package_name, version, upgrade, venv_path=venv_path)

def get_info(package_name: str, version: Optional[str] = None) -> Dict[str, Any]:
    """
    Pobiera informacje o pakiecie z PyPI.
    
    Args:
        package_name: Nazwa pakietu.
        version: Opcjonalna wersja pakietu.
        
    Returns:
        Słownik z informacjami o pakiecie.
    """
    registry = PyPIRegistry()
    return registry.get_package_info(package_name, version)


if __name__ == "__main__":
    # Przykład użycia
    if len(sys.argv) > 1:
        query = sys.argv[1]
        print(f"Wyszukiwanie pakietów dla zapytania: {query}")
        results = search(query)
        for result in results[:5]:  # Wyświetl pierwsze 5 wyników
            print(f"- {result.get('name')} ({result.get('version')}): {result.get('description')}")
    else:
        print("Użycie: python pypi.py <zapytanie>")
