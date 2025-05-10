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
from flask import Flask, render_template, request, jsonify, Response, stream_with_context, send_from_directory

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

# Katalog na metadane
METADATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "metadata")
os.makedirs(METADATA_DIR, exist_ok=True)

# Katalog na środowiska wirtualne
VENV_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "venvs")
os.makedirs(VENV_BASE_DIR, exist_ok=True)

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

# Funkcja do wczytywania metadanych przykładów
def load_examples_metadata():
    """
    Wczytuje metadane wszystkich przykładów
    
    Returns:
        Dict: Metadane przykładów
    """
    metadata_path = os.path.join(METADATA_DIR, "examples_metadata.json")
    
    # Jeśli plik metadanych nie istnieje, spróbuj go wygenerować
    if not os.path.exists(metadata_path):
        try:
            # Importuj DevopyLauncher i wygeneruj metadane
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from devopy_launcher import DevopyLauncher
            launcher = DevopyLauncher()
            launcher.manager.export_metadata()
        except Exception as e:
            add_log(f"[ERROR] Nie udało się wygenerować metadanych przykładów: {str(e)}")
            return {"examples": {}, "categories": {}}
    
    # Wczytaj metadane z pliku
    try:
        with open(metadata_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        add_log(f"[ERROR] Nie udało się wczytać metadanych przykładów: {str(e)}")
        return {"examples": {}, "categories": {}}

# Funkcja do uruchamiania przykładu
def run_example(example_name, args=None):
    """
    Uruchamia przykład z automatycznie wygenerowanym środowiskiem wirtualnym
    
    Args:
        example_name: Nazwa przykładu
        args: Argumenty do przekazania
        
    Returns:
        str: Wynik wykonania
    """
    try:
        # Importuj DevopyLauncher i uruchom przykład
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from devopy_launcher import DevopyLauncher
        launcher = DevopyLauncher()
        
        process = launcher.run_example(example_name, args)
        
        if process:
            add_log(f"[INFO] Uruchomiono przykład {example_name}")
            return f"Uruchomiono przykład {example_name}"
        else:
            add_log(f"[ERROR] Nie udało się uruchomić przykładu {example_name}")
            return f"Nie udało się uruchomić przykładu {example_name}"
    except Exception as e:
        add_log(f"[ERROR] Błąd podczas uruchamiania przykładu {example_name}: {str(e)}")
        return f"Błąd: {str(e)}"

# Aplikacja Flask
app = Flask(__name__, static_folder=STATIC_DIR, template_folder=STATIC_DIR)

# Globals
current_process = None
examples_metadata = None

# Initialize examples metadata
def init_examples_metadata():
    global examples_metadata
    examples_metadata = load_examples_metadata()
    
    # If no metadata exists, discover examples and create metadata
    if not examples_metadata or not examples_metadata.get('examples'):
        print("Discovering examples and creating metadata...")
        examples = discover_examples()
        examples_metadata = {
            'examples': {},
            'categories': {}
        }
        
        for example_name, example_path in examples.items():
            metadata = get_example_metadata(example_path)
            if metadata:
                examples_metadata['examples'][example_name] = metadata
                
                # Add to category
                category = metadata.get('category', 'Uncategorized')
                if category not in examples_metadata['categories']:
                    examples_metadata['categories'][category] = []
                examples_metadata['categories'][category].append(example_name)
    
    return examples_metadata

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/matrix')
def matrix():
    return render_template('matrix.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(STATIC_DIR, path)

@app.route('/api/generate', methods=['POST'])
def generate_code():
    data = request.json
    prompt = data.get('prompt', '')
    
    # Placeholder for actual code generation
    generated_code = f"# Generated from: {prompt}\n\ndef example_function():\n    \"\"\"{prompt}\"\"\"\n    # TODO: Implement the function\n    print(\"Function called: {prompt}\")\n    return True"
    
    return jsonify({'code': generated_code})

@app.route('/api/run', methods=['POST'])
def run_code():
    global current_process
    
    data = request.json
    code = data.get('code', '')
    
    # Save code to a temporary file
    with open('temp_code.py', 'w') as f:
        f.write(code)
    
    # Run the code
    try:
        # Kill previous process if exists
        if current_process and current_process.poll() is None:
            current_process.terminate()
            time.sleep(0.5)
        
        # Start new process
        current_process = subprocess.Popen(
            [sys.executable, 'temp_code.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Start threads to read output
        def read_output(stream, prefix):
            for line in stream:
                log_queue.put(f"{prefix}: {line.strip()}")
            
        threading.Thread(target=read_output, args=(current_process.stdout, "OUT"), daemon=True).start()
        threading.Thread(target=read_output, args=(current_process.stderr, "ERR"), daemon=True).start()
        
        return jsonify({'status': 'running'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/logs')
def get_logs():
    logs = []
    while not log_queue.empty():
        try:
            logs.append(log_queue.get_nowait())
        except queue.Empty:
            break
    
    return jsonify({'logs': logs})

@app.route('/api/execute', methods=['POST'])
def execute_command():
    data = request.json
    command = data.get('command', '')
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
        
        output = result.stdout
        error = result.stderr
        
        return jsonify({
            'output': output,
            'error': error,
            'exitCode': result.returncode
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/save', methods=['POST'])
def save_code():
    data = request.json
    code = data.get('code', '')
    filename = data.get('filename', 'saved_code.py')
    
    try:
        with open(filename, 'w') as f:
            f.write(code)
        return jsonify({'status': 'saved', 'filename': filename})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/functions')
def get_functions():
    # Placeholder for actual function list
    functions = [
        {'id': 1, 'name': 'example_function', 'description': 'An example function'},
        {'id': 2, 'name': 'another_function', 'description': 'Another example function'}
    ]
    
    return jsonify({'functions': functions})

# New API endpoints for the example loading system
@app.route('/examples')
def get_examples():
    """Return the list of available examples with their metadata"""
    global examples_metadata
    
    # Make sure examples metadata is initialized
    if examples_metadata is None:
        init_examples_metadata()
    
    return jsonify(examples_metadata)

@app.route('/run-example', methods=['POST'])
def api_run_example():
    """Run a specified example"""
    data = request.json
    example_name = data.get('name')
    args = data.get('args', [])
    
    if not example_name:
        return jsonify({'error': 'Example name is required'})
    
    try:
        # Get the example metadata
        global examples_metadata
        if examples_metadata is None:
            init_examples_metadata()
        
        if example_name not in examples_metadata.get('examples', {}):
            return jsonify({'error': f'Example {example_name} not found'})
        
        # Run the example
        result = run_example(example_name, args)
        return jsonify({'result': f'Example {example_name} executed successfully', 'output': result})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/example-code/<path:example_name>')
def get_example_code(example_name):
    """Return the code of a specified example"""
    global examples_metadata
    
    # Make sure examples metadata is initialized
    if examples_metadata is None:
        init_examples_metadata()
    
    if example_name not in examples_metadata.get('examples', {}):
        return jsonify({'error': f'Example {example_name} not found'})
    
    example_path = examples_metadata['examples'][example_name]['path']
    
    try:
        with open(example_path, 'r') as f:
            code = f.read()
        return jsonify({'code': code})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    # Initialize examples metadata
    init_examples_metadata()
    
    # Start the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
