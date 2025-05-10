#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demonstracja użycia przeniesionych modułów z projektu evopy do devopy

Ten skrypt pokazuje, jak korzystać z następujących modułów:
1. Menedżer zależności (dependency_manager)
2. Konwerter tekstu na kod (text2python)
3. Piaskownica Docker (docker_sandbox)
"""

import os
import sys
import json
from pathlib import Path

# Dodaj ścieżkę do katalogu głównego projektu
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Importy z modułu menedżera zależności
from devopy.utils.dependency_manager import (
    DependencyManager,
    fix_code_dependencies,
    install_missing_packages
)

# Importy z modułu konwertera tekstu na kod
from devopy.converters.text2python import (
    Text2Python,
    convert_text_to_python,
    explain_python_code,
    improve_python_code
)

# Importy z modułu piaskownicy Docker
from devopy.sandbox.docker_sandbox import (
    DockerSandbox,
    run_code_in_sandbox,
    run_service_in_sandbox,
    stop_sandbox_service,
    check_docker_available
)


def demo_dependency_manager():
    """Demonstracja użycia menedżera zależności"""
    print("\n=== Demonstracja menedżera zależności ===\n")
    
    # Przykładowy kod z brakującymi importami
    code = """
def analyze_data(data):
    # Oblicz podstawowe statystyki
    mean_value = np.mean(data)
    median_value = np.median(data)
    std_value = np.std(data)
    
    # Stwórz wykres
    plt.figure(figsize=(10, 6))
    plt.hist(data, bins=20, alpha=0.7)
    plt.axvline(mean_value, color='r', linestyle='--', label=f'Średnia: {mean_value:.2f}')
    plt.axvline(median_value, color='g', linestyle='--', label=f'Mediana: {median_value:.2f}')
    plt.legend()
    plt.title('Rozkład danych')
    plt.savefig('histogram.png')
    
    return {
        'mean': mean_value,
        'median': median_value,
        'std': std_value
    }
"""
    
    print("Oryginalny kod:")
    print(code)
    
    # Napraw brakujące importy
    fixed_code = fix_code_dependencies(code)
    
    print("\nKod z dodanymi importami:")
    print(fixed_code)
    
    # Utwórz instancję menedżera zależności
    manager = DependencyManager()
    
    # Analizuj kod
    used_modules = manager.analyze_code(code)
    
    print("\nWykryte moduły:")
    for module in sorted(used_modules):
        print(f"- {module}")
    
    print("\nMenedżer zależności może również automatycznie instalować brakujące pakiety.")
    print("Przykład: install_missing_packages(code)")


def demo_text2python():
    """Demonstracja użycia konwertera tekstu na kod"""
    print("\n=== Demonstracja konwertera tekstu na kod ===\n")
    
    # Sprawdź, czy Ollama jest dostępne
    try:
        import subprocess
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        ollama_available = result.returncode == 0
    except:
        ollama_available = False
    
    if not ollama_available:
        print("Uwaga: Ollama nie jest dostępne. Demonstracja będzie symulowana.")
        
        # Symulowane wyniki
        generated_code = """
def execute(n):
    # Oblicza n-ty wyraz ciągu Fibonacciego
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
"""
        explanation = "Ta funkcja oblicza n-ty wyraz ciągu Fibonacciego używając iteracyjnego podejścia, które jest bardziej wydajne niż rekurencja."
        improved_code = """
