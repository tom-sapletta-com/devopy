# Konwerter Tekstu na Kod Python

Moduł `text2python` to zaawansowane narzędzie w projekcie Devopy, które umożliwia konwersję opisów w języku naturalnym na funkcjonalny kod Python przy użyciu modeli językowych (LLM). Dodatkowo oferuje funkcje wyjaśniania i ulepszania istniejącego kodu.

## Funkcje

1. **Konwersja tekstu na kod Python**
   - Przekształcanie opisów zadań w języku naturalnym na działający kod Python
   - Automatyczne dodawanie niezbędnych importów (integracja z menedżerem zależności)
   - Generowanie kompletnych funkcji gotowych do uruchomienia

2. **Wyjaśnianie kodu**
   - Generowanie czytelnych wyjaśnień istniejącego kodu Python
   - Analiza krok po kroku działania funkcji i algorytmów

3. **Ulepszanie kodu**
   - Optymalizacja istniejącego kodu pod kątem wydajności i czytelności
   - Dostosowanie kodu do dobrych praktyk programistycznych

## Wymagania

Moduł wymaga zainstalowania i skonfigurowania narzędzia Ollama z odpowiednim modelem językowym. Domyślnie używany jest model `codellama:7b-code`, ale można skonfigurować dowolny inny model.

### Instalacja Ollama

```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Pobieranie modelu
ollama pull codellama:7b-code
```

## Użycie

### Jako moduł w kodzie Python

```python
from devopy.converters.text2python import Text2Python, convert_text_to_python, explain_python_code, improve_python_code

# Przykład 1: Konwersja opisu na kod
prompt = "Napisz funkcję, która oblicza n-ty wyraz ciągu Fibonacciego"
code = convert_text_to_python(prompt)
print(code)

# Przykład 2: Wyjaśnienie kodu
code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
explanation = explain_python_code(code)
print(explanation)

# Przykład 3: Ulepszenie kodu
improved_code = improve_python_code(code)
print(improved_code)

# Przykład 4: Użycie pełnego API
converter = Text2Python(model_name="codellama:7b-code")
result = converter.text_to_python("Napisz funkcję do sortowania listy")
if result["success"]:
    print(result["code"])
else:
    print(f"Błąd: {result['error']}")
```

### Jako narzędzie wiersza poleceń

```bash
# Konwersja opisu na kod
python -m devopy.converters.text2python "Napisz funkcję, która sortuje listę" --output sort.py

# Konwersja z wyjaśnieniem
python -m devopy.converters.text2python "Napisz funkcję, która sortuje listę" --explain

# Ulepszenie istniejącego kodu
python -m devopy.converters.text2python existing_code.py --improve --output improved_code.py
```

## Integracja z API i CLI Devopy

Konwerter tekstu na kod jest zintegrowany z API i CLI Devopy:

```python
# W API
from devopy.converters.text2python import convert_text_to_python

@app.route('/generate', methods=['POST'])
def generate_code():
    prompt = request.json.get('prompt')
    code = convert_text_to_python(prompt)
    return jsonify({"code": code})
```

## Konfiguracja

Konwerter można skonfigurować, modyfikując parametry w konstruktorze klasy `Text2Python`:

```python
converter = Text2Python(
    model_name="codellama:7b-code",  # Nazwa modelu Ollama
    code_dir="/path/to/code"         # Opcjonalny katalog z kodem
)
```

## Przykłady użycia

### Przykład 1: Generowanie funkcji do analizy danych

```python
from devopy.converters.text2python import convert_text_to_python

prompt = """
Napisz funkcję, która:
1. Wczytuje dane z pliku CSV
2. Oblicza podstawowe statystyki (średnia, mediana, odchylenie standardowe)
3. Generuje wykres histogramu
4. Zapisuje wyniki do pliku JSON
"""

code = convert_text_to_python(prompt)
print(code)
```

Wynik:

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json

def execute(file_path, output_json=None):
    # Wczytanie danych z pliku CSV
    df = pd.read_csv(file_path)
    
    # Obliczenie podstawowych statystyk
    stats = {}
    for column in df.select_dtypes(include=[np.number]).columns:
        stats[column] = {
            'mean': df[column].mean(),
            'median': df[column].median(),
            'std': df[column].std()
        }
    
    # Generowanie wykresu histogramu
    for column in df.select_dtypes(include=[np.number]).columns:
        plt.figure(figsize=(10, 6))
        plt.hist(df[column], bins=30, alpha=0.7)
        plt.title(f'Histogram dla {column}')
        plt.xlabel(column)
        plt.ylabel('Częstość')
        plt.savefig(f'histogram_{column}.png')
        plt.close()
    
    # Zapisanie wyników do pliku JSON
    if output_json is None:
        output_json = 'stats.json'
    
    with open(output_json, 'w') as f:
        json.dump(stats, f, indent=4)
    
    return stats
```

### Przykład 2: Wyjaśnienie złożonego kodu

```python
from devopy.converters.text2python import explain_python_code

code = """
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)
"""

explanation = explain_python_code(code)
print(explanation)
```

### Przykład 3: Ulepszenie nieefektywnego kodu

```python
from devopy.converters.text2python import improve_python_code

code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

improved_code = improve_python_code(code)
print(improved_code)
```

## Rozwiązywanie problemów

Jeśli konwerter tekstu na kod nie działa poprawnie, sprawdź:

1. Czy Ollama jest zainstalowane i działa
2. Czy wybrany model jest dostępny (`ollama list`)
3. Czy opis zadania jest wystarczająco precyzyjny
4. Czy występują błędy w logach

## Ograniczenia

1. Jakość generowanego kodu zależy od użytego modelu LLM
2. Złożone zadania mogą wymagać dodatkowego dopracowania wygenerowanego kodu
3. Generowanie kodu może być czasochłonne dla większych zadań

## Rozszerzanie funkcjonalności

Konwerter tekstu na kod można łatwo rozszerzyć o dodatkowe funkcje:

1. **Dodanie obsługi nowych modeli LLM**

```python
def use_openai_model(self, prompt: str) -> Dict[str, Any]:
    """Użycie modelu OpenAI zamiast Ollama"""
    import openai
    
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=1500
    )
    
    return {
        "success": True,
        "code": response.choices[0].text.strip(),
        "error": "",
        "analysis": "Kod wygenerowany przez OpenAI"
    }
```

2. **Dodanie funkcji testowania wygenerowanego kodu**

```python
def test_generated_code(self, code: str) -> bool:
    """Testuje wygenerowany kod w bezpiecznym środowisku"""
    import tempfile
    import subprocess
    
    with tempfile.NamedTemporaryFile(suffix='.py', mode='w+') as f:
        f.write(code)
        f.flush()
        
        try:
            result = subprocess.run(
                [sys.executable, f.name],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
```

## Integracja z innymi modułami Devopy

Konwerter tekstu na kod współpracuje z innymi modułami Devopy:

- **Menedżer zależności**: Automatyczne dodawanie importów do wygenerowanego kodu
- **Piaskownice (Sandboxes)**: Bezpieczne uruchamianie wygenerowanego kodu
- **API**: Udostępnianie funkcji konwersji przez API REST
