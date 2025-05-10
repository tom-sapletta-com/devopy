// Stan aplikacji
const state = {
    currentFile: 'main.py',
    files: {
        'main.py': '# Witaj w edytorze Devopy Docker!\n# Napisz swój kod Python tutaj i kliknij "Uruchom"\n\nprint("Hello, World!")\n'
    },
    matrixMode: false,
    expandedPanel: null,
    menuData: null,
    currentMode: 'development',
    panelContents: {
        development: {
            'media-panel': { title: 'Okno Mediów (Dev)', content: '<ul class="file-list" id="file-list"><li class="active" data-file="main.py">main.py</li></ul>' },
            'edit-panel': { title: 'Okno Edycji (Dev)', content: '<div class="tab-container"><div class="tab active" data-panel="code-panel">Kod</div><div class="tab" data-panel="command-panel">Polecenia</div></div><div class="panel active" id="code-panel"><textarea id="editor" spellcheck="false"></textarea></div><div class="panel" id="command-panel"><input type="text" id="command-input" placeholder="Wprowadź polecenie bash (np. ls -la)"><button id="run-command-btn">Wykonaj</button></div>' },
            'preview-panel': { title: 'Okno Podglądu (Dev)', content: '<div id="preview-content">Podgląd zaznaczonych mediów w trybie Development.</div>' },
            'communication-panel': { title: 'Okno Komunikacji (Dev)', content: '<pre id="output"></pre><div class="controls"><button id="clear-output-btn">Wyczyść wyjście</button></div>' }
        },
        testing: {
            'media-panel': { title: 'Testy Jednostkowe', content: '<div class="test-list"><h4>Testy do uruchomienia</h4><ul id="test-list"><li>test_main.py</li><li>test_utils.py</li></ul><button id="run-tests-btn" class="action-btn">Uruchom testy</button></div>' },
            'edit-panel': { title: 'Edytor Testów', content: '<div class="tab-container"><div class="tab active" data-panel="test-editor-panel">Edytor testów</div></div><div class="panel active" id="test-editor-panel"><textarea id="test-editor" spellcheck="false">import unittest\n\nclass TestMain(unittest.TestCase):\n    def test_example(self):\n        self.assertTrue(True)\n\nif __name__ == "__main__":\n    unittest.main()\n</textarea></div>' },
            'preview-panel': { title: 'Pokrycie Kodu', content: '<div id="coverage-report"><h4>Raport pokrycia kodu</h4><div class="coverage-stats"><div>Pokrycie: <span class="coverage-value">87%</span></div><div class="coverage-bar"><div class="coverage-fill" style="width: 87%"></div></div></div><div class="file-coverage"><div class="file-item"><span>main.py</span><span>92%</span></div><div class="file-item"><span>utils.py</span><span>82%</span></div></div></div>' },
            'communication-panel': { title: 'Wyniki Testów', content: '<pre id="test-output" class="test-results">Uruchom testy, aby zobaczyć wyniki...</pre>' }
        },
        monitoring: {
            'media-panel': { title: 'Zasoby Systemu', content: '<div class="monitoring-panel"><div class="resource-monitor"><h4>Wykorzystanie CPU</h4><div class="gauge"><div class="gauge-fill" style="width: 45%"></div></div><span>45%</span></div><div class="resource-monitor"><h4>Wykorzystanie RAM</h4><div class="gauge"><div class="gauge-fill" style="width: 60%"></div></div><span>60%</span></div><div class="resource-monitor"><h4>Dysk</h4><div class="gauge"><div class="gauge-fill" style="width: 25%"></div></div><span>25%</span></div></div>' },
            'edit-panel': { title: 'Konfiguracja Monitoringu', content: '<div class="config-editor"><h4>Ustawienia monitoringu</h4><div class="config-form"><div class="form-group"><label>Interwał odświeżania (s)</label><input type="number" value="5" min="1" max="60"></div><div class="form-group"><label>Próg alertu CPU (%)</label><input type="number" value="80" min="1" max="100"></div><div class="form-group"><label>Próg alertu RAM (%)</label><input type="number" value="90" min="1" max="100"></div><button class="save-config-btn">Zapisz ustawienia</button></div></div>' },
            'preview-panel': { title: 'Logi Systemu', content: '<div class="logs-container"><div class="log-controls"><select class="log-level-filter"><option value="all">Wszystkie poziomy</option><option value="error">Błędy</option><option value="warning">Ostrzeżenia</option><option value="info">Informacje</option></select><button class="refresh-logs-btn">Odśwież</button></div><div class="logs-output"><div class="log-entry error"><span class="timestamp">2023-05-10 18:45:23</span><span class="level">ERROR</span><span class="message">Failed to connect to database</span></div><div class="log-entry warning"><span class="timestamp">2023-05-10 18:44:15</span><span class="level">WARNING</span><span class="message">High memory usage detected</span></div><div class="log-entry info"><span class="timestamp">2023-05-10 18:43:01</span><span class="level">INFO</span><span class="message">Application started successfully</span></div></div></div>' },
            'communication-panel': { title: 'Powiadomienia', content: '<div class="notifications-panel"><div class="notification error"><div class="notification-header"><span class="notification-title">Błąd połączenia</span><span class="notification-time">18:45</span></div><div class="notification-body">Nie można połączyć się z bazą danych. Sprawdź konfiguracje połączenia.</div></div><div class="notification warning"><div class="notification-header"><span class="notification-title">Wysokie zużycie pamięci</span><span class="notification-time">18:44</span></div><div class="notification-body">Wykryto wysokie zużycie pamięci (90%). Rozważ restart aplikacji.</div></div></div>' }
        },
        production: {
            'media-panel': { title: 'Status Wdrożenia', content: '<div class="deployment-status"><div class="status-item success"><span class="status-label">Serwer produkcyjny</span><span class="status-value">Online</span></div><div class="status-item success"><span class="status-label">Baza danych</span><span class="status-value">Połączona</span></div><div class="status-item warning"><span class="status-label">Cache Redis</span><span class="status-value">Wysoki load</span></div><div class="deployment-info"><div>Wersja: <strong>v1.2.3</strong></div><div>Ostatnie wdrożenie: <strong>10.05.2023 15:30</strong></div></div></div>' },
            'edit-panel': { title: 'Zarządzanie Wdrożeniem', content: '<div class="deployment-manager"><div class="version-selector"><label>Wybierz wersję do wdrożenia:</label><select><option value="v1.2.4">v1.2.4 (Staging)</option><option value="v1.2.3">v1.2.3 (Produkcja)</option><option value="v1.2.2">v1.2.2</option></select></div><div class="deployment-options"><button class="deploy-btn primary">Wdrożenie</button><button class="deploy-btn rollback">Rollback</button></div><div class="deployment-checklist"><h4>Lista kontrolna wdrożenia</h4><div class="checklist-item"><input type="checkbox" id="check1"><label for="check1">Testy zostały przeprowadzone</label></div><div class="checklist-item"><input type="checkbox" id="check2"><label for="check2">Backup został wykonany</label></div><div class="checklist-item"><input type="checkbox" id="check3"><label for="check3">Dokumentacja została zaktualizowana</label></div></div></div>' },
            'preview-panel': { title: 'Metryki Produkcyjne', content: '<div class="metrics-panel"><div class="metric-card"><h4>Użytkownicy online</h4><div class="metric-value">1,245</div><div class="metric-trend positive">+12% ↑</div></div><div class="metric-card"><h4>Średni czas odpowiedzi</h4><div class="metric-value">235ms</div><div class="metric-trend negative">+15ms ↓</div></div><div class="metric-card"><h4>Błędy / min</h4><div class="metric-value">0.3</div><div class="metric-trend positive">-0.1 ↑</div></div></div>' },
            'communication-panel': { title: 'Alerty Produkcyjne', content: '<div class="alerts-panel"><div class="alert-card warning"><div class="alert-header"><span class="alert-title">Wysoki czas odpowiedzi API</span><span class="alert-time">18:30</span></div><div class="alert-body">Endpoint /api/users wykazuje podwyższony czas odpowiedzi (>500ms)</div><div class="alert-actions"><button class="alert-btn">Szczegóły</button><button class="alert-btn">Ignoruj</button></div></div><div class="alert-card info"><div class="alert-header"><span class="alert-title">Zaplanowana konserwacja</span><span class="alert-time">20:00</span></div><div class="alert-body">Zaplanowana konserwacja bazy danych o 22:00</div><div class="alert-actions"><button class="alert-btn">Szczegóły</button></div></div></div>' }
        }
    }
};

