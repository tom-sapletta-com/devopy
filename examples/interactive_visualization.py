import os
import sys
import inspect
import json
import io
import re
from flask import Flask, render_template_string, request, jsonify
from pygments import highlight
from pygments.lexers import PythonLexer, get_lexer_by_name
from pygments.formatters import HtmlFormatter
import markdown
import yaml
import uuid

# Katalog na wizualizacje
os.makedirs("generated/visualizations", exist_ok=True)

# Rejestr funkcji i ich dekoratorów
function_registry = {}

def devopy(*args, **kwargs):
    """
    Uniwersalny dekorator Devopy, który automatycznie interpretuje parametry
    w zależności od ich typu i formatu.
    
    Przykłady:
    @devopy("Napisz funkcję, która pobiera dane z API") - prompt dla text2python
    @devopy("GET /api/data") - endpoint REST API
    @devopy("run.sh") - skrypt do uruchomienia
    @devopy("docker:python:3.9") - konfiguracja Dockera
    """
    def decorator(func):
        # Inicjalizacja rejestracji funkcji
        if func.__name__ not in function_registry:
            function_registry[func.__name__] = {
                'func': func,
                'docstring': func.__doc__,
                'signature': str(inspect.signature(func)),
                'source': inspect.getsource(func),
                'decorators': []
            }
        
        # Przetwarzanie argumentów
        for arg in args:
            if isinstance(arg, str):
                # Rozpoznawanie typu argumentu na podstawie jego formatu
                if arg.startswith("GET ") or arg.startswith("POST ") or arg.startswith("PUT ") or arg.startswith("DELETE "):
                    # REST API endpoint
                    parts = arg.split(" ", 1)
                    method, route = parts[0], parts[1]
                    function_registry[func.__name__]['decorators'].append({
                        'type': 'restapi',
                        'method': method,
                        'route': route,
                        'display': f"@restapi_task({method} {route})"
                    })
                elif arg.endswith(".sh") or arg.endswith(".bash") or arg.endswith(".cmd") or arg.endswith(".bat"):
                    # Skrypt do uruchomienia
                    function_registry[func.__name__]['decorators'].append({
                        'type': 'shell',
                        'script': arg,
                        'display': f"@shell_task({arg})"
                    })
                elif arg.startswith("docker:"):
                    # Konfiguracja Dockera
                    parts = arg.split(":")
                    if len(parts) >= 3:
                        image = parts[1]
                        tag = parts[2]
                        function_registry[func.__name__]['decorators'].append({
                            'type': 'docker',
                            'image': image,
                            'tag': tag,
                            'display': f"@docker_task({image}:{tag})"
                        })
                elif "type Query" in arg or "type Mutation" in arg:
                    # Schemat GraphQL
                    function_registry[func.__name__]['decorators'].append({
                        'type': 'graphql',
                        'schema': arg,
                        'display': "@graphql_task(...)"
                    })
                elif "syntax = \"proto3\"" in arg or "message " in arg:
                    # Definicja gRPC
                    function_registry[func.__name__]['decorators'].append({
                        'type': 'grpc',
                        'proto': arg,
                        'display': "@grpc_task(...)"
                    })
                else:
                    # Domyślnie traktuj jako prompt dla text2python
                    function_registry[func.__name__]['decorators'].append({
                        'type': 'text2python',
                        'prompt': arg,
                        'display': f"@text2python_task(\"{arg}\")"
                    })
        
        # Przetwarzanie argumentów nazwanych
        for key, value in kwargs.items():
            function_registry[func.__name__]['decorators'].append({
                'type': key,
                'value': value,
                'display': f"@{key}_task({value})"
            })
        
        return func
    return decorator

# Przykładowy system przetwarzania danych z dekoratorami
@devopy("Napisz funkcję, która pobiera dane z API", "GET /api/data", "fetch_data.sh")
def fetch_data(source: str, limit: int = 100):
    """Pobiera dane z zewnętrznego API"""
    print(f"Pobieranie danych z {source}, limit: {limit}")
    # Symulacja pobierania danych
    return [{"id": i, "value": f"data_{i}"} for i in range(limit)]

@devopy("Napisz funkcję, która filtruje dane według kryteriów", """
type Query {
  filterData(data: [DataInput!]!, criteria: String!): [Data!]!
}

input DataInput {
  id: Int!
  value: String!
}

type Data {
  id: Int!
  value: String!
}
""")
def filter_data(data, criteria):
    """Filtruje dane według podanych kryteriów"""
    print(f"Filtrowanie danych według kryterium: {criteria}")
    # Symulacja filtrowania
    return [item for item in data if criteria in item["value"]]

