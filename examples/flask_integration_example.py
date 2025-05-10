from flask import Flask, request, jsonify
import inspect
import os
import sys

# Dodaj ścieżkę projektu do PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from devopy.converters.text2python_decorator import text2python_task
from devopy.converters.restapi_task import restapi_task, get_registered_restapi_tasks

app = Flask(__name__)

# Przykładowe funkcje z dekoratorami
@text2python_task("Napisz funkcję, która oblicza n-ty wyraz ciągu Fibonacciego")
@restapi_task("GET /fibonacci")
def fibonacci(n: int):
    """Oblicza n-ty wyraz ciągu Fibonacciego"""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

@text2python_task("Napisz funkcję, która sortuje listę liczb")
@restapi_task("POST /sort")
def sort_numbers(numbers):
    """Sortuje listę liczb"""
    return sorted(numbers)

@text2python_task("Napisz funkcję, która analizuje tekst i zwraca statystyki")
@restapi_task("POST /analyze")
def analyze_text(text):
    """Analizuje tekst i zwraca statystyki"""
    words = text.split()
    sentences = text.split('.')
    return {
        "words": len(words),
        "sentences": len(sentences),
        "characters": len(text),
        "average_word_length": sum(len(word) for word in words) / len(words) if words else 0
    }

def register_restapi_endpoints():
    """Rejestruje wszystkie funkcje oznaczone dekoratorem restapi_task jako endpointy Flask"""
    for func, route, method in get_registered_restapi_tasks():
        # Pobierz sygnaturę funkcji
        sig = inspect.signature(func)
        
        # Utwórz endpoint Flask
        def create_endpoint(func, method):
            def endpoint():
                # Pobierz argumenty z zapytania
                kwargs = {}
                if method == "GET":
                    # Dla GET pobierz argumenty z query string
                    for param_name in sig.parameters:
                        if param_name in request.args:
                            param_value = request.args.get(param_name)
                            # Konwertuj wartości na odpowiednie typy
                            param_type = sig.parameters[param_name].annotation
                            if param_type is int:
                                param_value = int(param_value)
                            elif param_type is float:
                                param_value = float(param_value)
                            elif param_type is bool:
                                param_value = param_value.lower() in ('true', 'yes', '1')
                            kwargs[param_name] = param_value
                else:
                    # Dla POST/PUT/DELETE pobierz argumenty z JSON
                    if request.is_json:
                        kwargs = request.get_json()
                
                # Wywołaj funkcję
                result = func(**kwargs)
                
                # Zwróć wynik jako JSON
                return jsonify(result)
            
            # Ustaw nazwę endpointu
            endpoint.__name__ = f"{func.__name__}_endpoint"
            return endpoint
        
        # Zarejestruj endpoint
        app.route(route, methods=[method])(create_endpoint(func, method))
        print(f"Zarejestrowano endpoint: {method} {route} -> {func.__name__}")

# Zarejestruj wszystkie endpointy
register_restapi_endpoints()

# Dodaj endpoint informacyjny
@app.route('/')
def index():
    """Zwraca informacje o dostępnych endpointach"""
    endpoints = []
    for func, route, method in get_registered_restapi_tasks():
        endpoints.append({
            "method": method,
            "route": route,
            "function": func.__name__,
            "prompt": func._text2python_prompt,
            "docstring": func.__doc__
        })
    
    return jsonify({
        "service": "Devopy REST API",
        "endpoints": endpoints
    })

if __name__ == "__main__":
    app.run(debug=True, port=8000)
