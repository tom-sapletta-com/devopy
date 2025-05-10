#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import yaml
from typing import Dict, List, Any, Optional

# Dodanie ścieżki do katalogu głównego projektu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import dekoratorów z devopy
from devopy.converters.docker_task import docker_task
from devopy.converters.restapi_task import restapi_task
from devopy.converters.text2python_decorator import text2python_task

# Funkcja pomocnicza do wczytywania konfiguracji z plików YAML
def load_docker_config(func_name: str) -> Dict[str, Any]:
    """Wczytuje konfigurację Docker z pliku YAML dla danej funkcji"""
    yaml_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docker', f'{func_name}.yml')
    
    if os.path.exists(yaml_path):
        with open(yaml_path, 'r') as f:
            try:
                service_def = yaml.safe_load(f)
                if 'service' in service_def:
                    return service_def['service']
            except Exception as e:
                print(f"Błąd podczas wczytywania pliku YAML dla {func_name}: {e}")
    
    return {}

# Przykład 1: Funkcja fetch_data z konfiguracją Docker z pliku YAML
@docker_task(image="python:3.9-slim", port=8001, env_vars={"API_KEY": "example_key"})
@restapi_task(route="/api/data", method="GET")
@text2python_task("Napisz funkcję, która pobiera dane z API")
def fetch_data_yaml(source: str, limit: int = 100) -> Dict[str, Any]:
    """
    Pobiera dane z zewnętrznego API na podstawie konfiguracji z pliku YAML
    
    Args:
        source: Źródło danych (URL API)
        limit: Maksymalna liczba rekordów do pobrania
        
    Returns:
        Słownik zawierający pobrane dane
    """
    config = load_docker_config("fetch_data")
    
    # Użyj konfiguracji z pliku YAML, jeśli jest dostępna
    api_key = os.environ.get("API_KEY", "default_key")
    max_requests = int(os.environ.get("MAX_REQUESTS", "100"))
    timeout = int(os.environ.get("TIMEOUT", "30"))
    
    print(f"[INFO] Pobieranie danych z {source} (limit: {limit})")
    print(f"[INFO] Używanie klucza API: {api_key}")
    print(f"[INFO] Max requests: {max_requests}")
    print(f"[INFO] Timeout: {timeout}s")
    
    # Symulacja pobierania danych
    data = {
        "source": source,
        "limit": limit,
        "records": [{"id": i, "value": f"record_{i}"} for i in range(limit)]
    }
    
    return data