// Elementy DOM
const editor = document.getElementById('editor');
const output = document.getElementById('output');
const fileList = document.getElementById('file-list');
const statusIndicator = document.getElementById('status-indicator');
const statusText = document.getElementById('status-text');
const containerId = document.getElementById('container-id');
const container = document.querySelector('.container');
const matrixContainer = document.querySelector('.matrix-container');

// Matrix panels
const mediaPanel = document.getElementById('media-panel');
const editPanel = document.getElementById('edit-panel');
const previewPanel = document.getElementById('preview-panel');
const communicationPanel = document.getElementById('communication-panel');
const intersectionPoint = document.getElementById('intersection-point');

// Menu elements
const menuOverlay = document.getElementById('menu-overlay');
const mediaMenuList = document.getElementById('media-menu-list');
const editMenuList = document.getElementById('edit-menu-list');
const previewMenuList = document.getElementById('preview-menu-list');
const communicationMenuList = document.getElementById('communication-menu-list');

// Przyciski
const runButton = document.getElementById('run-btn');
const saveButton = document.getElementById('save-btn');
const clearOutputButton = document.getElementById('clear-output-btn');
const newFileButton = document.getElementById('new-file-btn');
const checkStatusButton = document.getElementById('check-status-btn');
const restartButton = document.getElementById('restart-btn');
const runCommandButton = document.getElementById('run-command-btn');
const commandInput = document.getElementById('command-input');
const exampleSelect = document.getElementById('example-select');
const matrixToggleButton = document.getElementById('matrix-toggle-btn');
const panelMaximizeButtons = document.querySelectorAll('.panel-maximize-btn');
const panelHeaders = document.querySelectorAll('.panel-header');

