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
from flask import Flask, request, jsonify, Response, stream_with_context, send_from_directory, render_template
import uuid
import logging

# Dodanie ścieżki do katalogu głównego projektu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import devopy modules
from devopy.decorators.editor_sandbox import editor_sandbox
from devopy.sandbox.docker import DockerSandbox

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
VENV_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "venvs")
os.makedirs(VENV_DIR, exist_ok=True)

# Rejestr funkcji
function_registry = {}

# Kolejka logów
log_queue = queue.Queue()

# Lista słuchaczy logów
log_listeners = []

# Podstawowe zależności dla aplikacji
CORE_DEPENDENCIES = [
    'flask==2.0.1',
    'requests==2.28.1',
    'jinja2==3.0.1',
    'werkzeug==2.0.1',
    'markupsafe==2.0.1'
]

# Zależności dla poszczególnych modułów
MODULE_DEPENDENCIES = {
    'code_generation': [
        'openai==0.27.0',
        'tiktoken==0.3.0'
    ],
    'docker': [
        'docker==6.0.1',
        'pyyaml==6.0'
    ],
    'testing': [
        'pytest==7.0.1',
        'coverage==6.3.2'
    ]
}

# Logger
logger = logging.getLogger(__name__)

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

# Funkcja do sprawdzania i instalacji zależności
def ensure_dependencies(dependencies, venv_path=None):
    """
    Sprawdza i instaluje brakujące zależności w środowisku wirtualnym
    
    Args:
        dependencies: Lista zależności do zainstalowania
        venv_path: Ścieżka do środowiska wirtualnego (opcjonalnie)
    
    Returns:
        bool: True jeśli wszystkie zależności są dostępne
    """
    if venv_path is None:
        venv_path = VENV_DIR
    
    venv_pip = os.path.join(venv_path, 'bin', 'pip')
    
    # Sprawdź, czy środowisko wirtualne istnieje
    if not os.path.exists(venv_path):
        logger.info(f"Tworzenie środowiska wirtualnego w {venv_path}")
        subprocess.run([sys.executable, '-m', 'venv', venv_path], check=True)
    
    # Pobierz listę zainstalowanych pakietów
    try:
        installed = subprocess.check_output([venv_pip, 'freeze']).decode('utf-8')
        installed_packages = {pkg.split('==')[0].lower() for pkg in installed.splitlines()}
    except subprocess.CalledProcessError:
        installed_packages = set()
    
    # Sprawdź i zainstaluj brakujące zależności
    to_install = []
    for dep in dependencies:
        pkg_name = dep.split('==')[0].lower()
        if pkg_name not in installed_packages:
            to_install.append(dep)
    
    if to_install:
        logger.info(f"Instalowanie brakujących zależności: {', '.join(to_install)}")
        try:
            subprocess.run([venv_pip, 'install'] + to_install, check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Błąd podczas instalacji zależności: {e}")
            return False
    
    return True

# Funkcja do sprawdzania i instalacji zależności
def ensure_dependencies(dependencies, venv_path=None):
    """
    Sprawdza i instaluje brakujące zależności w środowisku wirtualnym.
    """
    if venv_path is None:
        venv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "venv")
    
    # Ścieżka do pip w środowisku wirtualnym
    if sys.platform == "win32":
        pip_path = os.path.join(venv_path, "Scripts", "pip.exe")
    else:
        pip_path = os.path.join(venv_path, "bin", "pip")
    
    # Sprawdź, czy środowisko wirtualne istnieje
    if not os.path.exists(pip_path):
        print(f"Tworzenie środowiska wirtualnego w {venv_path}")
        subprocess.check_call([sys.executable, "-m", "venv", venv_path])
    
    # Instaluj brakujące zależności
    for dep in dependencies:
        try:
            # Próba importu pakietu
            module_name = dep.split("==")[0].split(">")[0].split("<")[0].strip()
            __import__(module_name)
            print(f"Pakiet {module_name} jest już zainstalowany")
        except ImportError:
            print(f"Instalacja pakietu {dep}")
            subprocess.check_call([pip_path, "install", dep])

# Definicja zależności
CORE_DEPENDENCIES = [
    "flask==2.0.1",
    "requests==2.28.1",
    "jinja2==3.0.1",
    "werkzeug==2.0.1",
    "markupsafe==2.0.1"
]

MODULE_DEPENDENCIES = {
    "openai": ["openai==0.27.0"],
    "docker": ["docker==6.0.1"],
    "testing": ["pytest==7.0.0", "coverage==6.3.2"]
}

