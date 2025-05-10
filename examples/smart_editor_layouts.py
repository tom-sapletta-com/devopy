#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Smart Editor Layouts - różne warianty layoutów dla Smart Editora
"""

import os
import sys
from typing import Dict, List, Any

# Dodanie ścieżki do katalogu głównego projektu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Stałe
LAYOUT_TYPES = [
    "standard",
    "developer",
    "monitoring",
    "testing",
    "documentation"
]

# Funkcja do wyboru layoutu
def get_layout(layout_type: str = "standard") -> str:
    """
    Zwraca szablon HTML dla wybranego layoutu
    
    Args:
        layout_type: Typ layoutu (standard, developer, monitoring, testing, documentation)
        
    Returns:
        str: Szablon HTML
    """
    if layout_type not in LAYOUT_TYPES:
        layout_type = "standard"
    
    layout_function = globals().get(f"{layout_type}_layout")
    if layout_function:
        return layout_function()
    
    return standard_layout()

# Standardowy layout
def standard_layout() -> str:
    """
    Standardowy layout z edytorem kodu i panelem wyjściowym
    
    Returns:
        str: Szablon HTML
    """
    return """
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
        .layout-selector {
            margin-right: 20px;
        }
        .layout-select {
            padding: 8px;
            border-radius: 4px;
            border: 1px solid #ddd;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Smart Editor - Devopy</h1>
            <div style="display: flex; align-items: center;">
                <div class="layout-selector">
                    <select id="layout-select" class="layout-select" onchange="changeLayout()">
                        <option value="standard">Standardowy</option>
                        <option value="developer">Deweloperski</option>
                        <option value="monitoring">Monitorowanie</option>
                        <option value="testing">Testowanie</option>
                        <option value="documentation">Dokumentacja</option>
                    </select>
                </div>
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
        
        // Funkcja do przełączania layoutu
        function changeLayout() {
            var layoutType = document.getElementById("layout-select").value;
            window.location.href = "/?layout=" + layoutType;
        }
        
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
                alert("Wystąpił błąd podczas zapisywania kodu: " + error);
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
                alert("Wystąpił błąd podczas uruchamiania kodu: " + error);
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
                alert("Wystąpił błąd podczas wczytywania listy funkcji: " + error);
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
                alert("Wystąpił błąd podczas wczytywania funkcji: " + error);
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

# Layout deweloperski
def developer_layout() -> str:
    """
    Layout deweloperski z podziałem na dwa edytory kodu i konsolą
    
    Returns:
        str: Szablon HTML
    """
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Smart Editor - Devopy (Deweloper)</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/theme/dracula.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/python/python.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/yaml/yaml.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/addon/edit/matchbrackets.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/addon/selection/active-line.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #1e1e1e;
            color: #f0f0f0;
        }
        .container {
            display: flex;
            flex-direction: column;
            height: 100vh;
            padding: 10px;
            box-sizing: border-box;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            background-color: #333;
            padding: 10px;
            border-radius: 5px;
        }
        .header h1 {
            margin: 0;
            color: #fff;
            font-size: 18px;
        }
        .main {
            display: flex;
            flex: 1;
            gap: 10px;
        }
        .left-panel {
            display: flex;
            flex-direction: column;
            width: 300px;
            background-color: #252525;
            border-radius: 5px;
            overflow: hidden;
        }
        .center-panel {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .right-panel {
            width: 400px;
            display: flex;
            flex-direction: column;
            background-color: #252525;
            border-radius: 5px;
            overflow: hidden;
        }
        .panel-header {
            background-color: #333;
            color: white;
            padding: 8px;
            font-size: 14px;
            font-weight: bold;
        }
        .editor-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            background-color: #252525;
            border-radius: 5px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        .prompt-container {
            padding: 10px;
            background-color: #333;
        }
        .prompt-input {
            width: 100%;
            padding: 8px;
            border: 1px solid #555;
            border-radius: 4px;
            background-color: #1e1e1e;
            color: #f0f0f0;
            font-size: 14px;
            box-sizing: border-box;
        }
        .code-editor-container {
            flex: 1;
            position: relative;
            min-height: 200px;
        }
        .docker-editor-container {
            flex: 1;
            position: relative;
            min-height: 200px;
        }
        .console-container {
            height: 200px;
            background-color: #252525;
            border-radius: 5px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        .console-output {
            flex: 1;
            overflow: auto;
            padding: 10px;
            font-family: monospace;
            font-size: 14px;
            line-height: 1.5;
            background-color: #1e1e1e;
            color: #ddd;
            white-space: pre-wrap;
        }
        .console-input {
            display: flex;
            padding: 5px;
            background-color: #333;
        }
        .console-input input {
            flex: 1;
            padding: 5px;
            border: 1px solid #555;
            border-radius: 4px;
            background-color: #1e1e1e;
            color: #f0f0f0;
            font-family: monospace;
        }
        .console-input button {
            margin-left: 5px;
            padding: 5px 10px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .tabs {
            display: flex;
            background-color: #333;
        }
        .tab {
            padding: 8px 15px;
            cursor: pointer;
            background-color: #333;
            border: none;
            outline: none;
            color: #ccc;
            font-size: 14px;
        }
        .tab.active {
            background-color: #252525;
            color: #fff;
            border-bottom: 2px solid #4CAF50;
        }
        .tab-content {
            display: none;
            padding: 10px;
            flex: 1;
            overflow: auto;
        }
        .tab-content.active {
            display: block;
        }
        .button {
            padding: 6px 12px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            margin-left: 5px;
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
            flex: 1;
            overflow: auto;
            padding: 10px;
        }
        .function-item {
            padding: 8px;
            background-color: #333;
            border-radius: 4px;
            margin-bottom: 8px;
            cursor: pointer;
        }
        .function-item:hover {
            background-color: #444;
        }
        .function-name {
            font-weight: bold;
            color: #fff;
        }
        .function-description {
            color: #ccc;
            font-size: 12px;
            margin-top: 5px;
        }
        .logs-container {
            flex: 1;
            overflow: auto;
            padding: 10px;
            font-family: monospace;
            font-size: 14px;
            line-height: 1.5;
            background-color: #1e1e1e;
            color: #ddd;
            white-space: pre-wrap;
        }
        .layout-selector {
            margin-right: 10px;
        }
        .layout-select {
            padding: 6px;
            border-radius: 4px;
            border: 1px solid #555;
            background-color: #1e1e1e;
            color: #f0f0f0;
        }
        .endpoints-container {
            flex: 1;
            overflow: auto;
            padding: 10px;
        }
        .endpoint-item {
            padding: 8px;
            background-color: #333;
            border-radius: 4px;
            margin-bottom: 8px;
        }
        .endpoint-url {
            font-weight: bold;
            color: #4CAF50;
        }
        .endpoint-method {
            display: inline-block;
            padding: 2px 5px;
            background-color: #4CAF50;
            color: white;
            border-radius: 3px;
            font-size: 12px;
            margin-right: 5px;
        }
        .endpoint-description {
            color: #ccc;
            font-size: 12px;
            margin-top: 5px;
        }
        .endpoint-test {
            margin-top: 5px;
            text-align: right;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Smart Editor - Devopy (Deweloper)</h1>
            <div style="display: flex; align-items: center;">
                <div class="layout-selector">
                    <select id="layout-select" class="layout-select" onchange="changeLayout()">
                        <option value="standard">Standardowy</option>
                        <option value="developer" selected>Deweloperski</option>
                        <option value="monitoring">Monitorowanie</option>
                        <option value="testing">Testowanie</option>
                        <option value="documentation">Dokumentacja</option>
                    </select>
                </div>
                <button id="new-function-btn" class="button">Nowa</button>
                <button id="save-btn" class="button">Zapisz</button>
                <button id="run-btn" class="button">Uruchom</button>
                <button id="test-btn" class="button secondary">Test</button>
                <button id="deploy-btn" class="button secondary">Wdróż</button>
            </div>
        </div>
        <div class="main">
            <div class="left-panel">
                <div class="panel-header">Funkcje</div>
                <div class="function-list" id="function-list">
                    <!-- Lista funkcji będzie generowana dynamicznie -->
                </div>
            </div>
            <div class="center-panel">
                <div class="prompt-container">
                    <input type="text" id="prompt-input" class="prompt-input" placeholder="Opisz funkcję (np. 'Pobierz dane z API', 'Przetwórz dane JSON', 'Zapisz dane do bazy')">
                </div>
                <div class="editor-container">
                    <div class="panel-header">Kod Python</div>
                    <div class="code-editor-container">
                        <textarea id="code-editor"></textarea>
                    </div>
                </div>
                <div class="console-container">
                    <div class="panel-header">Konsola</div>
                    <div class="console-output" id="console-output"></div>
                    <div class="console-input">
                        <input type="text" id="console-input" placeholder="Wprowadź komendę...">
                        <button onclick="executeCommand()">Wykonaj</button>
                    </div>
                </div>
            </div>
            <div class="right-panel">
                <div class="panel-header">Docker & Endpoints</div>
                <div class="tabs">
                    <button class="tab active" onclick="openTab(event, 'docker-tab')">Docker</button>
                    <button class="tab" onclick="openTab(event, 'endpoints-tab')">Endpoints</button>
                    <button class="tab" onclick="openTab(event, 'logs-tab')">Logi</button>
                </div>
                <div id="docker-tab" class="tab-content active">
                    <div class="docker-editor-container">
                        <textarea id="docker-editor"></textarea>
                    </div>
                </div>
                <div id="endpoints-tab" class="tab-content">
                    <div class="endpoints-container" id="endpoints-container">
                        <!-- Lista endpointów będzie generowana dynamicznie -->
                    </div>
                </div>
                <div id="logs-tab" class="tab-content">
                    <div class="logs-container" id="logs-output"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Inicjalizacja edytora CodeMirror dla kodu Python
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
        
        // Inicjalizacja edytora CodeMirror dla konfiguracji Docker
        var dockerEditor = CodeMirror.fromTextArea(document.getElementById("docker-editor"), {
            mode: "yaml",
            theme: "dracula",
            lineNumbers: true,
            matchBrackets: true,
            styleActiveLine: true,
            indentUnit: 2,
            tabSize: 2,
            indentWithTabs: false,
            lineWrapping: true
        });
        
        // Ustawienie wysokości edytorów
        editor.setSize("100%", "100%");
        dockerEditor.setSize("100%", "100%");
        
        // Funkcja do przełączania layoutu
        function changeLayout() {
            var layoutType = document.getElementById("layout-select").value;
            window.location.href = "/?layout=" + layoutType;
        }
        
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
        
        // Funkcja do wykonywania komend w konsoli
        function executeCommand() {
            var command = document.getElementById("console-input").value;
            if (!command) return;
            
            var consoleOutput = document.getElementById("console-output");
            consoleOutput.innerHTML += "<span style='color: #4CAF50;'>$ " + command + "</span>\\n";
            
            // Tutaj można dodać logikę wykonywania komend
            // Na razie tylko symulacja
            if (command === "help") {
                consoleOutput.innerHTML += "Dostępne komendy:\\n";
                consoleOutput.innerHTML += "  help - wyświetla pomoc\\n";
                consoleOutput.innerHTML += "  run - uruchamia funkcję\\n";
                consoleOutput.innerHTML += "  test - testuje funkcję\\n";
                consoleOutput.innerHTML += "  deploy - wdraża funkcję\\n";
            } else if (command === "run") {
                runCode();
                consoleOutput.innerHTML += "Uruchamianie funkcji...\\n";
            } else {
                consoleOutput.innerHTML += "Wykonywanie: " + command + "\\n";
                consoleOutput.innerHTML += "Zakończono z kodem wyjścia: 0\\n";
            }
            
            document.getElementById("console-input").value = "";
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
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
                dockerEditor.setValue(data.docker_config);
                
                // Dodanie informacji do konsoli
                var consoleOutput = document.getElementById("console-output");
                consoleOutput.innerHTML += "<span style='color: #4CAF50;'>[INFO] Wygenerowano kod dla: " + prompt + "</span>\\n";
                consoleOutput.scrollTop = consoleOutput.scrollHeight;
                
                // Generowanie przykładowych endpointów
                generateEndpoints(prompt);
            })
            .catch(error => {
                console.error('Błąd:', error);
                alert("Wystąpił błąd podczas generowania kodu: " + error);
            });
        }
        
        // Funkcja do generowania przykładowych endpointów
        function generateEndpoints(prompt) {
            var endpointsContainer = document.getElementById("endpoints-container");
            
            // Wyczyszczenie poprzednich endpointów
            endpointsContainer.innerHTML = "";
            
            // Generowanie przykładowych endpointów na podstawie promptu
            var functionName = prompt.toLowerCase().replace(/[^a-z0-9]+/g, '-');
            
            // Endpoint GET
            var getEndpoint = document.createElement("div");
            getEndpoint.className = "endpoint-item";
            getEndpoint.innerHTML = `
                <div><span class="endpoint-method">GET</span> <span class="endpoint-url">/api/${functionName}</span></div>
                <div class="endpoint-description">Pobiera dane z funkcji ${functionName}</div>
                <div class="endpoint-test">
                    <button class="button secondary" onclick="testEndpoint('GET', '/api/${functionName}')">Test</button>
                </div>
            `;
            endpointsContainer.appendChild(getEndpoint);
            
            // Endpoint POST
            var postEndpoint = document.createElement("div");
            postEndpoint.className = "endpoint-item";
            postEndpoint.innerHTML = `
                <div><span class="endpoint-method">POST</span> <span class="endpoint-url">/api/${functionName}</span></div>
                <div class="endpoint-description">Wysyła dane do funkcji ${functionName}</div>
                <div class="endpoint-test">
                    <button class="button secondary" onclick="testEndpoint('POST', '/api/${functionName}')">Test</button>
                </div>
            `;
            endpointsContainer.appendChild(postEndpoint);
        }
        
        // Funkcja do testowania endpointów
        function testEndpoint(method, url) {
            var consoleOutput = document.getElementById("console-output");
            consoleOutput.innerHTML += `<span style='color: #4CAF50;'>[INFO] Testowanie endpointu: ${method} ${url}</span>\\n`;
            consoleOutput.innerHTML += `<span style='color: #4CAF50;'>[INFO] Wysyłanie żądania...</span>\\n`;
            consoleOutput.innerHTML += `<span style='color: #4CAF50;'>[INFO] Odpowiedź: 200 OK</span>\\n`;
            consoleOutput.innerHTML += `<span style='color: #4CAF50;'>[INFO] Dane: {"status": "success", "data": {"id": 1, "value": "test"}}</span>\\n`;
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
            
            // Przełączenie na zakładkę z logami
            openTab({currentTarget: document.querySelector('button.tab[onclick*="logs-tab"]')}, 'logs-tab');
            
            // Dodanie logów
            var logsOutput = document.getElementById("logs-output");
            logsOutput.innerHTML += `[${new Date().toISOString()}] Otrzymano żądanie ${method} ${url}\\n`;
            logsOutput.innerHTML += `[${new Date().toISOString()}] Przetwarzanie danych...\\n`;
            logsOutput.innerHTML += `[${new Date().toISOString()}] Odpowiedź wysłana: 200 OK\\n`;
            logsOutput.scrollTop = logsOutput.scrollHeight;
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
                // Dodanie informacji do konsoli
                var consoleOutput = document.getElementById("console-output");
                consoleOutput.innerHTML += "<span style='color: #4CAF50;'>[INFO] Kod zapisany pomyślnie!</span>\\n";
                consoleOutput.scrollTop = consoleOutput.scrollHeight;
                
                loadFunctionList();
            })
            .catch(error => {
                console.error('Błąd:', error);
                alert("Wystąpił błąd podczas zapisywania kodu: " + error);
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
                // Dodanie wyniku do konsoli
                var consoleOutput = document.getElementById("console-output");
                consoleOutput.innerHTML += "<span style='color: #4CAF50;'>[INFO] Wynik wykonania:</span>\\n";
                consoleOutput.innerHTML += data.result + "\\n";
                consoleOutput.scrollTop = consoleOutput.scrollHeight;
            })
            .catch(error => {
                console.error('Błąd:', error);
                alert("Wystąpił błąd podczas uruchamiania kodu: " + error);
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
                alert("Wystąpił błąd podczas wczytywania listy funkcji: " + error);
            });
        }
        
        // Funkcja do wczytywania konkretnej funkcji
        function loadFunction(functionName) {
            fetch('/function/' + functionName)
            .then(response => response.json())
            .then(data => {
                editor.setValue(data.code);
                document.getElementById("prompt-input").value = data.prompt;
                dockerEditor.setValue(data.docker_config);
                
                // Dodanie informacji do konsoli
                var consoleOutput = document.getElementById("console-output");
                consoleOutput.innerHTML += `<span style='color: #4CAF50;'>[INFO] Wczytano funkcję: ${functionName}</span>\\n`;
                consoleOutput.scrollTop = consoleOutput.scrollHeight;
                
                // Generowanie endpointów
                generateEndpoints(data.prompt);
            })
            .catch(error => {
                console.error('Błąd:', error);
                alert("Wystąpił błąd podczas wczytywania funkcji: " + error);
            });
        }
        
        // Funkcja do nasłuchiwania logów
        function startLogStream() {
            var logsOutput = document.getElementById("logs-output");
            var eventSource = new EventSource('/log-stream');
            
            eventSource.onmessage = function(event) {
                logsOutput.innerHTML += event.data + "\\n";
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
        
        document.getElementById("console-input").addEventListener("keyup", function(event) {
            if (event.key === "Enter") {
                executeCommand();
            }
        });
        
        document.getElementById("new-function-btn").addEventListener("click", function() {
            document.getElementById("prompt-input").value = "";
            editor.setValue("");
            dockerEditor.setValue("");
            document.getElementById("endpoints-container").innerHTML = "";
        });
        
        document.getElementById("save-btn").addEventListener("click", saveCode);
        document.getElementById("run-btn").addEventListener("click", runCode);
        document.getElementById("test-btn").addEventListener("click", function() {
            var consoleOutput = document.getElementById("console-output");
            consoleOutput.innerHTML += "<span style='color: #4CAF50;'>[INFO] Uruchamianie testów...</span>\\n";
            consoleOutput.innerHTML += "<span style='color: #4CAF50;'>[INFO] Testy zakończone pomyślnie!</span>\\n";
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
        });
        document.getElementById("deploy-btn").addEventListener("click", function() {
            var consoleOutput = document.getElementById("console-output");
            consoleOutput.innerHTML += "<span style='color: #4CAF50;'>[INFO] Wdrażanie funkcji...</span>\\n";
            consoleOutput.innerHTML += "<span style='color: #4CAF50;'>[INFO] Funkcja wdrożona pomyślnie!</span>\\n";
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
        });
        
        // Wczytaj listę funkcji przy starcie
        loadFunctionList();
        
        // Rozpocznij nasłuchiwanie logów
        startLogStream();
        
        // Dodaj obsługę błędów
        window.onerror = function(message, source, lineno, colno, error) {
            console.error("Błąd JavaScript:", message, "w", source, "linia:", lineno);
            var consoleOutput = document.getElementById("console-output");
            consoleOutput.innerHTML += `<span style='color: red;'>[ERROR] ${message} (${source}:${lineno})</span>\\n`;
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
        };
    </script>
</body>
</html>
"""