@devopy("Napisz funkcję, która transformuje dane do innego formatu", """
syntax = "proto3";

message TransformRequest {
    repeated DataItem data = 1;
    string format = 2;
}

message DataItem {
    int32 id = 1;
    string value = 2;
}

message TransformResponse {
    string result = 1;
}

service TransformService {
    rpc Transform (TransformRequest) returns (TransformResponse);
}
""", "docker:python:3.9")
def transform_data(data, format="json"):
    """Transformuje dane do określonego formatu"""
    print(f"Transformacja danych do formatu: {format}")
    if format.lower() == "json":
        return json.dumps(data)
    elif format.lower() == "csv":
        header = ",".join(data[0].keys()) if data else ""
        rows = [",".join(str(v) for v in item.values()) for item in data]
        return "\n".join([header] + rows)
    else:
        return str(data)

@devopy("Napisz funkcję, która zapisuje dane do bazy danych", "POST /api/data/save", """
type Mutation {
  saveData(data: [DataInput!]!, destination: String!): SaveResult!
}

type SaveResult {
  success: Boolean!
  message: String
  count: Int!
}
""")
def save_data(data, destination):
    """Zapisuje dane do określonego miejsca docelowego"""
    print(f"Zapisywanie {len(data)} elementów do {destination}")
    # Symulacja zapisywania
    return {
        "success": True,
        "message": f"Zapisano {len(data)} elementów do {destination}",
        "count": len(data)
    }

@devopy("Napisz funkcję, która analizuje dane i generuje raport", "POST /api/data/analyze")
def analyze_data(data, metrics=None):
    """Analizuje dane i generuje raport z metrykami"""
    if metrics is None:
        metrics = ["count", "avg", "min", "max"]
    
    print(f"Analizowanie danych z metrykami: {metrics}")
    
    # Symulacja analizy
    result = {"count": len(data)}
    
    if "avg" in metrics and data:
        # Zakładamy, że dane mają pole 'value' które można przekonwertować na liczbę
        try:
            values = [float(item["value"].split("_")[1]) for item in data]
            result["avg"] = sum(values) / len(values)
        except (ValueError, KeyError, IndexError):
            result["avg"] = None
    
    if "min" in metrics and data:
        try:
            values = [float(item["value"].split("_")[1]) for item in data]
            result["min"] = min(values)
        except (ValueError, KeyError, IndexError):
            result["min"] = None
    
    if "max" in metrics and data:
        try:
            values = [float(item["value"].split("_")[1]) for item in data]
            result["max"] = max(values)
        except (ValueError, KeyError, IndexError):
            result["max"] = None
    
    return result

def generate_code_html(func_name=None):
    """Generuje kolorowany HTML z kodem funkcji"""
    formatter = HtmlFormatter(style='colorful', linenos=True)
    
    if func_name and func_name in function_registry:
        # Pobierz kod źródłowy funkcji
        source = function_registry[func_name]['source']
        
        # Koloruj kod
        highlighted = highlight(source, PythonLexer(), formatter)
        
        html = f'<div class="function-code">{highlighted}</div>'
    else:
        functions = list(function_registry.values())
        html = '<div class="code-container">'
        
        for func_info in functions:
            # Pobierz kod źródłowy funkcji
            source = func_info['source']
            
            # Koloruj kod
            highlighted = highlight(source, PythonLexer(), formatter)
            
            html += f'<div class="function-code">{highlighted}</div>'
        
        html += '</div>'
    
    # Dodaj CSS
    html += f'<style>{formatter.get_style_defs(".highlight")}</style>'
    
    return html

def generate_execution_log():
    """Generuje log wykonania funkcji"""
    # Przechwyć stdout
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    
    try:
        # Symulacja przepływu danych
        print("=== Rozpoczęcie przepływu danych ===")
        
        # Krok 1: Pobierz dane
        data = fetch_data("example.com/api", 5)
        print(f"Pobrane dane: {data}")
        
        # Krok 2: Filtruj dane
        filtered_data = filter_data(data, "data_3")
        print(f"Przefiltrowane dane: {filtered_data}")
        
        # Krok 3: Transformuj dane
        transformed_data = transform_data(filtered_data, "json")
        print(f"Przetransformowane dane: {transformed_data}")
        
        # Krok 4: Zapisz dane
        save_result = save_data(filtered_data, "database")
        print(f"Wynik zapisywania: {save_result}")
        
        # Krok 5: Analizuj dane
        analysis = analyze_data(data)
        print(f"Wynik analizy: {analysis}")
        
        print("=== Zakończenie przepływu danych ===")
    finally:
        # Przywróć stdout
        sys.stdout = old_stdout
    
    # Pobierz logi
    log = new_stdout.getvalue()
    return log

