# Menedżer Zależności

Menedżer zależności to zaawansowany moduł projektu Devopy, który automatycznie analizuje kod Python, wykrywa brakujące zależności i automatycznie je dodaje. Wykorzystuje zarówno statyczną analizę kodu (AST), jak i dynamiczne wykrywanie importów.

## Funkcje

1. **Analiza kodu**
   - Wykrywanie używanych modułów w kodzie Python
   - Identyfikacja brakujących importów
   - Rozpoznawanie standardowych modułów Python

2. **Naprawianie brakujących importów**
   - Automatyczne dodawanie brakujących instrukcji import
   - Inteligentne umieszczanie importów w odpowiednim miejscu w kodzie

3. **Instalacja brakujących pakietów**
   - Wykrywanie i instalacja brakujących pakietów Python
   - Obsługa środowisk wirtualnych

## Instalacja

Menedżer zależności jest wbudowany w projekt Devopy i nie wymaga dodatkowej instalacji.

## Użycie

### Jako moduł w kodzie Python

```python
from devopy.utils.dependency_manager import DependencyManager, fix_code_dependencies, install_missing_packages

# Przykład 1: Naprawianie brakujących importów
code = """
def main():
    df = pd.DataFrame({'a': [1, 2, 3]})
    plt.plot(df['a'])
    plt.show()
"""

fixed_code = fix_code_dependencies(code)
print(fixed_code)
# Wynik:
# import pandas as pd
# import matplotlib.pyplot as plt
#
# def main():
#     df = pd.DataFrame({'a': [1, 2, 3]})
#     plt.plot(df['a'])
#     plt.show()

# Przykład 2: Instalacja brakujących pakietów
installed_packages = install_missing_packages(code)
print(f"Zainstalowane pakiety: {installed_packages}")

# Przykład 3: Użycie pełnego API
manager = DependencyManager()
used_modules = manager.analyze_code(code)
print(f"Używane moduły: {used_modules}")
```

### Jako narzędzie wiersza poleceń

```bash
# Analiza kodu z pliku
python -m devopy.utils.dependency_manager path/to/file.py

# Analiza kodu podanego bezpośrednio
python -m devopy.utils.dependency_manager "import numpy as np; x = np.array([1, 2, 3]); plt.plot(x)"
```

## Integracja z API i CLI Devopy

Menedżer zależności jest zintegrowany z API i CLI Devopy, co pozwala na automatyczne zarządzanie zależnościami podczas uruchamiania zadań:

```python
# W API
from devopy.utils.dependency_manager import fix_code_dependencies

@app.route('/run', methods=['POST'])
def run_code():
    code = request.json.get('code')
    fixed_code = fix_code_dependencies(code)
    # Uruchom naprawiony kod...
```

```python
# W CLI
from devopy.utils.dependency_manager import install_missing_packages

def run_task(task, code):
    # Zainstaluj brakujące pakiety przed uruchomieniem
    install_missing_packages(code)
    # Uruchom kod...
```

## Konfiguracja

Menedżer zależności można skonfigurować, modyfikując listy `STANDARD_MODULES` i `COMMON_MODULES` w pliku `devopy/utils/dependency_manager.py`:

```python
# Dodaj własne moduły do listy znanych modułów
COMMON_MODULES.update({
    'tensorflow', 'keras', 'pytorch', 'transformers'
})
```

## Rozszerzanie funkcjonalności

Menedżer zależności można łatwo rozszerzyć o dodatkowe funkcje:

1. **Dodanie obsługi nowych typów zależności**

```python
def analyze_requirements_txt(self, requirements_path):
    """Analizuje plik requirements.txt i instaluje wymienione pakiety"""
    with open(requirements_path, 'r') as f:
        requirements = f.readlines()
    
    packages = [line.strip() for line in requirements if line.strip() and not line.startswith('#')]
    return self.install_missing_packages(packages)
```

2. **Dodanie obsługi wirtualnych środowisk**

```python
def create_virtual_env(self, env_name, packages=None):
    """Tworzy nowe środowisko wirtualne i instaluje pakiety"""
    subprocess.check_call([sys.executable, '-m', 'venv', env_name])
    
    if packages:
        venv_path = os.path.abspath(env_name)
        self.install_missing_packages(packages, venv_path=venv_path)
    
    return os.path.abspath(env_name)
```

## Rozwiązywanie problemów

Jeśli menedżer zależności nie działa poprawnie, sprawdź:

1. Czy masz uprawnienia do instalacji pakietów
2. Czy kod Python jest poprawny składniowo
3. Czy pakiety są dostępne w repozytorium PyPI

Logi menedżera zależności są zapisywane w standardowym logu Devopy.

## Przykłady użycia

### Przykład 1: Analiza i naprawa kodu z brakującymi importami

```python
from devopy.utils.dependency_manager import fix_code_dependencies

code = """
def analyze_data(file_path):
    # Wczytaj dane z pliku CSV
    data = pd.read_csv(file_path)
    
    # Wykonaj podstawową analizę
    summary = data.describe()
    
    # Stwórz wykres
    plt.figure(figsize=(10, 6))
    sns.heatmap(data.corr(), annot=True)
    plt.title('Macierz korelacji')
    
    return summary
"""

fixed_code = fix_code_dependencies(code)
print(fixed_code)
```

Wynik:

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_data(file_path):
    # Wczytaj dane z pliku CSV
    data = pd.read_csv(file_path)
    
    # Wykonaj podstawową analizę
    summary = data.describe()
    
    # Stwórz wykres
    plt.figure(figsize=(10, 6))
    sns.heatmap(data.corr(), annot=True)
    plt.title('Macierz korelacji')
    
    return summary
```

### Przykład 2: Instalacja brakujących pakietów w środowisku wirtualnym

```python
from devopy.utils.dependency_manager import install_missing_packages

code = """
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
import sklearn.metrics as metrics

def train_model(data):
    # Kod trenowania modelu...
    pass
"""

# Zainstaluj brakujące pakiety w środowisku wirtualnym
venv_path = "/path/to/venv"
installed = install_missing_packages(code, venv_path=venv_path)
print(f"Zainstalowane pakiety: {installed}")
```

## Integracja z innymi modułami Devopy

Menedżer zależności współpracuje z innymi modułami Devopy:

- **Piaskownice (Sandboxes)**: Automatyczna instalacja zależności w izolowanych środowiskach
- **Konwertery tekstu na kod**: Automatyczne dodawanie importów do wygenerowanego kodu
- **API**: Zapewnienie, że kod uruchamiany przez API ma wszystkie wymagane zależności
