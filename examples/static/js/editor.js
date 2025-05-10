// Stan aplikacji
const state = {
    currentFile: 'main.py',
    files: {
        'main.py': '# Witaj w edytorze Devopy Docker!\n# Napisz swój kod Python tutaj i kliknij "Uruchom"\n\nprint("Hello, World!")\n'
    },
    matrixMode: false,
    expandedPanel: null,
    menuData: null
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
}

function setupMatrixLayout() {
    // Set up intersection point dragging
    setupIntersectionPoint();
    
    // Set up matrix mode toggle
    matrixToggleButton.addEventListener('click', toggleMatrixMode);
    
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
}

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});