def execute(n):
    # Oblicza n-ty wyraz ciągu Fibonacciego
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
"""
    else:
        # Przykład konwersji tekstu na kod
        prompt = "Napisz funkcję, która oblicza n-ty wyraz ciągu Fibonacciego"
        print(f"Prompt: {prompt}")
        
        generated_code = convert_text_to_python(prompt)
        
        # Przykład wyjaśnienia kodu
        code_to_explain = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        explanation = explain_python_code(code_to_explain)
        
        # Przykład ulepszania kodu
        improved_code = improve_python_code(code_to_explain)
    
    print("\nWygenerowany kod:")
    print(generated_code)
    
    print("\nWyjaśnienie kodu:")
    print(explanation)
    
    print("\nUlepszony kod:")
    print(improved_code)
    
    print("\nKonwerter tekstu na kod może również generować kod na podstawie bardziej złożonych opisów.")
    print("Przykład: convert_text_to_python('Napisz funkcję, która analizuje plik CSV i generuje wykres')")


def demo_docker_sandbox():
    """Demonstracja użycia piaskownicy Docker"""
    print("\n=== Demonstracja piaskownicy Docker ===\n")
    
    # Sprawdź, czy Docker jest dostępny
    available, message = check_docker_available()
    
    if not available:
        print(f"Docker nie jest dostępny: {message}")
        print("Demonstracja będzie symulowana.")
        
        # Symulowane wyniki
        run_result = {
            "success": True,
            "output": "Hello from Docker Sandbox!",
            "error": "",
            "execution_time": 0.1,
            "container_name": "devopy-sandbox-12345678",
            "sandbox_id": "12345678"
        }
        
        service_result = {
            "success": True,
            "container_id": "container-id",
            "container_name": "devopy-service-12345678",
            "sandbox_id": "12345678",
            "port": 8000,
            "url": "http://localhost:8000",
            "message": "Usługa uruchomiona w kontenerze devopy-service-12345678"
        }
    else:
        print(f"Docker jest dostępny: {message}")
        
        # Przykładowy kod do uruchomienia w piaskownicy
        code = """
import numpy as np
import matplotlib.pyplot as plt

# Generuj dane
data = np.random.normal(0, 1, 1000)

# Oblicz statystyki
mean_value = np.mean(data)
median_value = np.median(data)
std_value = np.std(data)

# Wyświetl wyniki
print(f"Średnia: {mean_value:.4f}")
print(f"Mediana: {median_value:.4f}")
print(f"Odchylenie standardowe: {std_value:.4f}")

# Zwróć wyniki
result = {
    'mean': float(mean_value),
    'median': float(median_value),
    'std': float(std_value)
}
"""
        
        print("\nUruchamianie kodu w piaskownicy Docker:")
        print(code)
        
        # Uruchom kod w piaskownicy
        run_result = run_code_in_sandbox(code, timeout=10)
        
        # Przykładowy kod usługi
        service_code = """
from flask import Flask, jsonify
import random

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Docker Sandbox Service!"

@app.route('/random')
def random_number():
    return jsonify({'number': random.randint(1, 100)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
"""
        
        print("\nUruchamianie usługi w piaskownicy Docker:")
        print(service_code)
        
        # Uruchom usługę w piaskownicy
        service_result = run_service_in_sandbox(service_code, port=8000)
    
    print("\nWynik uruchomienia kodu:")
    print(json.dumps(run_result, indent=2))
    
    print("\nWynik uruchomienia usługi:")
    print(json.dumps(service_result, indent=2))
    
    if available and service_result.get("success"):
        print(f"\nUsługa jest dostępna pod adresem: {service_result.get('url')}")
        print(f"Aby zatrzymać usługę, użyj: stop_sandbox_service('{service_result.get('container_name')}')")
    
    print("\nPiaskownica Docker umożliwia bezpieczne uruchamianie kodu i usług w izolowanym środowisku.")
    print("Przykład: run_code_in_sandbox('print(\"Hello, World!\")')")


def main():
    """Główna funkcja demonstracyjna"""
    print("=== Demonstracja przeniesionych modułów z projektu evopy do devopy ===")
    
    # Demonstracja menedżera zależności
    demo_dependency_manager()
    
    # Demonstracja konwertera tekstu na kod
    demo_text2python()
    
    # Demonstracja piaskownicy Docker
    demo_docker_sandbox()
    
    print("\n=== Koniec demonstracji ===")


if __name__ == "__main__":
    main()
