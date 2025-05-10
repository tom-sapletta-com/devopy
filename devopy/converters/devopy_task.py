#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import inspect
import functools
import yaml
import json
from typing import Dict, List, Any, Optional, Union, Callable

# Rejestr funkcji z dekoratorem devopy
devopy_registry = {}

def devopy(prompt: str, *args, **kwargs):
    """
    Dekorator devopy do automatycznego generowania kodu i konfiguracji Docker
    
    Args:
        prompt: Opis funkcji w języku naturalnym
        *args: Dodatkowe parametry dla dekoratora
        **kwargs: Dodatkowe parametry dla dekoratora
    
    Returns:
        Udekorowana funkcja
    """
    def decorator(func):
        # Pobierz informacje o funkcji
        func_name = func.__name__
        func_module = func.__module__
        func_doc = func.__doc__ or ""
        func_source = inspect.getsource(func)
        func_signature = str(inspect.signature(func))
        
        # Zapisz informacje o funkcji w rejestrze
        devopy_registry[func_name] = {
            'name': func_name,
            'module': func_module,
            'doc': func_doc,
            'source': func_source,
            'signature': func_signature,
            'prompt': prompt,
            'args': args,
            'kwargs': kwargs
        }
        
        # Generuj konfigurację Docker
        docker_config = generate_docker_config(func_name, prompt, args, kwargs)
        
        # Zapisz konfigurację Docker do pliku YAML
        docker_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'docker')
        os.makedirs(docker_dir, exist_ok=True)
        docker_file = os.path.join(docker_dir, f"{func_name}.yml")
        
        with open(docker_file, 'w') as f:
            f.write(docker_config)
        
        # Dodaj atrybuty do funkcji
        func.__devopy__ = {
            'prompt': prompt,
            'args': args,
            'kwargs': kwargs,
            'docker_file': docker_file
        }
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Logowanie wywołania funkcji
            print(f"[DEVOPY] Wywołanie funkcji {func_name} z promptem: {prompt}")
            
            # Wywołanie oryginalnej funkcji
            result = func(*args, **kwargs)
            
            # Logowanie wyniku
            print(f"[DEVOPY] Funkcja {func_name} zakończona")
            
            return result
        
        return wrapper
    
    return decorator

def generate_docker_config(func_name: str, prompt: str, args: tuple, kwargs: dict) -> str:
    """
    Generuje konfigurację Docker dla funkcji
    
    Args:
        func_name: Nazwa funkcji
        prompt: Opis funkcji
        args: Dodatkowe parametry dla dekoratora
        kwargs: Dodatkowe parametry dla dekoratora
    
    Returns:
        str: Konfiguracja Docker w formacie YAML
    """
    service_name = func_name.replace('_', '-')
    
    # Domyślne wartości
    image = kwargs.get('image', 'python:3.9-slim')
    port = kwargs.get('port', 8080)
    env_vars = kwargs.get('env_vars', {})
    volumes = kwargs.get('volumes', ['./:/app', './data:/app/data'])
    
    # Dodatkowe parametry z args
    for arg in args:
        if arg.startswith('image='):
            image = arg.split('=')[1]
        elif arg.startswith('port='):
            port = int(arg.split('=')[1])
    
    # Generowanie konfiguracji Docker
    docker_config = f"""service:
  name: {service_name}
  image: {image}
  description: "{prompt}"
  ports:
    - "{port}:{port}"
  environment:
"""
    
    # Dodanie zmiennych środowiskowych
    for key, value in env_vars.items():
        docker_config += f"    - {key}={value}\n"
    
    # Dodanie domyślnych zmiennych środowiskowych
    if 'PYTHONPATH' not in env_vars:
        docker_config += "    - PYTHONPATH=/app\n"
    if 'DEBUG' not in env_vars:
        docker_config += "    - DEBUG=true\n"
    
    # Dodanie woluminów
    docker_config += "  volumes:\n"
    for volume in volumes:
        docker_config += f"    - {volume}\n"
    
    # Dodanie komendy
    docker_config += f"""  command: "python -c 'from {func_name.split('.')[0] if '.' in func_name else 'examples'}.{func_name.split('.')[-1] if '.' in func_name else func_name} import {func_name.split('.')[-1] if '.' in func_name else func_name}; print({func_name.split('.')[-1] if '.' in func_name else func_name}(\"test\"))'"
  labels:
    - "devopy.function={func_name}"
    - "devopy.type=generated"
  logs:
    - "[INFO] Uruchamianie serwisu {service_name}"
    - "[INFO] Przetwarzanie danych"
    - "[INFO] Operacja zakończona powodzeniem"
"""
    
    return docker_config

# Funkcja do pobierania wszystkich funkcji z dekoratorem devopy
def get_all_devopy_functions() -> Dict[str, Dict[str, Any]]:
    """
    Pobiera wszystkie funkcje z dekoratorem devopy
    
    Returns:
        Dict[str, Dict[str, Any]]: Słownik z informacjami o funkcjach
    """
    return devopy_registry

# Funkcja do pobierania konfiguracji Docker dla funkcji
def get_docker_config(func_name: str) -> str:
    """
    Pobiera konfigurację Docker dla funkcji
    
    Args:
        func_name: Nazwa funkcji
    
    Returns:
        str: Konfiguracja Docker w formacie YAML
    """
    if func_name not in devopy_registry:
        return ""
    
    func_info = devopy_registry[func_name]
    docker_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'docker', f"{func_name}.yml")
    
    if os.path.exists(docker_file):
        with open(docker_file, 'r') as f:
            return f.read()
    
    # Jeśli plik nie istnieje, wygeneruj konfigurację
    return generate_docker_config(
        func_name,
        func_info['prompt'],
        func_info['args'],
        func_info['kwargs']
    )

# Funkcja do uruchamiania funkcji w sandboxie
def run_in_sandbox(func_name: str, *args, **kwargs) -> Any:
    """
    Uruchamia funkcję w sandboxie
    
    Args:
        func_name: Nazwa funkcji
        *args: Argumenty dla funkcji
        **kwargs: Argumenty nazwane dla funkcji
    
    Returns:
        Any: Wynik wywołania funkcji
    """
    if func_name not in devopy_registry:
        raise ValueError(f"Funkcja {func_name} nie istnieje w rejestrze devopy")
    
    func_info = devopy_registry[func_name]
    module_name = func_info['module']
    
    # Importuj moduł i funkcję
    module = __import__(module_name, fromlist=[func_name])
    func = getattr(module, func_name)
    
    # Wywołaj funkcję
    return func(*args, **kwargs)