// Zakładki
const tabs = document.querySelectorAll('.tab');
const panels = document.querySelectorAll('.panel');

// Matrix mode functions
function toggleMatrixMode() {
    state.matrixMode = !state.matrixMode;
    
    if (state.matrixMode) {
        matrixToggleButton.textContent = 'Tryb Normalny';
    } else {
        resetPanels();
        matrixToggleButton.textContent = 'Tryb Matrix';
    }
}

function resetPanels() {
    // Reset all panels to their original state
    mediaPanel.classList.remove('panel-expanded', 'panel-minimized');
    editPanel.classList.remove('panel-expanded', 'panel-minimized');
    previewPanel.classList.remove('panel-expanded', 'panel-minimized');
    communicationPanel.classList.remove('panel-expanded', 'panel-minimized');
    state.expandedPanel = null;
}

function togglePanelSize(panel) {
    if (!state.matrixMode) return;
    
    const panelElement = panel.closest('.matrix-panel');
    const panelId = panelElement.id;
    
    if (state.expandedPanel === panelId) {
        // If clicking on already expanded panel, reset all panels
        resetPanels();
    } else {
        // Reset previous expanded panel if any
        resetPanels();
        
        // Minimize all panels
        mediaPanel.classList.add('panel-minimized');
        editPanel.classList.add('panel-minimized');
        previewPanel.classList.add('panel-minimized');
        communicationPanel.classList.add('panel-minimized');
        
        // Expand the clicked panel
        panelElement.classList.remove('panel-minimized');
        panelElement.classList.add('panel-expanded');
        state.expandedPanel = panelId;
    }
}

