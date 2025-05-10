# Piaskownica Docker

Moduł piaskownicy Docker (Docker Sandbox) to zaawansowane narzędzie w projekcie Devopy, które umożliwia bezpieczne uruchamianie kodu Python w izolowanych kontenerach Docker. Zapewnia to ochronę przed potencjalnie niebezpiecznym kodem i umożliwia wykonywanie operacji bez ryzyka uszkodzenia systemu głównego.

## Funkcje

1. **Bezpieczne uruchamianie kodu**
   - Wykonywanie kodu Python w izolowanym środowisku
   - Ograniczenia zasobów (CPU, pamięć)
   - Brak dostępu do sieci
   - Przechwytywanie wyjścia i błędów

2. **Uruchamianie usług**
   - Możliwość uruchomienia długotrwałych usług (np. serwer HTTP)
   - Mapowanie portów między kontenerem a hostem
   - Zarządzanie cyklem życia usługi

3. **Automatyczne zarządzanie zależnościami**
   - Integracja z menedżerem zależności
   - Automatyczne importowanie standardowych modułów

## Wymagania

1. **Docker**
   - Zainstalowany i działający Docker na maszynie hosta
   - Minimalna wersja: Docker 19.03 lub nowszy

2. **Python**
   - Python 3.8 lub nowszy
   - Zainstalowane pakiety: `docker`, `psutil`

3. **Zależności dla kodu w piaskownicy**
   - Podstawowe pakiety są automatycznie instalowane w kontenerze: `numpy`, `matplotlib`, `pandas`, `flask`, `requests`
   - Dodatkowe pakiety można zainstalować poprzez dodanie ich do pliku requirements.txt w katalogu piaskownicy

### Sprawdzenie wymagań

```bash
# Sprawdź, czy Docker jest zainstalowany i jego wersję
docker --version

# Sprawdź, czy Docker działa
docker info

# Sprawdź, czy wymagane pakiety Python są zainstalowane
pip list | grep docker
pip list | grep psutil
```

## Instalacja

Piaskownica Docker jest wbudowana w projekt Devopy i nie wymaga dodatkowej instalacji poza samym Dockerem i wymaganymi pakietami Python.

```bash
# Instalacja wymaganych pakietów Python
pip install docker psutil

# Opcjonalnie: Instalacja dodatkowych pakietów dla pełnej funkcjonalności
pip install numpy matplotlib pandas flask requests
```

### Konfiguracja

Piaskownica Docker może być skonfigurowana poprzez parametry inicjalizacji klasy `DockerSandbox`:

```python
from devopy.sandbox.docker_sandbox import DockerSandbox

# Domyślna konfiguracja
sandbox = DockerSandbox()

# Niestandardowa konfiguracja
sandbox = DockerSandbox(
    base_dir="/sciezka/do/katalogu/piaskownicy",  # Katalog dla plików piaskownicy
    docker_image="python:3.10-slim",             # Niestandardowy obraz Docker
    timeout=120                                  # Limit czasu wykonania w sekundach
)
```

## Użycie

### Jako moduł w kodzie Python

```python
from devopy.sandbox.docker_sandbox import DockerSandbox, run_code_in_sandbox, run_service_in_sandbox, check_docker_available

# Sprawdź, czy Docker jest dostępny
docker_available, message = check_docker_available()
if not docker_available:
    print(f"Docker nie jest dostępny: {message}")
    exit(1)

# Przykład 1: Uruchomienie prostego kodu
code = """
import numpy as np
import matplotlib.pyplot as plt

def execute():
    # Generuj dane
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    
    # Stwórz wykres
    plt.figure(figsize=(8, 6))
    plt.plot(x, y, 'r-')
    plt.title('Wykres funkcji sinus')
    plt.grid(True)
    
    return "Wykres wygenerowany pomyślnie"

result = execute()
print(result)
"""

result = run_code_in_sandbox(code)
print(f"Sukces: {result['success']}")
print(f"Wyjście: {result['output']}")
print(f"Błąd: {result['error']}")
print(f"Czas wykonania: {result['execution_time']} s")

# Przykład 2: Uruchomienie usługi (np. serwer Flask)
service_code = """
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Docker Sandbox!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
"""

service_result = run_service_in_sandbox(service_code, port=8000)
print(f"Usługa uruchomiona: {service_result['success']}")
print(f"URL: {service_result['url']}")
print(f"Kontener: {service_result['container_name']}")

# Zatrzymanie usługi
from devopy.sandbox.docker_sandbox import stop_sandbox_service
stop_result = stop_sandbox_service(service_result['container_name'])
print(f"Usługa zatrzymana: {stop_result['success']}")
```

### Jako narzędzie wiersza poleceń

```bash
# Uruchomienie kodu z pliku
python -m devopy.sandbox.docker_sandbox --file path/to/code.py

# Uruchomienie kodu bezpośrednio
python -m devopy.sandbox.docker_sandbox --code "print('Hello from sandbox!')"

# Uruchomienie usługi
python -m devopy.sandbox.docker_sandbox --file server.py --service --port 8080

# Zatrzymanie usługi
python -m devopy.sandbox.docker_sandbox --stop devopy-service-12345678
```

## Integracja z API i CLI Devopy

Piaskownica Docker jest zintegrowana z API i CLI Devopy:

```python
# W API
from devopy.sandbox.docker_sandbox import run_code_in_sandbox

@app.route('/execute', methods=['POST'])
def execute_code():
    code = request.json.get('code')
    result = run_code_in_sandbox(code)
    return jsonify(result)
```

## Konfiguracja

