// Smart Editor - Main JavaScript File

// Inicjalizacja edytora CodeMirror dla kodu Python
function initCodeEditor(elementId) {
    return CodeMirror.fromTextArea(document.getElementById(elementId), {
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
}

// Inicjalizacja edytora CodeMirror dla konfiguracji Docker
function initDockerEditor(elementId) {
    return CodeMirror.fromTextArea(document.getElementById(elementId), {
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
}

// Funkcja do przełączania layoutu
function changeLayout() {
    const layoutType = document.getElementById("layout-select").value;
    window.location.href = "/?layout=" + layoutType;
}

// Funkcja do przełączania zakładek
function openTab(evt, tabName) {
    const tabcontent = document.getElementsByClassName("tab-content");
    for (let i = 0; i < tabcontent.length; i++) {
        tabcontent[i].className = tabcontent[i].className.replace(" active", "");
    }
    
    const tablinks = document.getElementsByClassName("tab");
    for (let i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    
    document.getElementById(tabName).className += " active";
    evt.currentTarget.className += " active";
}

// Funkcja do wykonywania komend w konsoli
function executeCommand() {
    const command = document.getElementById("console-input").value;
    if (!command) return;
    
    const consoleOutput = document.getElementById("console-output");
    consoleOutput.innerHTML += `<span style='color: #4CAF50;'>$ ${command}</span>\n`;
    
    // Tutaj można dodać logikę wykonywania komend
    // Na razie tylko symulacja
    if (command === "help") {
        consoleOutput.innerHTML += "Dostępne komendy:\n";
        consoleOutput.innerHTML += "  help - wyświetla pomoc\n";
        consoleOutput.innerHTML += "  run - uruchamia funkcję\n";
        consoleOutput.innerHTML += "  test - testuje funkcję\n";
        consoleOutput.innerHTML += "  deploy - wdraża funkcję\n";
    } else if (command === "run") {
        runCode();
        consoleOutput.innerHTML += "Uruchamianie funkcji...\n";
    } else {
        consoleOutput.innerHTML += `Wykonywanie: ${command}\n`;
        consoleOutput.innerHTML += "Zakończono z kodem wyjścia: 0\n";
    }
    
    document.getElementById("console-input").value = "";
    consoleOutput.scrollTop = consoleOutput.scrollHeight;
}

// Funkcja do generowania kodu na podstawie promptu
function generateCode() {
    const prompt = document.getElementById("prompt-input").value;
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
        window.codeEditor.setValue(data.code);
        window.dockerEditor.setValue(data.docker_config);
        
        // Dodanie informacji do konsoli
        const consoleOutput = document.getElementById("console-output");
        if (consoleOutput) {
            consoleOutput.innerHTML += `<span style='color: #4CAF50;'>[INFO] Wygenerowano kod dla: ${prompt}</span>\n`;
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
        }
        
        // Generowanie przykładowych endpointów
        generateEndpoints(prompt);
    })
    .catch(error => {
        console.error('Błąd:', error);
        alert(`Wystąpił błąd podczas generowania kodu: ${error}`);
    });
}

// Funkcja do generowania przykładowych endpointów
function generateEndpoints(prompt) {
    const endpointsContainer = document.getElementById("endpoints-container");
    if (!endpointsContainer) return;
    
    // Wyczyszczenie poprzednich endpointów
    endpointsContainer.innerHTML = "";
    
    // Generowanie przykładowych endpointów na podstawie promptu
    const functionName = prompt.toLowerCase().replace(/[^a-z0-9]+/g, '-');
    
    // Endpoint GET
    const getEndpoint = document.createElement("div");
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
    const postEndpoint = document.createElement("div");
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
    const consoleOutput = document.getElementById("console-output");
    if (consoleOutput) {
        consoleOutput.innerHTML += `<span style='color: #4CAF50;'>[INFO] Testowanie endpointu: ${method} ${url}</span>\n`;
        consoleOutput.innerHTML += `<span style='color: #4CAF50;'>[INFO] Wysyłanie żądania...</span>\n`;
        consoleOutput.innerHTML += `<span style='color: #4CAF50;'>[INFO] Odpowiedź: 200 OK</span>\n`;
        consoleOutput.innerHTML += `<span style='color: #4CAF50;'>[INFO] Dane: {"status": "success", "data": {"id": 1, "value": "test"}}</span>\n`;
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
    }
    
    // Przełączenie na zakładkę z logami
    const logsTab = document.querySelector('button.tab[onclick*="logs-tab"]');
    if (logsTab) {
        openTab({currentTarget: logsTab}, 'logs-tab');
    }
    
    // Dodanie logów
    const logsOutput = document.getElementById("logs-output");
    if (logsOutput) {
        logsOutput.innerHTML += `[${new Date().toISOString()}] Otrzymano żądanie ${method} ${url}\n`;
        logsOutput.innerHTML += `[${new Date().toISOString()}] Przetwarzanie danych...\n`;
        logsOutput.innerHTML += `[${new Date().toISOString()}] Odpowiedź wysłana: 200 OK\n`;
        logsOutput.scrollTop = logsOutput.scrollHeight;
    }
}

// Funkcja do zapisywania kodu
function saveCode() {
    const code = window.codeEditor.getValue();
    const prompt = document.getElementById("prompt-input").value;
    
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
        const consoleOutput = document.getElementById("console-output");
        if (consoleOutput) {
            consoleOutput.innerHTML += "<span style='color: #4CAF50;'>[INFO] Kod zapisany pomyślnie!</span>\n";
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
        }
        
        loadFunctionList();
    })
    .catch(error => {
        console.error('Błąd:', error);
        alert(`Wystąpił błąd podczas zapisywania kodu: ${error}`);
    });
}

// Funkcja do uruchamiania kodu
function runCode() {
    const code = window.codeEditor.getValue();
    
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
        const consoleOutput = document.getElementById("console-output");
        if (consoleOutput) {
            consoleOutput.innerHTML += "<span style='color: #4CAF50;'>[INFO] Wynik wykonania:</span>\n";
            consoleOutput.innerHTML += data.result + "\n";
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
        }
    })
    .catch(error => {
        console.error('Błąd:', error);
        alert(`Wystąpił błąd podczas uruchamiania kodu: ${error}`);
    });
}

