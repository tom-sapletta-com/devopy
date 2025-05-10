#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
from typing import Dict, List, Any, Optional

# Dodanie ścieżki do katalogu głównego projektu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import dekoratora devopy
from devopy.converters.devopy_task import devopy

@devopy("Pobierz dane z API i przekształć je do formatu JSON")
def fetch_and_transform(url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Pobiera dane z API i przekształca je do formatu JSON
    
    Args:
        url: URL API
        params: Parametry zapytania
        
    Returns:
        Dict[str, Any]: Dane w formacie JSON
    """
    print(f"[INFO] Pobieranie danych z {url}")
    
    # Symulacja pobierania danych
    if params:
        print(f"[INFO] Parametry: {params}")
    
    # Symulacja danych z API
    data = {
        "items": [
            {"id": 1, "name": "Item 1", "value": 100},
            {"id": 2, "name": "Item 2", "value": 200},
            {"id": 3, "name": "Item 3", "value": 300}
        ],
        "metadata": {
            "count": 3,
            "timestamp": "2025-05-10T17:37:12+02:00"
        }
    }
    
    print("[INFO] Dane pobrane pomyślnie")
    
    return data

@devopy("Filtruj dane według określonych kryteriów", image="python:3.9-alpine", port=8081)
def filter_data(data: Dict[str, Any], criteria: Dict[str, Any]) -> Dict[str, Any]:
    """
    Filtruje dane według określonych kryteriów
    
    Args:
        data: Dane wejściowe
        criteria: Kryteria filtrowania
        
    Returns:
        Dict[str, Any]: Przefiltrowane dane
    """
    print(f"[INFO] Filtrowanie danych według kryteriów: {criteria}")
    
    # Symulacja filtrowania danych
    filtered_items = []
    
    for item in data.get("items", []):
        match = True
        for key, value in criteria.items():
            if key in item and item[key] != value:
                match = False
                break
        
        if match:
            filtered_items.append(item)
    
    # Przygotowanie wyniku
    result = {
        "items": filtered_items,
        "metadata": {
            "count": len(filtered_items),
            "original_count": len(data.get("items", [])),
            "timestamp": data.get("metadata", {}).get("timestamp", "")
        }
    }
    
    print(f"[INFO] Przefiltrowano dane: {len(filtered_items)} z {len(data.get('items', []))}")
    
    return result

@devopy("Analizuj dane i generuj raport statystyczny", 
        image="python:3.9-slim", 
        port=8082, 
        env_vars={"REPORT_FORMAT": "json", "INCLUDE_CHARTS": "true"})
def analyze_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analizuje dane i generuje raport statystyczny
    
    Args:
        data: Dane do analizy
        
    Returns:
        Dict[str, Any]: Raport statystyczny
    """
    print("[INFO] Analizowanie danych")
    
    items = data.get("items", [])
    
    # Symulacja analizy danych
    if not items:
        return {"error": "Brak danych do analizy"}
    
    # Obliczanie statystyk
    values = [item.get("value", 0) for item in items]
    avg_value = sum(values) / len(values) if values else 0
    max_value = max(values) if values else 0
    min_value = min(values) if values else 0
    
    # Przygotowanie raportu
    report = {
        "statistics": {
            "count": len(items),
            "average_value": avg_value,
            "max_value": max_value,
            "min_value": min_value,
            "sum": sum(values)
        },
        "metadata": {
            "timestamp": data.get("metadata", {}).get("timestamp", ""),
            "report_format": os.environ.get("REPORT_FORMAT", "json"),
            "include_charts": os.environ.get("INCLUDE_CHARTS", "true") == "true"
        }
    }
    
    print("[INFO] Analiza zakończona pomyślnie")
    
    return report

@devopy("Zapisz dane do bazy danych i zwróć identyfikator", 
        image="python:3.9-slim", 
        port=8083, 
        env_vars={"DB_HOST": "database", "DB_PORT": "5432", "DB_NAME": "devopy_data"})
def save_to_database(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Zapisuje dane do bazy danych i zwraca identyfikator
    
    Args:
        data: Dane do zapisania
        
    Returns:
        Dict[str, Any]: Status operacji i identyfikator
    """
    print("[INFO] Zapisywanie danych do bazy")
    
    # Symulacja zapisywania do bazy danych
    db_host = os.environ.get("DB_HOST", "localhost")
    db_port = os.environ.get("DB_PORT", "5432")
    db_name = os.environ.get("DB_NAME", "devopy_data")
    
    print(f"[INFO] Łączenie z bazą danych: {db_host}:{db_port}/{db_name}")
    
    # Symulacja generowania ID
    record_id = 12345
    
    # Przygotowanie wyniku
    result = {
        "status": "success",
        "record_id": record_id,
        "database": f"{db_host}:{db_port}/{db_name}",
        "timestamp": "2025-05-10T17:37:12+02:00"
    }
    
    print(f"[INFO] Dane zapisane pomyślnie, ID: {record_id}")
    
    return result

# Główna funkcja do testowania
if __name__ == "__main__":
    # Test funkcji fetch_and_transform
    print("\n=== Test fetch_and_transform ===")
    data = fetch_and_transform("https://api.example.com/data", {"limit": 10})
    print(f"Wynik: {json.dumps(data, indent=2)}")
    
    # Test funkcji filter_data
    print("\n=== Test filter_data ===")
    filtered_data = filter_data(data, {"value": 200})
    print(f"Wynik: {json.dumps(filtered_data, indent=2)}")
    
    # Test funkcji analyze_data
    print("\n=== Test analyze_data ===")
    report = analyze_data(filtered_data)
    print(f"Wynik: {json.dumps(report, indent=2)}")
    
    # Test funkcji save_to_database
    print("\n=== Test save_to_database ===")
    save_result = save_to_database(report)
    print(f"Wynik: {json.dumps(save_result, indent=2)}")