Piaskownicę Docker można skonfigurować, modyfikując parametry w konstruktorze klasy `DockerSandbox`:

```python
sandbox = DockerSandbox(
    base_dir=Path("/tmp/devopy-sandbox"),  # Katalog bazowy dla plików piaskownicy
    docker_image="python:3.9-slim",        # Obraz Docker do użycia
    timeout=30                             # Limit czasu wykonania w sekundach
)
```

## Przykłady użycia

### Przykład 1: Analiza danych w piaskownicy

```python
from devopy.sandbox.docker_sandbox import run_code_in_sandbox

code = """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# Generuj przykładowe dane
np.random.seed(42)
X = np.random.rand(100, 1) * 10
y = 2 * X.squeeze() + 1 + np.random.randn(100) * 2

# Utwórz model regresji liniowej
model = LinearRegression()
model.fit(X, y)

# Przewidywania
y_pred = model.predict(X)

# Wyniki
print(f"Współczynnik: {model.coef_[0]:.4f}")
print(f"Wyraz wolny: {model.intercept_:.4f}")
print(f"R^2: {model.score(X, y):.4f}")

# Wykres
plt.figure(figsize=(10, 6))
plt.scatter(X, y, alpha=0.7)
plt.plot(X, y_pred, 'r-', linewidth=2)
plt.title('Regresja liniowa')
plt.xlabel('X')
plt.ylabel('y')
plt.grid(True)

def execute():
    return {
        "coefficient": float(model.coef_[0]),
        "intercept": float(model.intercept_),
        "r_squared": float(model.score(X, y))
    }
"""

result = run_code_in_sandbox(code)
if result["success"]:
    print(result["output"])
else:
    print(f"Błąd: {result['error']}")
```

### Przykład 2: Uruchomienie serwera API w piaskownicy

```python
from devopy.sandbox.docker_sandbox import run_service_in_sandbox, stop_sandbox_service

code = """
from flask import Flask, request, jsonify

app = Flask(__name__)

# Przykładowa baza danych
tasks = [
    {"id": 1, "title": "Zadanie 1", "completed": False},
    {"id": 2, "title": "Zadanie 2", "completed": True}
]

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = next((task for task in tasks if task["id"] == task_id), None)
    if task:
        return jsonify(task)
    return jsonify({"error": "Task not found"}), 404

@app.route('/tasks', methods=['POST'])
def create_task():
    if not request.json or 'title' not in request.json:
        return jsonify({"error": "Invalid request"}), 400
    
    task = {
        "id": tasks[-1]["id"] + 1 if tasks else 1,
        "title": request.json["title"],
        "completed": request.json.get("completed", False)
    }
    tasks.append(task)
    return jsonify(task), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
"""

# Uruchom serwer API
service = run_service_in_sandbox(code, port=8000)

if service["success"]:
    print(f"Serwer API uruchomiony pod adresem: {service['url']}")
    print(f"Aby zatrzymać serwer, użyj: stop_sandbox_service('{service['container_name']}')")
else:
    print(f"Błąd podczas uruchamiania serwera: {service['error']}")

# Zatrzymanie serwera (po zakończeniu pracy)
# stop_result = stop_sandbox_service(service['container_name'])
```

## Rozwiązywanie problemów

Jeśli piaskownica Docker nie działa poprawnie, sprawdź:

1. Czy Docker jest zainstalowany i działa
2. Czy masz uprawnienia do uruchamiania kontenerów Docker
3. Czy kod Python jest poprawny składniowo
4. Czy nie próbujesz uzyskać dostępu do zasobów niedostępnych w piaskownicy (np. sieć, pliki systemowe)

```python
from devopy.sandbox.docker_sandbox import check_docker_available

available, message = check_docker_available()
if not available:
    print(f"Problem z Dockerem: {message}")
else:
    print("Docker jest dostępny i działa poprawnie")
```

## Ograniczenia

1. Brak dostępu do sieci w trybie standardowym (można to zmienić w konfiguracji)
2. Ograniczone zasoby (CPU, pamięć)
3. Brak dostępu do plików systemowych poza katalogiem piaskownicy
4. Ograniczony czas wykonania

## Rozszerzanie funkcjonalności

Piaskownicę Docker można łatwo rozszerzyć o dodatkowe funkcje:

1. **Dodanie obsługi woluminów**

```python
def run_with_volume(self, code: str, volume_path: str, mount_point: str = "/data") -> Dict[str, Any]:
    """Uruchamia kod z dostępem do woluminu"""
    # Kod implementacji...
```

2. **Dodanie obsługi sieci**

```python
def run_with_network(self, code: str, network_mode: str = "bridge") -> Dict[str, Any]:
    """Uruchamia kod z dostępem do sieci"""
    # Kod implementacji...
```

## Integracja z innymi modułami Devopy

Piaskownica Docker współpracuje z innymi modułami Devopy:

- **Menedżer zależności**: Automatyczne dodawanie importów do kodu
- **Konwertery tekstu na kod**: Bezpieczne uruchamianie wygenerowanego kodu
- **API**: Udostępnianie funkcji piaskownicy przez API REST

## Bezpieczeństwo

Piaskownica Docker zapewnia wysoki poziom bezpieczeństwa dzięki:

1. Izolacji kontenerów Docker
2. Ograniczeniom zasobów
3. Brakowi dostępu do sieci
4. Automatycznemu czyszczeniu zasobów

Należy jednak pamiętać, że żadne rozwiązanie nie jest w 100% bezpieczne. Zaleca się regularne aktualizowanie Dockera i obrazów kontenerów.