// Funkcja do wczytywania listy funkcji
function loadFunctionList() {
    fetch('/function-list')
    .then(response => response.json())
    .then(data => {
        const functionList = document.getElementById("function-list");
        if (!functionList) return;
        
        functionList.innerHTML = "";
        
        data.functions.forEach(func => {
            const functionItem = document.createElement("div");
            functionItem.className = "function-item";
            functionItem.onclick = function() {
                loadFunction(func.name);
            };
            
            const functionName = document.createElement("div");
            functionName.className = "function-name";
            functionName.textContent = func.name;
            
            const functionDescription = document.createElement("div");
            functionDescription.className = "function-description";
            functionDescription.textContent = func.description;
            
            functionItem.appendChild(functionName);
            functionItem.appendChild(functionDescription);
            functionList.appendChild(functionItem);
        });
    })
    .catch(error => {
        console.error('Błąd:', error);
        alert(`Wystąpił błąd podczas wczytywania listy funkcji: ${error}`);
    });
}

// Funkcja do wczytywania konkretnej funkcji
function loadFunction(functionName) {
    fetch('/function/' + functionName)
    .then(response => response.json())
    .then(data => {
        window.codeEditor.setValue(data.code);
        
        const promptInput = document.getElementById("prompt-input");
        if (promptInput) {
            promptInput.value = data.prompt;
        }
        
        window.dockerEditor.setValue(data.docker_config);
        
        // Dodanie informacji do konsoli
        const consoleOutput = document.getElementById("console-output");
        if (consoleOutput) {
            consoleOutput.innerHTML += `<span style='color: #4CAF50;'>[INFO] Wczytano funkcję: ${functionName}</span>\n`;
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
        }
        
        // Generowanie endpointów
        generateEndpoints(data.prompt);
    })
    .catch(error => {
        console.error('Błąd:', error);
        alert(`Wystąpił błąd podczas wczytywania funkcji: ${error}`);
    });
}