// Intersection point dragging functionality
function setupIntersectionPoint() {
    let isDragging = false;
    let startX, startY;
    let startLeft, startTop;
    
    intersectionPoint.addEventListener('mousedown', function(e) {
        isDragging = true;
        startX = e.clientX;
        startY = e.clientY;
        
        // Get the current position of the intersection point
        const rect = intersectionPoint.getBoundingClientRect();
        startLeft = rect.left + window.scrollX;
        startTop = rect.top + window.scrollY;
        
        // Add event listeners for dragging
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
        
        // Prevent default behavior
        e.preventDefault();
    });
    
    function onMouseMove(e) {
        if (!isDragging) return;
        
        // Calculate the new position
        const deltaX = e.clientX - startX;
        const deltaY = e.clientY - startY;
        
        // Get the container dimensions
        const containerRect = matrixContainer.getBoundingClientRect();
        
        // Calculate percentage position within the container
        const percentX = ((startLeft + deltaX - containerRect.left) / containerRect.width) * 100;
        const percentY = ((startTop + deltaY - containerRect.top) / containerRect.height) * 100;
        
        // Limit the position to stay within the container (with some margin)
        const limitedX = Math.max(10, Math.min(90, percentX));
        const limitedY = Math.max(10, Math.min(90, percentY));
        
        // Update the grid template
        matrixContainer.style.gridTemplateColumns = `${limitedX}% ${100-limitedX}%`;
        matrixContainer.style.gridTemplateRows = `${limitedY}% ${100-limitedY}%`;
        
        // Update the intersection point position
        intersectionPoint.style.left = `${limitedX}%`;
        intersectionPoint.style.top = `${limitedY}%`;
    }
    
    function onMouseUp() {
        isDragging = false;
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
    }
}

// Menu functionality
function loadMenuData() {
    // Load menu configuration from JSON file
    fetch('/static/config/menu-config.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load menu configuration');
            }
            return response.json();
        })
        .then(data => {
            state.menuData = data;
            
            // Populate the menu lists
            populateMenuList(mediaMenuList, state.menuData.media);
            populateMenuList(editMenuList, state.menuData.edit);
            populateMenuList(previewMenuList, state.menuData.preview);
            populateMenuList(communicationMenuList, state.menuData.communication);
        })
        .catch(error => {
            console.error('Error loading menu configuration:', error);
            // Fallback to default menu data if loading fails
            state.menuData = {
                media: [
                    { id: 'filesystem', name: 'Filesystem' },
                    { id: 'nextcloud', name: 'NextCloud' }
                ],
                edit: [
                    { id: 'code', name: 'Code' },
                    { id: 'nocode', name: 'NoCode' }
                ],
                preview: [
                    { id: 'video-camera', name: 'Video Camera' },
                    { id: '3d-render', name: '3D Render' }
                ],
                communication: [
                    { id: 'chat', name: 'Chat' },
                    { id: 'terminal', name: 'Terminal' }
                ]
            };
            
            // Populate the menu lists with fallback data
            populateMenuList(mediaMenuList, state.menuData.media);
            populateMenuList(editMenuList, state.menuData.edit);
            populateMenuList(previewMenuList, state.menuData.preview);
            populateMenuList(communicationMenuList, state.menuData.communication);
        });
}

function populateMenuList(listElement, items) {
    listElement.innerHTML = '';
    
    items.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item.name;
        li.dataset.id = item.id;
        li.addEventListener('click', function() {
            handleMenuSelect(this.dataset.id, this.textContent, listElement.id);
        });
        listElement.appendChild(li);
    });
}

function handleMenuSelect(id, name, menuListId) {
    // Update the corresponding panel based on the selection
    let panelId;
    
    switch(menuListId) {
        case 'media-menu-list':
            panelId = 'media-panel';
            break;
        case 'edit-menu-list':
            panelId = 'edit-panel';
            break;
        case 'preview-menu-list':
            panelId = 'preview-panel';
            break;
        case 'communication-menu-list':
            panelId = 'communication-panel';
            break;
    }
    
    if (panelId) {
        const panel = document.getElementById(panelId);
        const header = panel.querySelector('.panel-header h3');
        header.textContent = name;
    }
    
    // Hide the menu overlay
    menuOverlay.style.display = 'none';
}

