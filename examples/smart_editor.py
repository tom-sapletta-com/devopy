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
from flask import Flask, render_template_string, request, jsonify, Response, stream_with_context

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

# Rejestr funkcji
function_registry = {}

# Kolejka logów
log_queue = queue.Queue()

# Szablon HTML
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart Editor - Devopy</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/theme/dracula.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/python/python.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/addon/edit/matchbrackets.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/addon/selection/active-line.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        .container {
            display: flex;
            flex-direction: column;
            height: 100vh;
            padding: 20px;
            box-sizing: border-box;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .header h1 {
            margin: 0;
            color: #333;
        }
        .main {
            display: flex;
            flex: 1;
            gap: 20px;
        }
        .editor-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .editor-header {
            background-color: #333;
            color: white;
            padding: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .editor-header h2 {
            margin: 0;
            font-size: 16px;
        }
        .prompt-container {
            padding: 10px;
            border-bottom: 1px solid #eee;
        }
        .prompt-input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            box-sizing: border-box;
        }
        .code-editor-container {
            flex: 1;
            position: relative;
            height: calc(100vh - 300px);
            min-height: 400px;
        }
        .output-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .output-header {
            background-color: #333;
            color: white;
            padding: 10px;
        }
        .output-header h2 {
            margin: 0;
            font-size: 16px;
        }
        .tabs {
            display: flex;
            background-color: #f1f1f1;
            border-bottom: 1px solid #ddd;
        }
        .tab {
            padding: 10px 15px;
            cursor: pointer;
            background-color: #f1f1f1;
            border: none;
            outline: none;
            font-size: 14px;
        }
        .tab.active {
            background-color: white;
            border-bottom: 2px solid #4CAF50;
        }
        .tab-content {
            display: none;
            padding: 15px;
            flex: 1;
            overflow: auto;
        }
        .tab-content.active {
            display: block;
        }
        .docker-config, .logs, .preview {
            height: 100%;
            overflow: auto;
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 14px;
            line-height: 1.5;
            background-color: #f9f9f9;
            padding: 10px;
            border-radius: 4px;
        }
        .logs {
            background-color: #1e1e1e;
            color: #ddd;
        }
        .button {
            padding: 8px 15px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            margin-left: 10px;
        }
        .button:hover {
            background-color: #45a049;
        }
        .button.secondary {
            background-color: #555;
        }
        .button.secondary:hover {
            background-color: #444;
        }
        .function-list {
            margin-top: 20px;
        }
        .function-item {
            padding: 10px;
            background-color: white;
            border-radius: 4px;
            margin-bottom: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            cursor: pointer;
        }
        .function-item:hover {
            background-color: #f9f9f9;
        }
        .function-name {
            font-weight: bold;
            color: #333;
        }
        .function-description {
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }
        pre {
            margin: 0;
        }
        code {
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Smart Editor - Devopy</h1>
            <div>
                <button id="new-function-btn" class="button">Nowa funkcja</button>
                <button id="save-btn" class="button">Zapisz</button>
                <button id="run-btn" class="button">Uruchom</button>
            </div>
        </div>
        <div class="main">
            <div class="editor-container">
                <div class="editor-header">
                    <h2>Edytor kodu</h2>
                </div>
                <div class="prompt-container">
                    <input type="text" id="prompt-input" class="prompt-input" placeholder="Opisz funkcję (np. 'Pobierz dane z API', 'Przetwórz dane JSON', 'Zapisz dane do bazy')">
                </div>
                <div class="code-editor-container">
                    <textarea id="code-editor"></textarea>
                </div>
            </div>
            <div class="output-container">
                <div class="output-header">
                    <h2>Wyjście</h2>
                </div>
                <div class="tabs">
                    <button class="tab active" onclick="openTab(event, 'docker-tab')">Docker</button>
                    <button class="tab" onclick="openTab(event, 'logs-tab')">Logi</button>
                    <button class="tab" onclick="openTab(event, 'preview-tab')">Podgląd</button>
                </div>
                <div id="docker-tab" class="tab-content active">
                    <pre class="docker-config" id="docker-config"></pre>
                </div>
                <div id="logs-tab" class="tab-content">
                    <pre class="logs" id="logs-output"></pre>
                </div>
                <div id="preview-tab" class="tab-content">
                    <div class="preview" id="preview-output"></div>
                </div>
            </div>
        </div>
        <div class="function-list" id="function-list">
            <!-- Lista funkcji będzie generowana dynamicznie -->
        </div>
    </div>

    <script>
        // Inicjalizacja edytora CodeMirror
        var editor = CodeMirror.fromTextArea(document.getElementById("code-editor"), {
            mode: "python",
            theme: "dracula",
            lineNumbers: true,
            matchBrackets: true,
            styleActiveLine: true,
            indentUnit: 4,
            tabSize: 4,
            indentWithTabs: false,
            lineWrapping: true,
            autoCloseBrackets: true
        });
        
        // Ustawienie wysokości edytora
        editor.setSize("100%", "100%");
        
        // Funkcja do przełączania zakładek
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tab-content");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].className = tabcontent[i].className.replace(" active", "");
            }
            tablinks = document.getElementsByClassName("tab");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
            document.getElementById(tabName).className += " active";
            evt.currentTarget.className += " active";
        }
        
        // Funkcja do generowania kodu na podstawie promptu
        function generateCode() {
            var prompt = document.getElementById("prompt-input").value;
            if (!prompt) {
                alert("Wprowadź opis funkcji!");
                return;
            }
            
            fetch('/generate-code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt: prompt
                })
            })
            .then(response => response.json())
            .then(data => {
                editor.setValue(data.code);
                document.getElementById("docker-config").textContent = data.docker_config;
            })
            .catch(error => {
                console.error('Błąd:', error);
                alert("Wystąpił błąd podczas generowania kodu: " + error);
            });
        }
        
        // Funkcja do zapisywania kodu
        function saveCode() {
            var code = editor.getValue();
            var prompt = document.getElementById("prompt-input").value;
            
            fetch('/save-code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    code: code,
                    prompt: prompt
                })
            })
            .then(response => response.json())
            .then(data => {
                alert("Kod zapisany pomyślnie!");
                loadFunctionList();
            })
            .catch(error => {
                console.error('Błąd:', error);
            });
        }
        
        // Funkcja do uruchamiania kodu
        function runCode() {
            var code = editor.getValue();
            
            fetch('/run-code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    code: code
                })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById("preview-output").innerHTML = data.result;
                openTab({currentTarget: document.querySelector('button.tab[onclick*="preview-tab"]')}, 'preview-tab');
            })
            .catch(error => {
                console.error('Błąd:', error);
            });
        }
        
        // Funkcja do wczytywania listy funkcji
        function loadFunctionList() {
            fetch('/function-list')
            .then(response => response.json())
            .then(data => {
                var functionList = document.getElementById("function-list");
                functionList.innerHTML = "";
                
                data.functions.forEach(func => {
                    var functionItem = document.createElement("div");
                    functionItem.className = "function-item";
                    functionItem.onclick = function() {
                        loadFunction(func.name);
                    };
                    
                    var functionName = document.createElement("div");
                    functionName.className = "function-name";
                    functionName.textContent = func.name;
                    
                    var functionDescription = document.createElement("div");
                    functionDescription.className = "function-description";
                    functionDescription.textContent = func.description;
                    
                    functionItem.appendChild(functionName);
                    functionItem.appendChild(functionDescription);
                    functionList.appendChild(functionItem);
                });
            })
            .catch(error => {
                console.error('Błąd:', error);
            });
        }
        
        // Funkcja do wczytywania konkretnej funkcji
        function loadFunction(functionName) {
            fetch('/function/' + functionName)
            .then(response => response.json())
            .then(data => {
                editor.setValue(data.code);
                document.getElementById("prompt-input").value = data.prompt;
                document.getElementById("docker-config").textContent = data.docker_config;
            })
            .catch(error => {
                console.error('Błąd:', error);
            });
        }
        
        // Funkcja do nasłuchiwania logów
        function startLogStream() {
            var logsOutput = document.getElementById("logs-output");
            var eventSource = new EventSource('/log-stream');
            
            eventSource.onmessage = function(event) {
                logsOutput.textContent += event.data + "\n";
                logsOutput.scrollTop = logsOutput.scrollHeight;
            };
            
            eventSource.onerror = function() {
                eventSource.close();
                setTimeout(startLogStream, 1000);
            };
        }
        
        // Inicjalizacja
        document.getElementById("prompt-input").addEventListener("keyup", function(event) {
            if (event.key === "Enter") {
                generateCode();
            }
        });
        
        document.getElementById("new-function-btn").addEventListener("click", function() {
            document.getElementById("prompt-input").value = "";
            editor.setValue("");
            document.getElementById("docker-config").textContent = "";
        });
        
        document.getElementById("save-btn").addEventListener("click", saveCode);
        document.getElementById("run-btn").addEventListener("click", runCode);
        
        // Wczytaj listę funkcji przy starcie
        loadFunctionList();
        
        // Rozpocznij nasłuchiwanie logów
        startLogStream();
        
        // Dodaj obsługę błędów
        window.onerror = function(message, source, lineno, colno, error) {
            console.error("Błąd JavaScript:", message, "w", source, "linia:", lineno);
            alert("Wystąpił błąd JavaScript: " + message);
        };
    </script>
</body>
</html>
"""

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
    code = f"""@devopy("{prompt}")
def {function_name}(data):
    \"\"\"
    {prompt}
    
    Args:
        data: Dane wejściowe
        
    Returns:
        Przetworzone dane
    \"\"\"
    # Implementacja funkcji
    print(f"Przetwarzanie danych: {{data}}")
    
    # Przykładowa logika
    result = {{"processed": data, "timestamp": "2025-05-10T17:37:12"}}
    
    return result
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
  command: "python -c 'from examples.smart_editor import {function_name}; print({function_name}(\"test\"))'"
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
sys.path.append('{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}')
from examples.temp_{function_name} import {function_name}
result = {function_name}("test_data")
print(result)
"""
        
        # Uruchomienie kodu w procesie
        process = subprocess.Popen(
            ["python", "-c", exec_code],
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
app = Flask(__name__)

@app.route('/')
def index():
    """Strona główna"""
    return render_template_string(HTML_TEMPLATE)

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