// Funkcja do nasłuchiwania logów
function startLogStream() {
    const logsOutput = document.getElementById("logs-output");
    if (!logsOutput) return;
    
    const eventSource = new EventSource('/log-stream');
    
    eventSource.onmessage = function(event) {
        logsOutput.innerHTML += event.data + "\n";
        logsOutput.scrollTop = logsOutput.scrollHeight;
    };
    
    eventSource.onerror = function() {
        eventSource.close();
        setTimeout(startLogStream, 1000);
    };
}

// Funkcja do tworzenia nowej funkcji
function newFunction() {
    const promptInput = document.getElementById("prompt-input");
    if (promptInput) {
        promptInput.value = "";
    }
    
    window.codeEditor.setValue("");
    window.dockerEditor.setValue("");
    
    const endpointsContainer = document.getElementById("endpoints-container");
    if (endpointsContainer) {
        endpointsContainer.innerHTML = "";
    }
}

// Funkcja do uruchamiania testów
function runTests() {
    const consoleOutput = document.getElementById("console-output");
    if (consoleOutput) {
        consoleOutput.innerHTML += "<span style='color: #4CAF50;'>[INFO] Uruchamianie testów...</span>\n";
        consoleOutput.innerHTML += "<span style='color: #4CAF50;'>[INFO] Testy zakończone pomyślnie!</span>\n";
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
    }
}

// Funkcja do wdrażania funkcji
function deployFunction() {
    const consoleOutput = document.getElementById("console-output");
    if (consoleOutput) {
        consoleOutput.innerHTML += "<span style='color: #4CAF50;'>[INFO] Wdrażanie funkcji...</span>\n";
        consoleOutput.innerHTML += "<span style='color: #4CAF50;'>[INFO] Funkcja wdrożona pomyślnie!</span>\n";
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
    }
}

// Funkcja do filtrowania logów
function filterLogs(level) {
    const logFilters = document.getElementsByClassName("log-filter");
    for (let i = 0; i < logFilters.length; i++) {
        logFilters[i].classList.remove("active");
    }
    
    document.getElementById(`filter-${level}`).classList.add("active");
    
    const logEntries = document.getElementsByClassName("log-entry");
    for (let i = 0; i < logEntries.length; i++) {
        if (level === "all" || logEntries[i].classList.contains(level)) {
            logEntries[i].style.display = "block";
        } else {
            logEntries[i].style.display = "none";
        }
    }
}

// Funkcja do uruchamiania testu endpointu z formularza
function runEndpointTest() {
    const method = document.getElementById("endpoint-method").value;
    const url = document.getElementById("endpoint-url").value;
    const headers = document.getElementById("endpoint-headers").value;
    const body = document.getElementById("endpoint-body").value;
    
    const resultOutput = document.getElementById("endpoint-result");
    resultOutput.innerHTML = `<div class="test-result">
        <div class="test-result-header">
            <span class="test-result-name">${method} ${url}</span>
            <span class="test-result-time">${new Date().toLocaleTimeString()}</span>
        </div>
        <div class="test-result-details">
REQUEST:
${method} ${url}
${headers}

${body}

RESPONSE:
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "success",
  "data": {
    "id": 1,
    "value": "test"
  }
}
        </div>
    </div>` + resultOutput.innerHTML;
    
    // Dodanie logów
    const logsOutput = document.getElementById("logs-output");
    if (logsOutput) {
        logsOutput.innerHTML += `[${new Date().toISOString()}] Otrzymano żądanie ${method} ${url}\n`;
        logsOutput.innerHTML += `[${new Date().toISOString()}] Przetwarzanie danych...\n`;
        logsOutput.innerHTML += `[${new Date().toISOString()}] Odpowiedź wysłana: 200 OK\n`;
        logsOutput.scrollTop = logsOutput.scrollHeight;
    }
}

