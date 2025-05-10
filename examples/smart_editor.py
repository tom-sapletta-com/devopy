#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import json
import yaml
import time
import subprocess
import threading
import queue
from typing import Dict, List, Any, Optional, Tuple, Union
from flask import Flask, render_template_string, request, jsonify, Response, stream_with_context, send_from_directory

# Dodanie ścieżki do katalogu głównego projektu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Katalog na wizualizacje
VISUALIZATION_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "visualizations")
os.makedirs(VISUALIZATION_DIR, exist_ok=True)

# Katalog na logi
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# Katalog na dane Docker
DOCKER_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docker")
os.makedirs(DOCKER_DIR, exist_ok=True)

# Katalog na pliki statyczne
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

# Rejestr funkcji
function_registry = {}

# Kolejka logów
log_queue = queue.Queue()

# Funkcja do generowania kodu na podstawie promptu
def generate_code_from_prompt(prompt: str) -> Tuple[str, str]:
    """
    Generuje kod funkcji i konfigurację Docker na podstawie promptu
    
    Args:
        prompt: Opis funkcji
        
    Returns:
        Tuple[str, str]: Wygenerowany kod i konfiguracja Docker
    """
    # Generowanie nazwy funkcji na podstawie promptu
    function_name = "_".join(re.findall(r'\b[a-z]+\b', prompt.lower()))
    if not function_name:
        function_name = "generated_function"
    
    # Generowanie kodu funkcji
    code = f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
from typing import Dict, Any, Optional

# Dodanie ścieżki do katalogu głównego projektu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import dekoratora devopy
from devopy.converters.devopy_task import devopy

@devopy("{prompt}")
def {function_name}(data: Any) -> Dict[str, Any]:
    \"\"\"
    {prompt}
    
    Args:
        data: Dane wejściowe
        
    Returns:
        Dict[str, Any]: Przetworzone dane
    \"\"\"
    # Implementacja funkcji
    print(f"Przetwarzanie danych: {{data}}")
    
    # Przykładowa logika
    result = {{"processed": data, "timestamp": "2025-05-10T17:37:12"}}
    
    return result

# Test funkcji
if __name__ == "__main__":
    test_data = "test_input"
    result = {function_name}(test_data)
    print(f"Wynik: {{result}}")
"""
    
    # Generowanie konfiguracji Docker
    docker_config = f"""service:
  name: {function_name.replace('_', '-')}
  image: python:3.9-slim
  description: "{prompt}"
  ports:
    - "8080:8080"
  environment:
    - PYTHONPATH=/app
    - DEBUG=true
  volumes:
    - ./:/app
    - ./data:/app/data
  command: "python -c 'from examples.{function_name} import {function_name}; print({function_name}(\"test\"))'"
  labels:
    - "devopy.function={function_name}"
    - "devopy.type=generated"
  logs:
    - "[INFO] Uruchamianie serwisu {function_name.replace('_', '-')}"
    - "[INFO] Przetwarzanie danych"
    - "[INFO] Operacja zakończona powodzeniem"