# Główna funkcja aplikacji
@editor_sandbox(
    base_image="python:3.12-slim",
    packages=CORE_DEPENDENCIES,
    ports={5000: 5000},
    volumes={os.path.dirname(os.path.dirname(os.path.abspath(__file__))): "/app"},
    env_vars={"FLASK_ENV": "development", "FLASK_DEBUG": "1"},
    auto_start=True
)
def create_app(sandbox=None):
    """
    Tworzy i konfiguruje aplikację Flask.
    """
    # Upewnij się, że wszystkie zależności są zainstalowane
    ensure_dependencies(CORE_DEPENDENCIES)
    
    app = Flask(__name__, 
                static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "static"),
                template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "static"))
    
    # Konfiguracja aplikacji
    app.config['SECRET_KEY'] = str(uuid.uuid4())
    app.config['JSON_SORT_KEYS'] = False
    app.config['SANDBOX'] = sandbox
    
    # Logowanie
    log_queue = queue.Queue()
    log_handler = QueueHandler(log_queue)
    app.logger.addHandler(log_handler)
    app.logger.setLevel(logging.INFO)
    
    # Rejestracja tras
    @app.route('/')
    def index():
        return render_template('matrix_layout.html')
    
    @app.route('/matrix')
    def matrix():
        return render_template('matrix.html')
    
    @app.route('/api/examples')
    def get_examples():
        examples_dir = os.path.dirname(os.path.abspath(__file__))
        examples = []
        
        for filename in os.listdir(examples_dir):
            if filename.endswith('.py') and filename != 'smart_editor.py':
                example_path = os.path.join(examples_dir, filename)
                with open(example_path, 'r') as f:
                    content = f.read()
                
                examples.append({
                    'name': filename,
                    'path': example_path,
                    'content': content
                })
        
        return jsonify(examples)
    
    @app.route('/api/run-example', methods=['POST'])
    def run_example_endpoint():
        data = request.json
        example_path = data.get('path')
        
        if not example_path or not os.path.exists(example_path):
            return jsonify({'error': 'Invalid example path'}), 400
        
        # Uruchom przykład w kontenerze Docker, jeśli sandbox jest dostępny
        if sandbox and sandbox.ready:
            # Kopiuj plik do kontenera
            container_path = f"/app/examples/{os.path.basename(example_path)}"
            result = sandbox.execute(["python", container_path])
            
            return jsonify({
                'success': result['success'],
                'output': result['stdout'],
                'error': result['stderr']
            })
        else:
            # Fallback - uruchom lokalnie
            try:
                output = subprocess.check_output([sys.executable, example_path], 
                                               stderr=subprocess.STDOUT,
                                               text=True)
                return jsonify({'success': True, 'output': output})
            except subprocess.CalledProcessError as e:
                return jsonify({'success': False, 'error': e.output})
    
    @app.route('/api/view-example/<path:example_name>')
    def viewExampleCode(example_name):
        examples_dir = os.path.dirname(os.path.abspath(__file__))
        example_path = os.path.join(examples_dir, example_name)
        
        if not os.path.exists(example_path) or not example_path.endswith('.py'):
            return jsonify({'error': 'Example not found'}), 404
        
        with open(example_path, 'r') as f:
            content = f.read()
        
        return jsonify({'name': example_name, 'content': content})
    
    @app.route('/log-stream')
    def log_stream():
        """Endpoint do strumieniowania logów"""
        def generate():
            while True:
                try:
                    record = log_queue.get(block=False)
                    yield f"data: {json.dumps({'message': record.getMessage(), 'level': record.levelname})}\n\n"
                except queue.Empty:
                    yield f"data: {json.dumps({'heartbeat': True})}\n\n"
                time.sleep(0.5)
        
        return Response(stream_with_context(generate()), 
                       mimetype='text/event-stream')
    
    @app.route('/function-list')
    def function_list():
        """Endpoint zwracający listę dostępnych funkcji"""
        functions = []
        
        # Dodaj funkcje z bieżącego modułu
        for name, obj in globals().items():
            if callable(obj) and not name.startswith('_'):
                functions.append({
                    'name': name,
                    'doc': obj.__doc__ or 'No documentation available'
                })
        
        # Dodaj informacje o sandboxie Docker
        if sandbox and sandbox.ready:
            functions.append({
                'name': 'docker_sandbox',
                'doc': 'Docker sandbox is available for running code in isolation',
                'status': 'ready',
                'id': sandbox.sandbox_id
            })
        
        return jsonify(functions)
    
    @app.route('/api/docker-status')
    def docker_status():
        """Endpoint zwracający status sandboxa Docker"""
        if sandbox:
            return jsonify({
                'ready': sandbox.ready,
                'status': sandbox.status,
                'id': sandbox.sandbox_id,
                'container_id': sandbox.container_id
            })
        else:
            return jsonify({'ready': False, 'status': 'not_initialized'})
    
    @app.route('/api/docker-execute', methods=['POST'])
    def docker_execute():
        """Endpoint do wykonywania poleceń w sandboxie Docker"""
        if not sandbox or not sandbox.ready:
            return jsonify({'error': 'Docker sandbox not ready'}), 400
        
        data = request.json
        command = data.get('command')
        workdir = data.get('workdir', '/app')
        
        if not command:
            return jsonify({'error': 'No command provided'}), 400
        
        # Wykonaj polecenie w kontenerze
        if isinstance(command, str):
            command = command.split()
        
        result = sandbox.execute(command, workdir)
        return jsonify(result)
    
    return app

# Klasa do obsługi logów
class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue
    
    def emit(self, record):
        self.log_queue.put(record)

# Uruchomienie aplikacji
if __name__ == '__main__':
    # Upewnij się, że wszystkie zależności są zainstalowane
    ensure_dependencies(CORE_DEPENDENCIES)
    
    # Utwórz i uruchom aplikację
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