function toggleMenuOverlay() {
    if (menuOverlay.style.display === 'flex') {
        menuOverlay.style.display = 'none';
    } else {
        menuOverlay.style.display = 'flex';
    }
}

// Funkcje pomocnicze
function updateEditor() {
    editor.value = state.files[state.currentFile] || '';
}

function updateFileList() {
    fileList.innerHTML = '';
    
    Object.keys(state.files).forEach(file => {
        const li = document.createElement('li');
        li.textContent = file;
        li.dataset.file = file;
        
        if (file === state.currentFile) {
            li.classList.add('active');
        }
        
        li.addEventListener('click', () => {
            // Zapisz aktualny plik przed przełączeniem
            state.files[state.currentFile] = editor.value;
            
            // Przełącz na nowy plik
            state.currentFile = file;
            
            // Aktualizuj interfejs
            updateFileList();
            updateEditor();
        });
        
        fileList.appendChild(li);
    });
}

function updateStatusIndicator(status) {
    statusIndicator.className = 'status-indicator';
    
    switch (status) {
        case 'ready':
            statusIndicator.classList.add('status-ready');
            statusText.textContent = 'Gotowy';
            break;
        case 'busy':
            statusIndicator.classList.add('status-busy');
            statusText.textContent = 'Zajęty';
            break;
        case 'error':
            statusIndicator.classList.add('status-error');
            statusText.textContent = 'Błąd';
            break;
        default:
            statusText.textContent = 'Nieznany';
    }
}

function appendOutput(text, isError = false) {
    const span = document.createElement('span');
    span.textContent = text;
    
    if (isError) {
        span.style.color = '#e74c3c';
    }
    
    output.appendChild(span);
    output.appendChild(document.createElement('br'));
    output.scrollTop = output.scrollHeight;
}

// Obsługa zdarzeń
runButton.addEventListener('click', function() {
    // Zapisz aktualny plik
    state.files[state.currentFile] = editor.value;
    
    // Zaktualizuj status
    updateStatusIndicator('busy');
    
    // Wyślij kod do wykonania
    fetch('/api/execute-python', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            code: editor.value
        })
    })
    .then(response => response.json())
    .then(data => {
        // Zaktualizuj status
        updateStatusIndicator('ready');
        
        // Wyczyść wyjście
        output.innerHTML = '';
        
        // Wyświetl wynik
        if (data.success) {
            if (data.stdout) {
                appendOutput(data.stdout);
            }
            
            if (data.stderr) {
                appendOutput(data.stderr, true);
            }
        } else {
            appendOutput(`Błąd: ${data.error || 'Nieznany błąd'}`, true);
            
            if (data.stderr) {
                appendOutput(data.stderr, true);
            }
        }
    })
    .catch(error => {
        updateStatusIndicator('error');
        appendOutput(`Błąd: ${error.message}`, true);
    });
});

saveButton.addEventListener('click', function() {
    // Zapisz aktualny plik
    state.files[state.currentFile] = editor.value;
    
    // Wyślij plik do zapisania
    fetch('/api/save-file', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            filename: state.currentFile,
            content: editor.value
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            appendOutput(`Plik ${state.currentFile} zapisany pomyślnie.`);
        } else {
            appendOutput(`Błąd zapisywania pliku: ${data.error}`, true);
        }
    })
    .catch(error => {
        appendOutput(`Błąd: ${error.message}`, true);
    });
});

clearOutputButton.addEventListener('click', function() {
    output.innerHTML = '';
});

newFileButton.addEventListener('click', function() {
    const filename = prompt('Podaj nazwę pliku:');
    
    if (filename && !state.files[filename]) {
        state.files[filename] = '';
        state.currentFile = filename;
        
        updateFileList();
        updateEditor();
    } else if (state.files[filename]) {
        alert('Plik o tej nazwie już istnieje!');
    }
});