// Funkcja do wczytywania listy przykładów
function loadExamples() {
    fetch('/examples')
        .then(response => response.json())
        .then(data => {
            const examplesContainer = document.getElementById('examples-container');
            if (!examplesContainer) return;
            
            displayExamples(data, examplesContainer);
        })
        .catch(error => {
            console.error('Błąd podczas wczytywania przykładów:', error);
            const examplesContainer = document.getElementById('examples-container');
            if (examplesContainer) {
                examplesContainer.innerHTML = '<div class="error-message">Nie udało się wczytać przykładów</div>';
            }
        });
}

// Funkcja do wyświetlania przykładów
function displayExamples(data, container) {
    container.innerHTML = '';
    
    // Wyświetl przykłady pogrupowane według kategorii
    const categories = data.categories || {};
    
    for (const category in categories) {
        const categoryDiv = document.createElement('div');
        categoryDiv.className = 'example-category';
        
        const categoryTitle = document.createElement('div');
        categoryTitle.className = 'category-title';
        categoryTitle.textContent = category;
        categoryDiv.appendChild(categoryTitle);
        
        const examples = categories[category] || [];
        
        for (const exampleName of examples) {
            const example = data.examples[exampleName];
            if (!example) continue;
            
            const exampleDiv = document.createElement('div');
            exampleDiv.className = 'example-item';
            
            const exampleNameDiv = document.createElement('div');
            exampleNameDiv.className = 'example-name';
            exampleNameDiv.textContent = example.name;
            exampleDiv.appendChild(exampleNameDiv);
            
            const exampleDescDiv = document.createElement('div');
            exampleDescDiv.className = 'example-description';
            exampleDescDiv.textContent = example.description;
            exampleDiv.appendChild(exampleDescDiv);
            
            const exampleActionsDiv = document.createElement('div');
            exampleActionsDiv.className = 'example-actions';
            
            const runButton = document.createElement('button');
            runButton.className = 'button';
            runButton.textContent = 'Uruchom';
            runButton.onclick = function() {
                runExample(example.name);
            };
            exampleActionsDiv.appendChild(runButton);
            
            const viewButton = document.createElement('button');
            viewButton.className = 'button secondary';
            viewButton.textContent = 'Pokaż kod';
            viewButton.onclick = function() {
                viewExampleCode(example.path);
            };
            exampleActionsDiv.appendChild(viewButton);
            
            exampleDiv.appendChild(exampleActionsDiv);
            categoryDiv.appendChild(exampleDiv);
        }
        
        container.appendChild(categoryDiv);
    }
    
    // Jeśli nie ma przykładów, wyświetl komunikat
    if (Object.keys(categories).length === 0) {
        container.innerHTML = '<div class="error-message">Brak dostępnych przykładów</div>';
    }
}

// Funkcja do uruchamiania przykładu
function runExample(exampleName) {
    const consoleOutput = document.getElementById('console-output');
    if (consoleOutput) {
        consoleOutput.innerHTML += `<span style='color: #4CAF50;'>[INFO] Uruchamianie przykładu: ${exampleName}</span>\n`;
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
    }
    
    fetch('/run-example', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: exampleName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (consoleOutput) {
            if (data.error) {
                consoleOutput.innerHTML += `<span style='color: #e74c3c;'>[ERROR] ${data.error}</span>\n`;
            } else {
                consoleOutput.innerHTML += `<span style='color: #4CAF50;'>[INFO] ${data.result}</span>\n`;
            }
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
        }
    })
    .catch(error => {
        if (consoleOutput) {
            consoleOutput.innerHTML += `<span style='color: #e74c3c;'>[ERROR] Błąd podczas uruchamiania przykładu: ${error}</span>\n`;
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
        }
    });
}