def highlight_code_in_markdown(text):
    """Podświetla bloki kodu w tekście markdown"""
    def replace_code_block(match):
        language = match.group(1) or 'text'
        code = match.group(2)
        
        try:
            lexer = get_lexer_by_name(language)
        except:
            lexer = get_lexer_by_name('text')
        
        formatter = HtmlFormatter(style='colorful')
        highlighted = highlight(code, lexer, formatter)
        
        return f'<div class="code-block">{highlighted}</div>'
    
    # Znajdź i zastąp bloki kodu
    pattern = r'```(\w+)?\n(.*?)```'
    result = re.sub(pattern, replace_code_block, text, flags=re.DOTALL)
    
    return result

# Aplikacja Flask
app = Flask(__name__)

# Główny szablon HTML
main_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Interaktywna wizualizacja dekoratorów Devopy</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 0;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        .header {
            background: #333;
            color: white;
            padding: 10px 20px;
        }
        .content {
            display: flex;
            flex: 1;
            overflow: hidden;
        }
        .sidebar {
            width: 250px;
            background: #f5f5f5;
            padding: 10px;
            overflow-y: auto;
            border-right: 1px solid #ddd;
        }
        .main-content {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }
        .function-item {
            padding: 8px 12px;
            margin-bottom: 5px;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .function-item:hover {
            background: #e0e0e0;
        }
        .function-item.active {
            background: #007bff;
            color: white;
        }
        .section {
            margin-bottom: 30px;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
        }
        .section h2 {
            margin-top: 0;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .decorator-tag {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            margin-right: 5px;
            margin-bottom: 5px;
            font-size: 0.8em;
        }
        .text2python { background: #e6f7ff; color: #0066cc; }
        .restapi { background: #e6ffe6; color: #006600; }
        .graphql { background: #ffe6f0; color: #cc0066; }
        .grpc { background: #fff2e6; color: #cc6600; }
        .shell { background: #f0f0f0; color: #333333; }
        .docker { background: #e6e6ff; color: #000066; }
        .tabs {
            display: flex;
            border-bottom: 1px solid #ddd;
            margin-bottom: 15px;
        }
        .tab {
            padding: 8px 16px;
            cursor: pointer;
            border: 1px solid transparent;
            border-bottom: none;
            margin-right: 5px;
            border-radius: 4px 4px 0 0;
        }
        .tab.active {
            background: #fff;
            border-color: #ddd;
            border-bottom: 1px solid white;
            margin-bottom: -1px;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        pre {
            background: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 0;
        }
        .function-code {
            margin-bottom: 20px;
        }
        .code-editor-container {
            position: relative;
            height: calc(100vh - 300px);
            min-height: 400px;
            margin-bottom: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        #code-editor {
            position: absolute;
            top: 0;
            right: 0;
            bottom: 0;
            left: 0;
            font-size: 14px;
        }
        .button {
            padding: 8px 16px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .button:hover {
            background: #0069d9;
        }
        .code-block {
            margin: 15px 0;
        }
        .markdown-content {
            line-height: 1.6;
        }
        .markdown-content h1, .markdown-content h2, .markdown-content h3 {
            margin-top: 20px;
            margin-bottom: 10px;
        }
        .markdown-content p {
            margin-bottom: 15px;
        }
        .markdown-content ul, .markdown-content ol {
            margin-bottom: 15px;
            padding-left: 20px;
        }
        .flow-step {
            padding: 10px;
            margin: 10px 0;
            border-left: 3px solid #0066cc;
            background: #f0f8ff;
        }
        .flow-arrow {
            text-align: center;
            font-size: 20px;
            color: #999;
            margin: 5px 0;
        }
        .docker-compose-section {
            background: #f8f9fa;
            border-radius: 5px;
            padding: 15px;
            margin-top: 20px;
        }
        .docker-service {
            border-left: 3px solid #0066cc;
            padding: 10px;
            margin: 10px 0;
            background: #f0f8ff;
        }
        {{ formatter_styles }}
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.62.0/codemirror.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.62.0/theme/dracula.min.css">
</head>
<body>
    <div class="header">
        <h1>Interaktywna wizualizacja dekoratorów Devopy</h1>
    </div>
    <div class="content">
        <div class="sidebar">
            <h3>Funkcje</h3>
            <div id="function-list">
                {% for func_name, func_info in functions.items() %}
                <div class="function-item {% if selected_function == func_name %}active{% endif %}" onclick="showFunction('{{ func_name }}')">{{ func_name }}</div>
                {% endfor %}
            </div>
        </div>
        <div class="main-content">
            <div id="function-details">
                {% if selected_function %}
                <h2>{{ selected_function }}</h2>
                <p>{{ functions[selected_function].docstring }}</p>
                <p><strong>Sygnatura:</strong> {{ functions[selected_function].signature }}</p>
                
                <div class="section">
                    <h2>Dekoratory</h2>
                    {% for decorator in functions[selected_function].decorators %}
                    <span class="decorator-tag {{ decorator.type }}">{{ decorator.display }}</span>
                    {% endfor %}
                </div>
                
                <div class="tabs">
                    <div class="tab active" onclick="showTab('code')">Kod</div>
                    <div class="tab" onclick="showTab('editor')">Edytor</div>
                    <div class="tab" onclick="showTab('logs')">Logi</div>
                    <div class="tab" onclick="showTab('markdown')">Markdown</div>
                    <div class="tab" onclick="showTab('docker')">Docker</div>
                </div>
                
                <div id="code" class="tab-content active">
                    {{ code_html|safe }}
                </div>
                
                <div id="editor" class="tab-content">
                    <div class="code-editor-container">
                        <div id="code-editor"></div>
                    </div>
                    <button class="button" onclick="saveCode()">Zapisz zmiany</button>
                </div>
                
                <div id="logs" class="tab-content">
                    <pre>{{ execution_log }}</pre>
                </div>
                
                <div id="markdown" class="tab-content">
                    <div class="markdown-content">
                        {{ markdown_content|safe }}
                    </div>
                </div>
                
                <div id="docker" class="tab-content">
                    <div class="docker-compose-section">
                        <h3>Docker Compose dla {{ selected_function }}</h3>
                        <pre><code class="language-yaml">{{ docker_compose_yaml }}</code></pre>
                        
                        <h3>Usługi Docker</h3>
                        {% for service in docker_services %}
                        <div class="docker-service">
                            <h4>{{ service.name }}</h4>
                            <p><strong>Obraz:</strong> {{ service.image }}</p>
                            <p><strong>Porty:</strong> {{ service.ports }}</p>
                            <p><strong>Zmienne środowiskowe:</strong></p>
                            <pre>{{ service.env_vars }}</pre>
                        </div>
                        {% endfor %}
                        
                        <h3>Logi Docker</h3>
                        <pre>{{ docker_logs }}</pre>
                    </div>
                </div>
                {% else %}
                <div class="section">
                    <h2>Przepływ danych</h2>
                    <div class="data-flow">
                        <div class="flow-step">
                            <strong>1. Pobieranie danych</strong> (fetch_data)
                            <div>Dekoratory: text2python, restapi, shell</div>
                        </div>
                        <div class="flow-arrow">↓</div>
                        <div class="flow-step">
                            <strong>2. Filtrowanie danych</strong> (filter_data)
                            <div>Dekoratory: text2python, graphql</div>
                        </div>
                        <div class="flow-arrow">↓</div>
                        <div class="flow-step">
                            <strong>3. Transformacja danych</strong> (transform_data)
                            <div>Dekoratory: text2python, grpc, docker</div>
                        </div>
                        <div class="flow-arrow">↓</div>
                        <div class="flow-step">
                            <strong>4. Zapisywanie danych</strong> (save_data)
                            <div>Dekoratory: text2python, restapi, graphql</div>
                        </div>
                        <div class="flow-arrow">↓</div>
                        <div class="flow-step">
                            <strong>5. Analiza danych</strong> (analyze_data)
                            <div>Dekoratory: text2python, restapi</div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Docker Compose</h2>
                    <pre><code class="language-yaml">{{ docker_compose_full }}</code></pre>
                </div>
                
                <div class="section">
                    <h2>Logi wykonania</h2>
                    <pre>{{ execution_log }}</pre>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.62.0/codemirror.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.62.0/mode/python/python.min.js"></script>
    <script>
        let editor;
        
        function showFunction(funcName) {
            // Podświetl wybraną funkcję
            document.querySelectorAll('.function-item').forEach(item => {
                item.classList.remove('active');
            });
            document.querySelector(`.function-item[onclick="showFunction('${funcName}')"]`).classList.add('active');
            
            // Załaduj szczegóły funkcji
            fetch(`/function/${funcName}`)
                .then(response => response.text())
                .then(html => {
                    document.getElementById('function-details').innerHTML = html;
                    // Inicjalizuj edytor po załadowaniu szczegółów funkcji
                    initCodeMirror();
                });
        }
        
        function initCodeMirror() {
            const editorElement = document.getElementById('code-editor');
            if (editorElement) {
                const code = editorElement.textContent || '';
                
                // Usuń poprzedni edytor, jeśli istnieje
                if (editor) {
                    editor.toTextArea();
                }
                
                // Inicjalizuj CodeMirror
                editor = CodeMirror(editorElement, {
                    value: code,
                    mode: 'python',
                    theme: 'dracula',
                    lineNumbers: true,
                    indentUnit: 4,
                    tabSize: 4,
                    indentWithTabs: false,
                    lineWrapping: true,
                    matchBrackets: true,
                    autoCloseBrackets: true,
                    extraKeys: {
                        "Tab": function(cm) {
                            if (cm.somethingSelected()) {
                                cm.indentSelection("add");
                            } else {
                                cm.replaceSelection("    ", "end", "+input");
                            }
                        }
                    }
                });
                
                // Ustaw początkową wartość
                editor.setValue(code);
            }
        }
        
        function showTab(tabId) {
            // Ukryj wszystkie zakładki
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Pokaż wybraną zakładkę
            document.getElementById(tabId).classList.add('active');
            document.querySelector(`.tab[onclick="showTab('${tabId}')"]`).classList.add('active');
            
            // Odśwież edytor, jeśli wybrano zakładkę edytora
            if (tabId === 'editor' && editor) {
                editor.refresh();
            }
        }
        
        function saveCode() {
            const funcName = '{{ selected_function }}';
            const code = editor ? editor.getValue() : document.getElementById('code-editor').value;
            
            fetch('/save_code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    function_name: funcName,
                    code: code
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Kod został zapisany!');
                    // Odśwież widok kodu
                    showFunction(funcName);
                } else {
                    alert('Błąd podczas zapisywania kodu: ' + data.error);
                }
            });
        }
        
        // Inicjalizuj edytor po załadowaniu strony
        document.addEventListener('DOMContentLoaded', function() {
            initCodeMirror();
        });
    </script>
</body>
</html>
'''

# Funkcja do generowania konfiguracji Docker Compose dla funkcji
def generate_docker_compose(func_name):
    """Generuje konfigurację Docker Compose dla funkcji"""
    if func_name not in function_registry:
        return "", [], ""
    
    # Sprawdź, czy istnieje plik YAML z definicją Docker dla tej funkcji
    yaml_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docker', f'{func_name}.yml')
    
    if os.path.exists(yaml_path):
        # Wczytaj definicję z pliku YAML
        with open(yaml_path, 'r') as f:
            try:
                service_def = yaml.safe_load(f)
                
                if 'service' in service_def:
                    service = service_def['service']
                    service_name = service.get('name', func_name.replace('_', '-'))
                    image = service.get('image', 'python:3.9-slim')
                    ports = service.get('ports', [])
                    env_vars = service.get('environment', [])
                    volumes = service.get('volumes', [])
                    command = service.get('command', None)
                    dependencies = service.get('dependencies', [])
                    labels = service.get('labels', [])
                    logs_entries = service.get('logs', [])
                    
                    # Generuj konfigurację Docker Compose
                    docker_compose = f"""version: '3'
services:
  {service_name}:
    image: {image}
    volumes:
"""
                    for volume in volumes:
                        docker_compose += f"      - {volume}\n"
                    
                    docker_compose += "    working_dir: /app\n"
                    
                    if ports:
                        docker_compose += "    ports:\n"
                        for port in ports:
                            docker_compose += f"      - \"{port}\"\n"
                    
                    if env_vars:
                        docker_compose += "    environment:\n"
                        for env_var in env_vars:
                            docker_compose += f"      - {env_var}\n"
                    
                    if command:
                        docker_compose += f"    command: {command}\n"
                    else:
                        docker_compose += f"    command: python -c \"from examples.interactive_visualization import {func_name}; print({func_name}('test'))\"\n"
                    
                    if dependencies:
                        docker_compose += "    depends_on:\n"
                        for dep in dependencies:
                            docker_compose += f"      - {dep}\n"
                    
                    if labels:
                        docker_compose += "    labels:\n"
                        for label in labels:
                            docker_compose += f"      - \"{label}\"\n"
                    
                    # Generuj listę usług
                    ports_str = ", ".join(ports) if ports else "N/A"
                    env_vars_str = "\n".join(env_vars) if env_vars else "N/A"
                    
                    services = [{
                        'name': service_name,
                        'image': image,
                        'ports': ports_str,
                        'env_vars': env_vars_str
                    }]
                    
                    # Generuj logi
                    logs = "\n".join(logs_entries) if logs_entries else f"# Symulowane logi dla {service_name}\n[2025-05-10 17:30:00] INFO: Uruchamianie kontenera {service_name}\n[2025-05-10 17:30:01] INFO: Kontener {service_name} uruchomiony\n[2025-05-10 17:30:02] INFO: Wykonywanie funkcji {func_name}\n[2025-05-10 17:30:03] INFO: Funkcja {func_name} zakończona powodzeniem"
                    
                    return docker_compose, services, logs
            except Exception as e:
                print(f"Błąd podczas wczytywania pliku YAML dla {func_name}: {e}")
    
    # Jeśli nie ma pliku YAML lub wystąpił błąd, użyj domyślnej konfiguracji
    func_info = function_registry[func_name]
    
    # Sprawdź, czy funkcja ma dekorator Docker
    has_docker = any(dec['type'] == 'docker' for dec in func_info['decorators'])
    
    # Domyślna konfiguracja, jeśli nie ma dekoratora Docker
    if not has_docker:
        service_name = func_name.replace('_', '-')
        docker_compose = f"""version: '3'
services:
  {service_name}:
    image: python:3.9-slim
    volumes:
      - ./:/app
    working_dir: /app
    command: python -c "from examples.interactive_visualization import {func_name}; print({func_name}('test'))"
    environment:
      - PYTHONPATH=/app
"""
        services = [{
            'name': service_name,
            'image': 'python:3.9-slim',
            'ports': 'N/A',
            'env_vars': 'PYTHONPATH=/app'
        }]
        logs = f"# Symulowane logi dla {service_name}\n[2025-05-10 17:30:00] INFO: Uruchamianie {func_name} w kontenerze\n[2025-05-10 17:30:01] INFO: Wykonywanie funkcji {func_name}\n[2025-05-10 17:30:02] INFO: Funkcja {func_name} zakończona powodzeniem"
    else:
        # Znajdź dekorator Docker
        docker_dec = next((dec for dec in func_info['decorators'] if dec['type'] == 'docker'), None)
        
        # Parsuj parametry dekoratora
        image = docker_dec.get('params', {}).get('image', 'python:3.9-slim')
        port = docker_dec.get('params', {}).get('port', None)
        env_vars = docker_dec.get('params', {}).get('env_vars', {})
        command = docker_dec.get('params', {}).get('command', None)
        
        # Generuj konfigurację Docker Compose
        service_name = func_name.replace('_', '-')
        docker_compose = f"""version: '3'
services:
  {service_name}:
    image: {image}
    volumes:
      - ./:/app
    working_dir: /app"""
        
        if port:
            docker_compose += f"""
    ports:
      - "{port}:{port}" """
        
        if env_vars:
            docker_compose += "\n    environment:"
            for key, value in env_vars.items():
                docker_compose += f"\n      - {key}={value}"
        
        if command:
            docker_compose += f"\n    command: {command}"
        else:
            docker_compose += f"\n    command: python -c \"from examples.interactive_visualization import {func_name}; print({func_name}('test'))\""
        
        # Generuj listę usług
        ports_str = f"{port}:{port}" if port else "N/A"
        env_vars_str = "\n".join([f"{k}={v}" for k, v in env_vars.items()]) if env_vars else "N/A"
        
        services = [{
            'name': service_name,
            'image': image,
            'ports': ports_str,
            'env_vars': env_vars_str
        }]
        
        # Generuj przykładowe logi
        logs = f"# Symulowane logi dla {service_name}\n[2025-05-10 17:30:00] INFO: Uruchamianie kontenera {service_name}\n[2025-05-10 17:30:01] INFO: Kontener {service_name} uruchomiony\n[2025-05-10 17:30:02] INFO: Wykonywanie funkcji {func_name}\n[2025-05-10 17:30:03] INFO: Funkcja {func_name} zakończona powodzeniem"
    
    return docker_compose, services, logs

# Funkcja do generowania pełnej konfiguracji Docker Compose dla wszystkich funkcji
def generate_full_docker_compose():
    """Generuje pełną konfigurację Docker Compose dla wszystkich funkcji"""
    docker_compose = "version: '3'\nservices:\n"
    
    # Dodaj główną usługę
    docker_compose += """  interactive-visualization:
    image: python:3.9-slim
    volumes:
      - ./:/app
    working_dir: /app
    command: bash -c "pip install -r requirements.txt && python examples/interactive_visualization.py"
    ports:
      - "5050:5050"
    environment:
      - PYTHONPATH=/app
      - FLASK_ENV=development
      - FLASK_DEBUG=1
    networks:
      - devopy-network

  # Baza danych PostgreSQL
  database:
    image: postgres:13
    environment:
      - POSTGRES_USER=devopy
      - POSTGRES_PASSWORD=devopy123
      - POSTGRES_DB=devopy_data
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - devopy-network
"""
    
    # Dodaj usługi dla funkcji
    for func_name, func_info in function_registry.items():
        # Sprawdź, czy istnieje plik YAML z definicją Docker dla tej funkcji
        yaml_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docker', f'{func_name}.yml')
        
        if os.path.exists(yaml_path):
            # Wczytaj definicję z pliku YAML
            with open(yaml_path, 'r') as f:
                try:
                    service_def = yaml.safe_load(f)
                    
                    if 'service' in service_def:
                        service = service_def['service']
                        service_name = service.get('name', func_name.replace('_', '-'))
                        image = service.get('image', 'python:3.9-slim')
                        ports = service.get('ports', [])
                        env_vars = service.get('environment', [])
                        volumes = service.get('volumes', [])
                        command = service.get('command', None)
                        dependencies = service.get('dependencies', [])
                        labels = service.get('labels', [])
                        
                        # Generuj konfigurację dla usługi
                        docker_compose += f"  {service_name}:\n"
                        docker_compose += f"    image: {image}\n"
                        docker_compose += "    volumes:\n"
                        for volume in volumes:
                            docker_compose += f"      - {volume}\n"
                        
                        docker_compose += "    working_dir: /app\n"
                        
                        if ports:
                            docker_compose += "    ports:\n"
                            for port in ports:
                                docker_compose += f"      - \"{port}\"\n"
                        
                        if env_vars:
                            docker_compose += "    environment:\n"
                            for env_var in env_vars:
                                docker_compose += f"      - {env_var}\n"
                        
                        if command:
                            docker_compose += f"    command: {command}\n"
                        else:
                            docker_compose += f"    command: python -c \"from examples.interactive_visualization import {func_name}; print({func_name}('test'))\"\n"
                        
                        if dependencies:
                            docker_compose += "    depends_on:\n"
                            for dep in dependencies:
                                docker_compose += f"      - {dep}\n"
                        
                        if labels:
                            docker_compose += "    labels:\n"
                            for label in labels:
                                docker_compose += f"      - \"{label}\"\n"
                        
                        docker_compose += "    networks:\n"
                        docker_compose += "      - devopy-network\n"
                        
                        continue
                except Exception as e:
                    print(f"Błąd podczas wczytywania pliku YAML dla {func_name}: {e}")
        
        # Jeśli nie ma pliku YAML lub wystąpił błąd, użyj domyślnej konfiguracji
        service_name = func_name.replace('_', '-')
        
        # Sprawdź, czy funkcja ma dekorator Docker
        has_docker = any(dec['type'] == 'docker' for dec in func_info['decorators'])
        
        if has_docker:
            # Znajdź dekorator Docker
            docker_dec = next((dec for dec in func_info['decorators'] if dec['type'] == 'docker'), None)
            
            # Parsuj parametry dekoratora
            image = docker_dec.get('params', {}).get('image', 'python:3.9-slim')
            port = docker_dec.get('params', {}).get('port', None)
            env_vars = docker_dec.get('params', {}).get('env_vars', {})
            command = docker_dec.get('params', {}).get('command', None)
        else:
            # Domyślna konfiguracja
            image = 'python:3.9-slim'
            port = None
            env_vars = {}
            command = None
        
        # Generuj konfigurację dla usługi
        docker_compose += f"  {service_name}:\n"
        docker_compose += f"    image: {image}\n"
        docker_compose += "    volumes:\n"
        docker_compose += "      - ./:/app\n"
        docker_compose += "    working_dir: /app\n"
        
        if port:
            docker_compose += "    ports:\n"
            docker_compose += f"      - \"{port}:{port}\"\n"
        
        if env_vars:
            docker_compose += "    environment:\n"
            for key, value in env_vars.items():
                docker_compose += f"      - {key}={value}\n"
        
        if command:
            docker_compose += f"    command: {command}\n"
        else:
            docker_compose += f"    command: python -c \"from examples.interactive_visualization import {func_name}; print({func_name}('test'))\"\n"
        
        docker_compose += "    networks:\n"
        docker_compose += "      - devopy-network\n"
    
    # Dodaj definicje sieci i woluminów
    docker_compose += """
networks:
  devopy-network:
    driver: bridge

volumes:
  postgres-data:
"""
    
    return docker_compose

@app.route('/')
def index():
    """Strona główna"""
    formatter = HtmlFormatter(style='colorful')
    formatter_styles = formatter.get_style_defs('.highlight')
    
    # Generuj pełną konfigurację Docker Compose
    docker_compose_full = generate_full_docker_compose()
    
    return render_template_string(
        main_template,
        functions=function_registry,
        selected_function=None,
        execution_log=generate_execution_log(),
        formatter_styles=formatter_styles,
        docker_compose_full=docker_compose_full
    )

@app.route('/function/<func_name>')
def function_detail(func_name):
    """Szczegóły funkcji"""
    if func_name not in function_registry:
        return "Funkcja nie znaleziona", 404
    
    # Generuj kolorowany kod HTML
    code_html = generate_code_html(func_name)
    
    # Generuj przykładowy markdown z blokami kodu
    markdown_text = f"""
# Funkcja {func_name}

{function_registry[func_name]['docstring']}

## Sygnatura

```python
def {func_name}{function_registry[func_name]['signature']}
```

## Dekoratory

{', '.join([dec['display'] for dec in function_registry[func_name]['decorators']])}

## Przykład użycia

```python
# Przykład użycia funkcji {func_name}
result = {func_name}('example_param', 42)
print(result)
```

## Przepływ danych

1. Dane wejściowe -> {func_name}
2. Przetwarzanie w {func_name}
3. Wynik -> Następna funkcja
    """
    
    # Renderuj markdown z podświetlonymi blokami kodu
    markdown_content = markdown.markdown(markdown_text)
    markdown_content = highlight_code_in_markdown(markdown_text)
    
    # Generuj konfigurację Docker Compose dla funkcji
    docker_compose_yaml, docker_services, docker_logs = generate_docker_compose(func_name)
    
    # Zwróć tylko zawartość sekcji function-details, a nie cały szablon
    function_detail_template = '''
    <h2>{{ selected_function }}</h2>
    <p>{{ functions[selected_function].docstring }}</p>
    <p><strong>Sygnatura:</strong> {{ functions[selected_function].signature }}</p>
    
    <div class="section">
        <h2>Dekoratory</h2>
        {% for decorator in functions[selected_function].decorators %}
        <span class="decorator-tag {{ decorator.type }}">{{ decorator.display }}</span>
        {% endfor %}
    </div>
    
    <div class="tabs">
        <div class="tab active" onclick="showTab('code')">Kod</div>
        <div class="tab" onclick="showTab('editor')">Edytor</div>
        <div class="tab" onclick="showTab('logs')">Logi</div>
        <div class="tab" onclick="showTab('markdown')">Markdown</div>
        <div class="tab" onclick="showTab('docker')">Docker</div>
    </div>
    
    <div id="code" class="tab-content active">
        {{ code_html|safe }}
    </div>
    
    <div id="editor" class="tab-content">
        <div class="code-editor-container">
            <div id="code-editor">{{ functions[selected_function].source }}</div>
        </div>
        <button class="button" onclick="saveCode()">Zapisz zmiany</button>
    </div>
    
    <div id="logs" class="tab-content">
        <pre>{{ execution_log }}</pre>
    </div>
    
    <div id="markdown" class="tab-content">
        <div class="markdown-content">
            {{ markdown_content|safe }}
        </div>
    </div>
    
    <div id="docker" class="tab-content">
        <div class="docker-compose-section">
            <h3>Docker Compose dla {{ selected_function }}</h3>
            <pre><code class="language-yaml">{{ docker_compose_yaml }}</code></pre>
            
            <h3>Usługi Docker</h3>
            {% for service in docker_services %}
            <div class="docker-service">
                <h4>{{ service.name }}</h4>
                <p><strong>Obraz:</strong> {{ service.image }}</p>
                <p><strong>Porty:</strong> {{ service.ports }}</p>
                <p><strong>Zmienne środowiskowe:</strong></p>
                <pre>{{ service.env_vars }}</pre>
            </div>
            {% endfor %}
            
            <h3>Logi Docker</h3>
            <pre>{{ docker_logs }}</pre>
        </div>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            initCodeMirror();
        });
    </script>
    '''
    
    return render_template_string(
        function_detail_template,
        functions=function_registry,
        selected_function=func_name,
        code_html=code_html,
        execution_log=generate_execution_log(),
        markdown_content=markdown_content,
        docker_compose_yaml=docker_compose_yaml,
        docker_services=docker_services,
        docker_logs=docker_logs
    )

@app.route('/save_code', methods=['POST'])
def save_code():
    """Zapisuje zmiany w kodzie funkcji"""
    data = request.json
    func_name = data.get('function_name')
    code = data.get('code')
    
    if not func_name or not code or func_name not in function_registry:
        return jsonify({'success': False, 'error': 'Nieprawidłowe dane'})
    
    try:
        # W prawdziwej aplikacji tutaj zapisalibyśmy kod do pliku
        # i przeładowali funkcję, ale dla uproszczenia tylko aktualizujemy
        # źródło w rejestrze
        function_registry[func_name]['source'] = code
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == "__main__":
    print(f"Uruchamianie serwera na http://localhost:5050")
    app.run(host='0.0.0.0', port=5050, debug=True)