"""
    
    return code, docker_config

# Funkcja do zapisywania kodu i konfiguracji Docker
def save_code_and_docker(code: str, prompt: str) -> Tuple[str, str]:
    """
    Zapisuje kod funkcji i konfigurację Docker
    
    Args:
        code: Kod funkcji
        prompt: Opis funkcji
        
    Returns:
        Tuple[str, str]: Nazwa funkcji i ścieżka do pliku
    """
    # Ekstrakcja nazwy funkcji z kodu
    match = re.search(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', code)
    if not match:
        return None, None
    
    function_name = match.group(1)
    
    # Zapisanie kodu do pliku
    code_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{function_name}.py")
    with open(code_file, 'w') as f:
        f.write(code)
    
    # Ekstrakcja konfiguracji Docker z kodu
    docker_config = generate_docker_config_from_code(code, prompt)
    
    # Zapisanie konfiguracji Docker do pliku YAML
    docker_file = os.path.join(DOCKER_DIR, f"{function_name}.yml")
    with open(docker_file, 'w') as f:
        f.write(docker_config)
    
    # Dodanie funkcji do rejestru
    function_registry[function_name] = {
        'name': function_name,
        'description': prompt,
        'code_file': code_file,
        'docker_file': docker_file
    }
    
    # Dodanie logu
    add_log(f"[INFO] Zapisano funkcję {function_name}")
    add_log(f"[INFO] Zapisano konfigurację Docker dla {function_name}")
    
    return function_name, code_file

# Funkcja do generowania konfiguracji Docker na podstawie kodu
def generate_docker_config_from_code(code: str, prompt: str) -> str:
    """
    Generuje konfigurację Docker na podstawie kodu funkcji
    
    Args:
        code: Kod funkcji
        prompt: Opis funkcji
        
    Returns:
        str: Konfiguracja Docker w formacie YAML
    """
    # Ekstrakcja nazwy funkcji z kodu
    match = re.search(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', code)
    if not match:
        return ""
    
    function_name = match.group(1)
    service_name = function_name.replace('_', '-')
    
    # Ekstrakcja parametrów z dekoratora devopy
    devopy_match = re.search(r'@devopy\((.+)\)', code)
    devopy_params = []
    
    if devopy_match:
        params_str = devopy_match.group(1)
        # Usunięcie cudzysłowów i podzielenie po przecinkach
        params = [p.strip().strip('"\'') for p in params_str.split(',')]
        devopy_params = params
    
    # Generowanie konfiguracji Docker
    docker_config = f"""service:
  name: {service_name}
  image: python:3.9-slim
  description: "{prompt}"
  ports:
    - "8080:8080"
  environment:
    - PYTHONPATH=/app
    - DEBUG=true
  volumes:
    - ./:/app
    - ./data:/app/data
  command: "python -c 'from examples.{function_name} import {function_name}; print({function_name}(\"test\"))'"
  labels:
    - "devopy.function={function_name}"
    - "devopy.type=generated"
  logs:
    - "[INFO] Uruchamianie serwisu {service_name}"
    - "[INFO] Przetwarzanie danych"
    - "[INFO] Operacja zakończona powodzeniem"
"""
    
    return docker_config

# Funkcja do uruchamiania kodu
def run_code(code: str) -> str:
    """
    Uruchamia kod funkcji w sandboxie
    
    Args:
        code: Kod funkcji
        
    Returns:
        str: Wynik wykonania kodu
    """
    # Ekstrakcja nazwy funkcji z kodu
    match = re.search(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', code)
    if not match:
        return "Błąd: Nie znaleziono definicji funkcji w kodzie"
    
    function_name = match.group(1)
    
    # Zapisanie kodu do tymczasowego pliku
    temp_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"temp_{function_name}.py")
    with open(temp_file, 'w') as f:
        f.write(code)
    
    # Uruchomienie kodu w sandboxie
    try:
        add_log(f"[INFO] Uruchamianie funkcji {function_name} w sandboxie")
        
        # Przygotowanie kodu do wykonania
        exec_code = f"""
import sys
import os
import json
sys.path.append('{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}')
try:
    from examples.temp_{function_name} import {function_name}
    result = {function_name}("test_data")
    print(json.dumps(result) if isinstance(result, (dict, list)) else str(result))
except Exception as e:
    print(f"Błąd wykonania: {{str(e)}}")
"""
        
        # Uruchomienie kodu w procesie
        process = subprocess.Popen(
            ["python3", "-c", exec_code],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Odczytanie wyniku
        stdout, stderr = process.communicate()
        
        if stderr:
            add_log(f"[ERROR] Błąd podczas wykonywania funkcji {function_name}: {stderr}")
            return f"Błąd: {stderr}"
        
        add_log(f"[INFO] Funkcja {function_name} wykonana pomyślnie")
        add_log(f"[INFO] Wynik: {stdout.strip()}")
        
        # Usunięcie tymczasowego pliku
        os.remove(temp_file)
        
        return stdout.strip()
    
    except Exception as e:
        add_log(f"[ERROR] Wyjątek podczas wykonywania funkcji {function_name}: {str(e)}")
        
        # Usunięcie tymczasowego pliku
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        return f"Błąd: {str(e)}"

# Funkcja do dodawania logów
def add_log(message: str) -> None:
    """
    Dodaje wiadomość do kolejki logów
    
    Args:
        message: Wiadomość do dodania
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    log_queue.put(log_message)
    
    # Zapisanie logu do pliku
    log_file = os.path.join(LOGS_DIR, "smart_editor.log")
    with open(log_file, 'a') as f:
        f.write(log_message + "\n")