checkStatusButton.addEventListener('click', function() {
    fetch('/api/docker-status')
        .then(response => response.json())
        .then(data => {
            if (data.ready) {
                updateStatusIndicator('ready');
                containerId.textContent = data.container_id || '-';
            } else {
                updateStatusIndicator('error');
            }
        })
        .catch(error => {
            updateStatusIndicator('error');
            console.error('Błąd sprawdzania statusu:', error);
        });
});

restartButton.addEventListener('click', function() {
    updateStatusIndicator('busy');
    
    fetch('/api/restart-container', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateStatusIndicator('ready');
            containerId.textContent = data.container_id || '-';
            appendOutput('Kontener Docker zrestartowany pomyślnie.');
        } else {
            updateStatusIndicator('error');
            appendOutput(`Błąd restartowania kontenera: ${data.error}`, true);
        }
    })
    .catch(error => {
        updateStatusIndicator('error');
        appendOutput(`Błąd: ${error.message}`, true);
    });
});

runCommandButton.addEventListener('click', function() {
    const command = commandInput.value.trim();
    
    if (!command) return;
    
    updateStatusIndicator('busy');
    
    fetch('/api/docker-execute', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            command: command
        })
    })
    .then(response => response.json())
    .then(data => {
        updateStatusIndicator('ready');
        
        if (data.success) {
            if (data.stdout) {
                appendOutput(`$ ${command}`);
                appendOutput(data.stdout);
            }
            
            if (data.stderr) {
                appendOutput(data.stderr, true);
            }
        } else {
            appendOutput(`$ ${command}`);
            appendOutput(`Błąd: ${data.error || 'Nieznany błąd'}`, true);
            
            if (data.stderr) {
                appendOutput(data.stderr, true);
            }
        }
    })
    .catch(error => {
        updateStatusIndicator('error');
        appendOutput(`Błąd: ${error.message}`, true);
    });
});

