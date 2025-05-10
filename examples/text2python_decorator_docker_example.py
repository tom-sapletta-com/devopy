from devopy.converters.text2python_decorator import text2python_task
from devopy.converters.restapi_task import restapi_task, get_registered_restapi_tasks
from devopy.converters.graphql_task import graphql_task, get_registered_graphql_tasks
from devopy.converters.grpc_task import grpc_task, get_registered_grpc_tasks
from devopy.converters.docker_task import docker_task, generate_docker_compose, get_registered_docker_tasks
import os

# Funkcja Fibonacci z dekoratorami dla wielu protokołów i Dockera
@text2python_task("Napisz funkcję, która oblicza n-ty wyraz ciągu Fibonacciego")
@restapi_task("GET http://localhost:8000/fibonacci")
@graphql_task("type Query { fibonacci(n: Int!): Int! }")
@grpc_task('service Fibonacci { rpc Compute (FiboRequest) returns (FiboResponse); }', service='Fibonacci')
@docker_task("python:3.9-slim", port=8000, env_vars={"DEBUG": "true"}, command="python app.py")
def fibonacci(n: int):
    # Ta implementacja zostanie zastąpiona przez text2python
    return n

# Funkcja do sortowania z dekoratorami
@text2python_task("Napisz funkcję, która sortuje listę liczb")
@restapi_task("POST http://localhost:8001/sort")
@graphql_task("type Mutation { sort(numbers: [Int!]!): [Int!]! }")
@docker_task("python:3.9-slim", port=8001, env_vars={"LOG_LEVEL": "INFO"})
def sort_numbers(numbers):
    # Ta implementacja zostanie zastąpiona przez text2python
    return numbers

# Funkcja do analizy tekstu
@text2python_task("Napisz funkcję, która analizuje tekst i zwraca statystyki (liczba słów, zdań, znaków)")
@restapi_task("POST http://localhost:8002/analyze")
@graphql_task("type Query { analyzeText(text: String!): TextStats! }")
@docker_task("python:3.9-slim", port=8002, env_vars={"LANG": "pl_PL.UTF-8"})
def analyze_text(text):
    # Ta implementacja zostanie zastąpiona przez text2python
    return {"words": 0, "sentences": 0, "characters": 0}

def generate_app_files():
    """Generuje pliki aplikacji dla każdej funkcji"""
    os.makedirs("generated", exist_ok=True)
    
    # Generuj pliki dla REST API
    rest_app = """from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

"""
    
    # Dodaj endpointy dla każdej funkcji
    for func, _, _, _, _ in get_registered_docker_tasks():
        func_name = func.__name__
        route_path = func._restapi_route
        http_method = func._restapi_method.upper()
        
        rest_app += f"""
@app.route('{route_path}', methods=['{http_method}'])
def {func_name}_endpoint():
    # Pobierz parametry z zapytania
    if '{http_method}' == 'GET':
        args = request.args.to_dict()
    else:
        args = request.json
    
    # Wywołaj funkcję
    result = {func_name}(**args)
    
    # Zwróć wynik jako JSON
    return jsonify(result)
"""
    
    rest_app += """
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
"""
    
    # Zapisz plik app.py
    with open("generated/app.py", "w") as f:
        f.write(rest_app)
    
    # Generuj plik requirements.txt
    requirements = """flask==2.0.1
gunicorn==20.1.0
graphene==2.1.9
grpcio==1.41.0
grpcio-tools==1.41.0
"""
    
    with open("generated/requirements.txt", "w") as f:
        f.write(requirements)

def generate_docker_files():
    """Generuje pliki Docker dla każdej funkcji"""
    os.makedirs("generated/docker", exist_ok=True)
    
    # Generuj Dockerfile dla każdej funkcji
    for func, image, port, env_vars, command in get_registered_docker_tasks():
        func_name = func.__name__
        
        dockerfile = f"""FROM {image}

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE {port}

CMD ["python", "app.py"]
"""
        
        with open(f"generated/docker/Dockerfile.{func_name}", "w") as f:
            f.write(dockerfile)
    
    # Generuj docker-compose.yml
    docker_compose = generate_docker_compose(get_registered_docker_tasks())
    
    with open("generated/docker-compose.yml", "w") as f:
        f.write(docker_compose)

if __name__ == "__main__":
    # Wyświetl informacje o zarejestrowanych funkcjach
    print("=== Zarejestrowane funkcje ===")
    for func, image, port, env_vars, command in get_registered_docker_tasks():
        print(f"Funkcja: {func.__name__}")
        print(f"  Prompt: {func._text2python_prompt}")
        print(f"  REST: {func._restapi_method} {func._restapi_route}")
        print(f"  GraphQL: {func._graphql_query}")
        print(f"  Docker: {image} (port: {port})")
        print()
    
    # Generuj pliki
    generate_app_files()
    generate_docker_files()
    
    print("=== Wygenerowane pliki ===")
    print("- generated/app.py")
    print("- generated/requirements.txt")
    for func, _, _, _, _ in get_registered_docker_tasks():
        print(f"- generated/docker/Dockerfile.{func.__name__}")
    print("- generated/docker-compose.yml")
    
    print("\nAby uruchomić kontenery, wykonaj:")
    print("cd generated && docker-compose up -d")