# Przykład 2: Funkcja transform_data z konfiguracją Docker z pliku YAML
@docker_task(image="python:3.9-slim", port=8003, env_vars={"OUTPUT_FORMAT": "json"})
@restapi_task(route="/api/transform", method="POST")
@text2python_task("Napisz funkcję, która transformuje dane do określonego formatu")
def transform_data_yaml(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transformuje dane do określonego formatu na podstawie konfiguracji z pliku YAML
    
    Args:
        data: Dane wejściowe do transformacji
        
    Returns:
        Słownik zawierający przetransformowane dane
    """
    config = load_docker_config("transform_data")
    
    # Użyj konfiguracji z pliku YAML, jeśli jest dostępna
    output_format = os.environ.get("OUTPUT_FORMAT", "json")
    compression = os.environ.get("COMPRESSION", "true").lower() == "true"
    include_metadata = os.environ.get("INCLUDE_METADATA", "true").lower() == "true"
    
    print(f"[INFO] Transformacja danych do formatu: {output_format}")
    print(f"[INFO] Kompresja: {compression}")
    print(f"[INFO] Dołączanie metadanych: {include_metadata}")
    
    # Symulacja transformacji danych
    result = {
        "transformed_data": data,
        "format": output_format
    }
    
    if include_metadata:
        result["metadata"] = {
            "timestamp": "2025-05-10T17:30:00",
            "compression": compression,
            "source": "transform_data_yaml"
        }
    
    return result

# Przykład 3: Funkcja save_data z konfiguracją Docker z pliku YAML
@docker_task(image="python:3.9-slim", port=8004, env_vars={"DB_HOST": "database"})
@restapi_task(route="/api/save", method="POST")
@text2python_task("Napisz funkcję, która zapisuje dane do bazy danych")
def save_data_yaml(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Zapisuje dane do bazy danych na podstawie konfiguracji z pliku YAML
    
    Args:
        data: Dane do zapisania
        
    Returns:
        Słownik zawierający status operacji
    """
    config = load_docker_config("save_data")
    
    # Użyj konfiguracji z pliku YAML, jeśli jest dostępna
    db_host = os.environ.get("DB_HOST", "localhost")
    db_port = os.environ.get("DB_PORT", "5432")
    db_user = os.environ.get("DB_USER", "devopy")
    db_password = os.environ.get("DB_PASSWORD", "devopy123")
    db_name = os.environ.get("DB_NAME", "devopy_data")
    
    print(f"[INFO] Łączenie z bazą danych: {db_host}:{db_port}/{db_name}")
    print(f"[INFO] Użytkownik: {db_user}")
    print(f"[INFO] Zapisywanie danych...")
    
    # Symulacja zapisywania danych
    result = {
        "status": "success",
        "id": 12345,
        "timestamp": "2025-05-10T17:30:00",
        "database": f"{db_host}:{db_port}/{db_name}"
    }
    
    return result

# Przykład 4: Funkcja analyze_data z konfiguracją Docker z pliku YAML
@docker_task(image="python:3.9-slim", port=8005, env_vars={"ANALYSIS_TYPE": "statistical"})
@restapi_task(route="/api/analyze", method="POST")
@text2python_task("Napisz funkcję, która analizuje dane i generuje raport")
def analyze_data_yaml(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analizuje dane i generuje raport na podstawie konfiguracji z pliku YAML
    
    Args:
        data: Dane do analizy
        
    Returns:
        Słownik zawierający wyniki analizy
    """
    config = load_docker_config("analyze_data")
    
    # Użyj konfiguracji z pliku YAML, jeśli jest dostępna
    analysis_type = os.environ.get("ANALYSIS_TYPE", "statistical")
    generate_charts = os.environ.get("GENERATE_CHARTS", "true").lower() == "true"
    report_format = os.environ.get("REPORT_FORMAT", "html")
    email_report = os.environ.get("EMAIL_REPORT", "false").lower() == "true"
    
    print(f"[INFO] Typ analizy: {analysis_type}")
    print(f"[INFO] Generowanie wykresów: {generate_charts}")
    print(f"[INFO] Format raportu: {report_format}")
    print(f"[INFO] Wysyłanie raportu e-mailem: {email_report}")
    
    # Symulacja analizy danych
    result = {
        "analysis_results": {
            "type": analysis_type,
            "data_points": 100,
            "mean": 42.5,
            "median": 40.2,
            "std_dev": 5.7
        },
        "report_url": f"/reports/analysis_report.{report_format}",
        "charts_generated": generate_charts,
        "email_sent": email_report
    }
    
    return result

# Główna funkcja do testowania
if __name__ == "__main__":
    # Test funkcji fetch_data_yaml
    print("\n=== Test fetch_data_yaml ===")
    result = fetch_data_yaml("https://api.example.com/data", 5)
    print(f"Wynik: {result}")
    
    # Test funkcji transform_data_yaml
    print("\n=== Test transform_data_yaml ===")
    result = transform_data_yaml({"data": [1, 2, 3, 4, 5]})
    print(f"Wynik: {result}")
    
    # Test funkcji save_data_yaml
    print("\n=== Test save_data_yaml ===")
    result = save_data_yaml({"transformed_data": {"values": [1, 2, 3, 4, 5]}})
    print(f"Wynik: {result}")
    
    # Test funkcji analyze_data_yaml
    print("\n=== Test analyze_data_yaml ===")
    result = analyze_data_yaml({"saved_data": {"id": 123, "status": "success"}})
    print(f"Wynik: {result}")