exampleSelect.addEventListener('change', function() {
    const example = this.value;
    
    if (!example) return;
    
    fetch(`/api/get-example?file=${example}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.content) {
                // Dodaj przykład jako nowy plik
                state.files[example] = data.content;
                state.currentFile = example;
                
                updateFileList();
                updateEditor();
            } else {
                appendOutput(`Błąd ładowania przykładu: ${data.error}`, true);
            }
        })
        .catch(error => {
            appendOutput(`Błąd: ${error.message}`, true);
        });
});

// Obsługa zakładek
tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        // Usuń klasę active ze wszystkich zakładek
        tabs.forEach(t => t.classList.remove('active'));
        
        // Dodaj klasę active do klikniętej zakładki
        tab.classList.add('active');
        
        // Ukryj wszystkie panele
        panels.forEach(panel => panel.classList.remove('active'));
        
        // Pokaż odpowiedni panel
        const panelId = tab.dataset.panel;
        document.getElementById(panelId).classList.add('active');
    });
});

// Inicjalizacja
document.addEventListener('DOMContentLoaded', function() {
    // Sprawdzenie statusu piaskownicy
    fetch('/api/docker-status')
        .then(response => response.json())
        .then(data => {
            if (data.ready) {
                updateStatusIndicator('ready');
                containerId.textContent = data.container_id || '-';
            } else {
                updateStatusIndicator('error');
            }
        })
        .catch(error => {
            updateStatusIndicator('error');
            console.error('Błąd sprawdzania statusu:', error);
        });
}

// Inicjalizacja
function initializeApp() {
    updateFileList();
    updateEditor();
    checkDockerStatus();
    
    // Set up matrix layout functionality
    setupMatrixLayout();
    
    // Load menu data
    loadMenuData();
    
    // Initialize isEditing state
    state.isEditing = false;
}

// Mode switching functionality
function switchAppMode(mode) {
    // Update state
    state.currentMode = mode;
    
    // Update body data attribute for CSS styling
    document.body.setAttribute('data-mode', mode);
    
    // Update panel contents based on the mode
    updatePanelContentsForMode(mode);
    
    // Reset panel sizes when switching modes
    resetPanels();
    
    console.log(`Switched to ${mode} mode`);
}

function updatePanelContentsForMode(mode) {
    const modeContents = state.panelContents[mode];
    if (!modeContents) return;
    
    // Update each panel's title and content
    Object.keys(modeContents).forEach(panelId => {
        const panel = document.getElementById(panelId);
        if (!panel) return;
        
        const panelData = modeContents[panelId];
        
        // Update panel title
        const headerElement = panel.querySelector('.panel-header h3');
        if (headerElement && panelData.title) {
            headerElement.textContent = panelData.title;
        }
        
        // Only update content if we're not in the middle of editing something
        // This prevents losing user input when switching modes
        if (!state.isEditing) {
            const contentElement = panel.querySelector('.panel-content');
            if (contentElement && panelData.content) {
                // Store original content if this is the first mode switch
                if (!panel.dataset.originalContent && mode === 'development') {
                    panel.dataset.originalContent = contentElement.innerHTML;
                }
                
                // Update content
                contentElement.innerHTML = panelData.content;
            }
        }
    });
    
    // Reinitialize necessary event listeners and elements
    initializePanelElements();
}

function initializePanelElements() {
    // Reinitialize editor if it exists in the current mode
    const editorElement = document.getElementById('editor');
    if (editorElement) {
        editorElement.value = state.files[state.currentFile] || '';
    }
    
    // Reinitialize file list if it exists
    updateFileList();
    
    // Reinitialize tab functionality
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const panelId = this.dataset.panel;
            activateTab(this, panelId);
        });
    });
    
    // Activate first tab in each tab container
    document.querySelectorAll('.tab-container').forEach(container => {
        const firstTab = container.querySelector('.tab');
        if (firstTab) {
            const panelId = firstTab.dataset.panel;
            activateTab(firstTab, panelId);
        }
    });
}

function activateTab(tabElement, panelId) {
    // Deactivate all tabs in the same container
    const tabContainer = tabElement.closest('.tab-container');
    if (!tabContainer) return;
    
    tabContainer.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Activate the clicked tab
    tabElement.classList.add('active');
    
    // Hide all panels related to this tab container
    const panelContainer = tabContainer.closest('.panel-content');
    if (!panelContainer) return;
    
    panelContainer.querySelectorAll('.panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    // Show the selected panel
    const targetPanel = document.getElementById(panelId);
    if (targetPanel) {
        targetPanel.classList.add('active');
    }
}

function setupMatrixLayout() {
    // Set up intersection point dragging
    setupIntersectionPoint();
    
    // Set up matrix mode toggle
    matrixToggleButton.addEventListener('click', toggleMatrixMode);
    
    // Set up app mode selector
    const modeSelector = document.getElementById('app-mode-selector');
    if (modeSelector) {
        modeSelector.addEventListener('change', function() {
            switchAppMode(this.value);
        });
    }
    
    // Set up panel headers for expanding/minimizing
    const panelHeaders = document.querySelectorAll('.panel-header');
    panelHeaders.forEach(header => {
        header.addEventListener('click', function() {
            togglePanelSize(this);
        });
    });
    
    // Set up maximize buttons
    const panelMaximizeButtons = document.querySelectorAll('.panel-maximize-btn');
    panelMaximizeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            togglePanelSize(this);
        });
    });
    
    // Set up CoPanel buttons
    const uploadBtn = document.getElementById('upload-btn');
    const runAppBtn = document.getElementById('run-app-btn');
    const editBtn = document.getElementById('edit-btn');
    
    if (uploadBtn) uploadBtn.addEventListener('click', toggleMenuOverlay);
    
    // Initialize the intersection point at the center
    matrixContainer.style.gridTemplateColumns = '50% 50%';
    matrixContainer.style.gridTemplateRows = '50% 50%';
    intersectionPoint.style.left = '50%';
    intersectionPoint.style.top = '50%';
    
    // Set initial mode
    document.body.setAttribute('data-mode', state.currentMode);
}

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});