// Funkcja do wyświetlania kodu przykładu
function viewExampleCode(examplePath) {
    fetch(examplePath)
        .then(response => {
            if (!response.ok) {
                throw new Error('Nie udało się pobrać kodu przykładu');
            }
            return response.text();
        })
        .then(code => {
            if (window.codeEditor) {
                window.codeEditor.setValue(code);
                
                // Przełącz na zakładkę z kodem
                const codePanel = document.querySelector('.panel:nth-child(2)');
                if (codePanel) {
                    codePanel.scrollIntoView({ behavior: 'smooth' });
                }
            }
        })
        .catch(error => {
            const consoleOutput = document.getElementById('console-output');
            if (consoleOutput) {
                consoleOutput.innerHTML += `<span style='color: #e74c3c;'>[ERROR] ${error.message}</span>\n`;
                consoleOutput.scrollTop = consoleOutput.scrollHeight;
            }
        });
}

// Inicjalizacja po załadowaniu strony
document.addEventListener("DOMContentLoaded", function() {
    // Inicjalizacja edytorów
    const codeEditorElement = document.getElementById("code-editor");
    if (codeEditorElement) {
        window.codeEditor = initCodeEditor("code-editor");
    }
    
    const dockerEditorElement = document.getElementById("docker-editor");
    if (dockerEditorElement) {
        window.dockerEditor = initDockerEditor("docker-editor");
    }
    
    // Dodanie obsługi przycisków
    const saveBtn = document.getElementById("save-btn");
    if (saveBtn) {
        saveBtn.addEventListener("click", saveCode);
    }
    
    const runBtn = document.getElementById("run-btn");
    if (runBtn) {
        runBtn.addEventListener("click", runCode);
    }
    
    const testBtn = document.getElementById("test-btn");
    if (testBtn) {
        testBtn.addEventListener("click", runTests);
    }
    
    const deployBtn = document.getElementById("deploy-btn");
    if (deployBtn) {
        deployBtn.addEventListener("click", deployFunction);
    }
    
    const newFunctionBtn = document.getElementById("new-function-btn");
    if (newFunctionBtn) {
        newFunctionBtn.addEventListener("click", newFunction);
    }
    
    // Wczytanie listy funkcji
    loadFunctionList();
    
    // Wczytanie listy przykładów
    loadExamples();
    
    // Uruchomienie strumienia logów
    startLogStream();
    
    // Obsługa klawisza Enter w konsoli
    const consoleInput = document.getElementById("console-input");
    if (consoleInput) {
        consoleInput.addEventListener("keyup", function(event) {
            if (event.key === "Enter") {
                executeCommand();
            }
        });
    }
    
    // Obsługa klawisza Enter w polu promptu
    const promptInput = document.getElementById("prompt-input");
    if (promptInput) {
        promptInput.addEventListener("keyup", function(event) {
            if (event.key === "Enter") {
                generateCode();
            }
        });
    }
    
    // Dodatkowa inicjalizacja dla układu matrix
    const mainContainer = document.querySelector('.main');
    if (mainContainer && mainContainer.classList.contains('grid')) {
        // Funkcja do automatycznego dostosowywania rozmiaru paneli
        function resizePanels() {
            const windowHeight = window.innerHeight;
            const headerHeight = document.querySelector('.header').offsetHeight;
            
            // Ustaw wysokość głównego kontenera
            mainContainer.style.height = `${windowHeight - headerHeight - 10}px`;
        }
        
        // Wywołaj funkcję przy załadowaniu i zmianie rozmiaru okna
        resizePanels();
        window.addEventListener('resize', resizePanels);
    }
});

// Funkcja do obsługi błędów
window.onerror = function(message, source, lineno, colno, error) {
    console.error("Błąd JavaScript:", message, "w", source, "linia:", lineno);
    const consoleOutput = document.getElementById("console-output");
    if (consoleOutput) {
        consoleOutput.innerHTML += `<span style='color: red;'>[ERROR] ${message} (${source}:${lineno})</span>\n`;
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
    }
};
