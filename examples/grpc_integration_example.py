import os
import sys
import tempfile
import subprocess
import time
import threading
from concurrent import futures

# Dodaj ścieżkę projektu do PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from devopy.converters.text2python_decorator import text2python_task
from devopy.converters.grpc_task import grpc_task, get_registered_grpc_tasks

# Przykładowe funkcje z dekoratorami
@text2python_task("Napisz funkcję, która oblicza n-ty wyraz ciągu Fibonacciego")
@grpc_task("""
syntax = "proto3";

message FibonacciRequest {
    int32 n = 1;
}

message FibonacciResponse {
    int32 result = 1;
}

service FibonacciService {
    rpc Compute (FibonacciRequest) returns (FibonacciResponse);
}
""", service="FibonacciService")
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
@grpc_task("""
syntax = "proto3";

message SortRequest {
    repeated int32 numbers = 1;
}

message SortResponse {
    repeated int32 sorted_numbers = 1;
}

service SortService {
    rpc Sort (SortRequest) returns (SortResponse);
}
""", service="SortService")
def sort_numbers(numbers):
    """Sortuje listę liczb"""
    return sorted(numbers)

@text2python_task("Napisz funkcję, która analizuje tekst i zwraca statystyki")
@grpc_task("""
syntax = "proto3";

message TextAnalysisRequest {
    string text = 1;
}

message TextAnalysisResponse {
    int32 words = 1;
    int32 sentences = 2;
    int32 characters = 3;
    float average_word_length = 4;
}

service TextAnalysisService {
    rpc Analyze (TextAnalysisRequest) returns (TextAnalysisResponse);
}
""", service="TextAnalysisService")
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

def generate_proto_files():
    """Generuje pliki .proto na podstawie zarejestrowanych funkcji"""
    proto_dir = os.path.join(os.getcwd(), "generated", "proto")
    os.makedirs(proto_dir, exist_ok=True)
    
    proto_files = []
    
    for func, proto_content, service_name in get_registered_grpc_tasks():
        # Utwórz plik .proto
        proto_file = os.path.join(proto_dir, f"{func.__name__}.proto")
        with open(proto_file, "w") as f:
            f.write(proto_content)
        
        proto_files.append((proto_file, func.__name__, service_name))
        print(f"Wygenerowano plik .proto dla {func.__name__}: {proto_file}")
    
    return proto_files

def generate_grpc_code(proto_files):
    """Generuje kod Python na podstawie plików .proto"""
    for proto_file, module_name, _ in proto_files:
        # Utwórz katalog dla wygenerowanego kodu
        output_dir = os.path.dirname(proto_file)
        
        # Uruchom protoc do wygenerowania kodu Python
        cmd = [
            "python", "-m", "grpc_tools.protoc",
            f"--proto_path={output_dir}",
            f"--python_out={output_dir}",
            f"--grpc_python_out={output_dir}",
            proto_file
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"Wygenerowano kod gRPC dla {module_name}")
        except subprocess.CalledProcessError as e:
            print(f"Błąd podczas generowania kodu gRPC: {e}")
            continue
        except FileNotFoundError:
            print("Narzędzie protoc nie jest dostępne. Zainstaluj grpcio-tools.")
            continue

def generate_server_code(proto_files):
    """Generuje kod serwera gRPC"""
    server_file = os.path.join(os.getcwd(), "generated", "grpc_server.py")
    
    server_code = """import os
import sys
import time
import grpc
from concurrent import futures
import importlib

# Dodaj katalog z wygenerowanym kodem do PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

"""
    
    # Importuj wygenerowane moduły
    for _, module_name, _ in proto_files:
        server_code += f"""
# Importuj wygenerowany kod dla {module_name}
try:
    {module_name}_pb2 = importlib.import_module("proto.{module_name}_pb2")
    {module_name}_pb2_grpc = importlib.import_module("proto.{module_name}_pb2_grpc")
except ImportError as e:
    print(f"Błąd importu modułu {module_name}: {{e}}")
"""
    
    # Dodaj implementacje serwisów
    for func, _, service_name in get_registered_grpc_tasks():
        module_name = func.__name__
        
        server_code += f"""
# Implementacja serwisu {service_name}
class {service_name}Servicer({module_name}_pb2_grpc.{service_name}Servicer):
    def Compute(self, request, context):
        # Wywołaj funkcję {func.__name__}
        result = {func.__name__}(request.n)
        return {module_name}_pb2.FibonacciResponse(result=result)
"""
    
    # Dodaj kod serwera
    server_code += """
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
"""
    
    # Zarejestruj serwisy
    for _, module_name, service_name in proto_files:
        server_code += f"""    {module_name}_pb2_grpc.add_{service_name}Servicer_to_server({service_name}Servicer(), server)
"""
    
    server_code += """
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Serwer gRPC uruchomiony na porcie 50051")
    
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
"""
    
    with open(server_file, "w") as f:
        f.write(server_code)
    
    print(f"Wygenerowano kod serwera gRPC: {server_file}")
    return server_file