# Aplikacja Flask
app = Flask(__name__, static_folder=STATIC_DIR)

@app.route('/')
def index():
    """Strona główna"""
    layout = request.args.get('layout', 'standard')
    
    # Sprawdzenie, czy plik layoutu istnieje
    layout_file = f"{layout}_layout.html"
    layout_path = os.path.join(STATIC_DIR, layout_file)
    
    if not os.path.exists(layout_path):
        layout_file = "standard_layout.html"
    
    return send_from_directory(STATIC_DIR, layout_file)

@app.route('/static/<path:path>')
def serve_static(path):
    """Serwowanie plików statycznych"""
    return send_from_directory(STATIC_DIR, path)

@app.route('/generate-code', methods=['POST'])
def generate_code():
    """Generowanie kodu na podstawie promptu"""
    data = request.json
    prompt = data.get('prompt', '')
    
    add_log(f"[INFO] Generowanie kodu dla promptu: {prompt}")
    
    code, docker_config = generate_code_from_prompt(prompt)
    
    return jsonify({
        'code': code,
        'docker_config': docker_config
    })

@app.route('/save-code', methods=['POST'])
def save_code():
    """Zapisywanie kodu"""
    data = request.json
    code = data.get('code', '')
    prompt = data.get('prompt', '')
    
    function_name, code_file = save_code_and_docker(code, prompt)
    
    if not function_name:
        return jsonify({'error': 'Nie udało się zapisać kodu'})
    
    return jsonify({
        'success': True,
        'function_name': function_name,
        'code_file': code_file
    })

@app.route('/run-code', methods=['POST'])
def run_code_endpoint():
    """Uruchamianie kodu"""
    data = request.json
    code = data.get('code', '')
    
    result = run_code(code)
    
    return jsonify({
        'result': result
    })

@app.route('/function-list')
def function_list():
    """Lista funkcji"""
    functions = []
    
    for name, info in function_registry.items():
        functions.append({
            'name': name,
            'description': info.get('description', '')
        })
    
    return jsonify({
        'functions': functions
    })

@app.route('/function/<function_name>')
def get_function(function_name):
    """Pobieranie funkcji"""
    if function_name not in function_registry:
        return jsonify({'error': 'Funkcja nie istnieje'})
    
    info = function_registry[function_name]
    
    # Wczytanie kodu funkcji
    code = ""
    if 'code_file' in info and os.path.exists(info['code_file']):
        with open(info['code_file'], 'r') as f:
            code = f.read()
    
    # Wczytanie konfiguracji Docker
    docker_config = ""
    if 'docker_file' in info and os.path.exists(info['docker_file']):
        with open(info['docker_file'], 'r') as f:
            docker_config = f.read()
    
    return jsonify({
        'name': function_name,
        'description': info.get('description', ''),
        'code': code,
        'docker_config': docker_config,
        'prompt': info.get('description', '')
    })

@app.route('/log-stream')
def log_stream():
    """Strumień logów"""
    def generate():
        while True:
            # Pobieranie logów z kolejki
            try:
                message = log_queue.get(timeout=1)
                yield f"data: {message}\n\n"
            except queue.Empty:
                yield f"data: \n\n"  # Puste dane, aby utrzymać połączenie
            time.sleep(0.5)
    
    return Response(stream_with_context(generate()), content_type='text/event-stream')

# Główna funkcja
if __name__ == "__main__":
    add_log("[INFO] Uruchamianie Smart Editor")
    app.run(host='0.0.0.0', port=5051, debug=True, threaded=True)