def generate_client_code(proto_files):
    """Generuje kod klienta gRPC"""
    client_file = os.path.join(os.getcwd(), "generated", "grpc_client.py")
    
    client_code = """import os
import sys
import grpc
import importlib

# Dodaj katalog z wygenerowanym kodem do PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

"""
    
    # Importuj wygenerowane moduły
    for _, module_name, _ in proto_files:
        client_code += f"""
# Importuj wygenerowany kod dla {module_name}
try:
    {module_name}_pb2 = importlib.import_module("proto.{module_name}_pb2")
    {module_name}_pb2_grpc = importlib.import_module("proto.{module_name}_pb2_grpc")
except ImportError as e:
    print(f"Błąd importu modułu {module_name}: {{e}}")
"""
    
    # Dodaj kod klienta
    client_code += """
def run():
    # Utwórz kanał gRPC
    with grpc.insecure_channel('localhost:50051') as channel:
"""
    
    # Dodaj kod dla każdego serwisu
    for func, _, service_name in get_registered_grpc_tasks():
        module_name = func.__name__
        
        client_code += f"""
        # Klient dla {service_name}
        {module_name}_stub = {module_name}_pb2_grpc.{service_name}Stub(channel)
        
        # Przykładowe wywołanie
        if "{module_name}" == "fibonacci":
            response = {module_name}_stub.Compute({module_name}_pb2.FibonacciRequest(n=10))
            print(f"Fibonacci(10) = {{response.result}}")
        elif "{module_name}" == "sort_numbers":
            response = {module_name}_stub.Sort({module_name}_pb2.SortRequest(numbers=[3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]))
            print(f"Sorted numbers: {{response.sorted_numbers}}")
        elif "{module_name}" == "analyze_text":
            response = {module_name}_stub.Analyze({module_name}_pb2.TextAnalysisRequest(text="To jest przykładowy tekst. Zawiera dwa zdania."))
            print(f"Text analysis: words={{response.words}}, sentences={{response.sentences}}, characters={{response.characters}}, avg_word_length={{response.average_word_length}}")
"""
    
    client_code += """
if __name__ == '__main__':
    run()
"""
    
    with open(client_file, "w") as f:
        f.write(client_code)
    
    print(f"Wygenerowano kod klienta gRPC: {client_file}")
    return client_file

def generate_readme():
    """Generuje plik README z instrukcjami"""
    readme_file = os.path.join(os.getcwd(), "generated", "README.md")
    
    readme_content = """# Wygenerowane serwisy gRPC

Ten katalog zawiera wygenerowane pliki dla serwisów gRPC na podstawie dekoratorów `@grpc_task`.

## Struktura katalogów

- `proto/` - Pliki .proto i wygenerowany kod Python
- `grpc_server.py` - Implementacja serwera gRPC
- `grpc_client.py` - Przykładowy klient gRPC

## Uruchamianie serwera

```bash
python grpc_server.py
```

## Uruchamianie klienta

```bash
python grpc_client.py
```

## Wymagania

- grpcio
- grpcio-tools
- protobuf
"""
    
    with open(readme_file, "w") as f:
        f.write(readme_content)
    
    print(f"Wygenerowano plik README: {readme_file}")

if __name__ == "__main__":
    # Generuj pliki .proto
    proto_files = generate_proto_files()
    
    # Generuj kod Python na podstawie plików .proto
    # Uwaga: Ta funkcja wymaga zainstalowanego pakietu grpcio-tools
    # generate_grpc_code(proto_files)
    
    # Generuj kod serwera
    server_file = generate_server_code(proto_files)
    
    # Generuj kod klienta
    client_file = generate_client_code(proto_files)
    
    # Generuj README
    generate_readme()
    
    print("\nAby zainstalować wymagane pakiety, wykonaj:")
    print("pip install grpcio grpcio-tools protobuf")
    
    print("\nAby wygenerować kod gRPC, wykonaj:")
    print("python -m grpc_tools.protoc --proto_path=generated/proto --python_out=generated/proto --grpc_python_out=generated/proto generated/proto/*.proto")
    
    print("\nAby uruchomić serwer, wykonaj:")
    print("python generated/grpc_server.py")
    
    print("\nAby uruchomić klienta, wykonaj:")
    print("python generated/grpc_client.py")
