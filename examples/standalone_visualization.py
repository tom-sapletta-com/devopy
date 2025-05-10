import os
import sys
import inspect
import json
import matplotlib.pyplot as plt
import networkx as nx
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

# Katalog na wizualizacje
os.makedirs("generated/visualizations", exist_ok=True)

# Własne implementacje dekoratorów, które nie modyfikują funkcji
def text2python_task(prompt=None, **kwargs):
    """Dekorator do oznaczania funkcji generowanych z promptu tekstowego"""
    def decorator(func):
        # Zamiast modyfikować funkcję, przechowujemy informacje w słowniku
        if not hasattr(decorator, 'registry'):
            decorator.registry = {}
        
        decorator.registry[func.__name__] = {
            'prompt': prompt,
            'kwargs': kwargs,
            'func': func
        }
        
        return func
    return decorator

def restapi_task(route, method="GET"):
    """Dekorator do rejestracji funkcji jako endpointy REST API"""
    if " " in route:
        parts = route.split(" ", 1)
        method, route = parts[0], parts[1]
    
    # Usuń prefiks URL, jeśli istnieje
    if "://" in route:
        route = "/" + route.split("/", 3)[3]
    
    def decorator(func):
        if not hasattr(decorator, 'registry'):
            decorator.registry = {}
        
        decorator.registry[func.__name__] = {
            'route': route,
            'method': method,
            'func': func
        }
        
        return func
    return decorator

def graphql_task(query):
    """Dekorator do rejestracji funkcji jako resolvery GraphQL"""
    def decorator(func):
        if not hasattr(decorator, 'registry'):
            decorator.registry = {}
        
        decorator.registry[func.__name__] = {
            'query': query,
            'func': func
        }
        
        return func
    return decorator

def grpc_task(proto, service=None):
    """Dekorator do rejestracji funkcji jako metody gRPC"""
    def decorator(func):
        if not hasattr(decorator, 'registry'):
            decorator.registry = {}
        
        decorator.registry[func.__name__] = {
            'proto': proto,
            'service': service or func.__name__,
            'func': func
        }
        
        return func
    return decorator

# Przykładowy system przetwarzania danych z dekoratorami
@text2python_task("Napisz funkcję, która pobiera dane z API")
@restapi_task("GET /api/data")
def fetch_data(source: str, limit: int = 100):
    """Pobiera dane z zewnętrznego API"""
    print(f"Pobieranie danych z {source}, limit: {limit}")
    # Symulacja pobierania danych
    return [{"id": i, "value": f"data_{i}"} for i in range(limit)]

@text2python_task("Napisz funkcję, która filtruje dane według kryteriów")
@graphql_task("""
type Query {
  filterData(data: [DataInput!]!, criteria: String!): [Data!]!
}

input DataInput {
  id: Int!
  value: String!
}

type Data {
  id: Int!
  value: String!
}
""")
def filter_data(data, criteria):
    """Filtruje dane według podanych kryteriów"""
    print(f"Filtrowanie danych według kryterium: {criteria}")
    # Symulacja filtrowania
    return [item for item in data if criteria in item["value"]]

@text2python_task("Napisz funkcję, która transformuje dane do innego formatu")
@grpc_task("""
syntax = "proto3";

message TransformRequest {
    repeated DataItem data = 1;
    string format = 2;
}

message DataItem {
    int32 id = 1;
    string value = 2;
}

message TransformResponse {
    string result = 1;
}

service TransformService {
    rpc Transform (TransformRequest) returns (TransformResponse);
}
""", service="TransformService")
def transform_data(data, format="json"):
    """Transformuje dane do określonego formatu"""
    print(f"Transformacja danych do formatu: {format}")
    if format.lower() == "json":
        return json.dumps(data)
    elif format.lower() == "csv":
        header = ",".join(data[0].keys()) if data else ""
        rows = [",".join(str(v) for v in item.values()) for item in data]
        return "\n".join([header] + rows)
    else:
        return str(data)

@text2python_task("Napisz funkcję, która zapisuje dane do bazy danych")
@restapi_task("POST /api/data/save")
@graphql_task("""
type Mutation {
  saveData(data: [DataInput!]!, destination: String!): SaveResult!
}

type SaveResult {
  success: Boolean!
  message: String
  count: Int!
}
""")
def save_data(data, destination):
    """Zapisuje dane do określonego miejsca docelowego"""
    print(f"Zapisywanie {len(data)} elementów do {destination}")
    # Symulacja zapisywania
    return {
        "success": True,
        "message": f"Zapisano {len(data)} elementów do {destination}",
        "count": len(data)
    }

@text2python_task("Napisz funkcję, która analizuje dane i generuje raport")
@restapi_task("POST /api/data/analyze")
def analyze_data(data, metrics=None):
    """Analizuje dane i generuje raport z metrykami"""
    if metrics is None:
        metrics = ["count", "avg", "min", "max"]
    
    print(f"Analizowanie danych z metrykami: {metrics}")
    
    # Symulacja analizy
    result = {"count": len(data)}
    
    if "avg" in metrics and data:
        # Zakładamy, że dane mają pole 'value' które można przekonwertować na liczbę
        try:
            values = [float(item["value"].split("_")[1]) for item in data]
            result["avg"] = sum(values) / len(values)
        except (ValueError, KeyError, IndexError):
            result["avg"] = None
    
    if "min" in metrics and data:
        try:
            values = [float(item["value"].split("_")[1]) for item in data]
            result["min"] = min(values)
        except (ValueError, KeyError, IndexError):
            result["min"] = None
    
    if "max" in metrics and data:
        try:
            values = [float(item["value"].split("_")[1]) for item in data]
            result["max"] = max(values)
        except (ValueError, KeyError, IndexError):
            result["max"] = None
    
    return result

def generate_function_info():
    """Generuje informacje o funkcjach i ich dekoratorach"""
    functions = [fetch_data, filter_data, transform_data, save_data, analyze_data]
    
    function_info = []
    for func in functions:
        info = {
            "name": func.__name__,
            "docstring": func.__doc__,
            "signature": str(inspect.signature(func)),
            "decorators": []
        }
        
        # Dodaj informacje o dekoratorach
        if func.__name__ in text2python_task.registry:
            info["decorators"].append({
                "type": "text2python_task",
                "prompt": text2python_task.registry[func.__name__]["prompt"]
            })
        
        if func.__name__ in restapi_task.registry:
            info["decorators"].append({
                "type": "restapi_task",
                "route": restapi_task.registry[func.__name__]["route"],
                "method": restapi_task.registry[func.__name__]["method"]
            })
        
        if func.__name__ in graphql_task.registry:
            info["decorators"].append({
                "type": "graphql_task",
                "query": graphql_task.registry[func.__name__]["query"]
            })
        
        if func.__name__ in grpc_task.registry:
            info["decorators"].append({
                "type": "grpc_task",
                "proto": grpc_task.registry[func.__name__]["proto"],
                "service": grpc_task.registry[func.__name__]["service"]
            })
        
        function_info.append(info)
    
    return function_info

def generate_decorator_network():
    """Generuje sieć połączeń między funkcjami i dekoratorami"""
    G = nx.Graph()
    
    # Dodaj węzły dla funkcji
    functions = [fetch_data, filter_data, transform_data, save_data, analyze_data]
    for func in functions:
        G.add_node(func.__name__, type='function')
    
    # Dodaj węzły dla dekoratorów
    decorators = ['text2python_task', 'restapi_task', 'graphql_task', 'grpc_task']
    for dec in decorators:
        G.add_node(dec, type='decorator')
    
    # Dodaj krawędzie
    for func in functions:
        if func.__name__ in text2python_task.registry:
            G.add_edge(func.__name__, 'text2python_task')
        
        if func.__name__ in restapi_task.registry:
            G.add_edge(func.__name__, 'restapi_task')
        
        if func.__name__ in graphql_task.registry:
            G.add_edge(func.__name__, 'graphql_task')
        
        if func.__name__ in grpc_task.registry:
            G.add_edge(func.__name__, 'grpc_task')
    
    # Zapisz wizualizację
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, seed=42)  # Ustaw seed dla powtarzalności
    
    # Rysuj węzły funkcji
    function_nodes = [n for n, attr in G.nodes(data=True) if attr.get('type') == 'function']
    nx.draw_networkx_nodes(G, pos, nodelist=function_nodes, node_color='lightblue', node_size=500)
    
    # Rysuj węzły dekoratorów
    decorator_nodes = [n for n, attr in G.nodes(data=True) if attr.get('type') == 'decorator']
    nx.draw_networkx_nodes(G, pos, nodelist=decorator_nodes, node_color='lightgreen', node_size=700)
    
    # Rysuj krawędzie
    nx.draw_networkx_edges(G, pos)
    
    # Rysuj etykiety
    nx.draw_networkx_labels(G, pos)
    
    plt.title("Funkcje i ich dekoratory")
    plt.axis('off')
    
    # Zapisz wykres
    try:
        plt.savefig('generated/visualizations/decorator_network.png')
    except Exception as e:
        print(f"Błąd podczas zapisywania wykresu: {e}")
        # Alternatywna metoda zapisywania
        plt.savefig('generated/visualizations/decorator_network.png', backend='Agg')
    
    return 'generated/visualizations/decorator_network.png'

def generate_flow_diagram():
    """Generuje diagram przepływu danych między funkcjami"""
    G = nx.DiGraph()
    
    # Dodaj węzły dla funkcji
    G.add_node('fetch_data', label='Pobierz dane\n(REST API)')
    G.add_node('filter_data', label='Filtruj dane\n(GraphQL)')
    G.add_node('transform_data', label='Transformuj dane\n(gRPC)')
    G.add_node('save_data', label='Zapisz dane\n(REST API + GraphQL)')
    G.add_node('analyze_data', label='Analizuj dane\n(REST API)')
    
    # Dodaj krawędzie
    G.add_edge('fetch_data', 'filter_data', label='dane')
    G.add_edge('filter_data', 'transform_data', label='przefiltrowane dane')
    G.add_edge('transform_data', 'save_data', label='przetransformowane dane')
    G.add_edge('fetch_data', 'analyze_data', label='surowe dane')
    G.add_edge('filter_data', 'analyze_data', label='przefiltrowane dane')
    
    # Zapisz wizualizację
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, seed=42)  # Ustaw seed dla powtarzalności
    
    # Rysuj węzły
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=2000)
    
    # Rysuj krawędzie
    nx.draw_networkx_edges(G, pos, edge_color='gray', width=1.5, arrowsize=20)
    
    # Rysuj etykiety węzłów
    node_labels = {node: data['label'] if 'label' in data else node for node, data in G.nodes(data=True)}
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10)
    
    # Rysuj etykiety krawędzi
    edge_labels = {(u, v): d['label'] for u, v, d in G.edges(data=True) if 'label' in d}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    
    plt.title("Przepływ danych między funkcjami")
    plt.axis('off')
    
    # Zapisz wykres
    try:
        plt.savefig('generated/visualizations/data_flow.png')
    except Exception as e:
        print(f"Błąd podczas zapisywania wykresu: {e}")
        # Alternatywna metoda zapisywania
        plt.savefig('generated/visualizations/data_flow.png', backend='Agg')
    
    return 'generated/visualizations/data_flow.png'

def generate_code_html():
    """Generuje kolorowany HTML z kodem funkcji"""
    functions = [fetch_data, filter_data, transform_data, save_data, analyze_data]
    
    html = '<div class="code-container">'
    formatter = HtmlFormatter(style='colorful', linenos=True)
    
    for func in functions:
        # Pobierz kod źródłowy funkcji
        source = inspect.getsource(func)
        
        # Koloruj kod
        highlighted = highlight(source, PythonLexer(), formatter)
        
        html += f'<div class="function-code">{highlighted}</div>'
    
    html += '</div>'
    
    # Dodaj CSS
    html += f'<style>{formatter.get_style_defs(".highlight")}</style>'
    html += '''
    <style>
    .code-container {
        display: flex;
        flex-direction: column;
        gap: 20px;
    }
    .function-code {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    '''
    
    # Zapisz HTML
    with open('generated/visualizations/code_highlight.html', 'w') as f:
        f.write(html)
    
    return 'generated/visualizations/code_highlight.html'

def generate_execution_log():
    """Generuje log wykonania funkcji"""
    # Symulacja przepływu danych
    print("=== Rozpoczęcie przepływu danych ===")
    
    # Krok 1: Pobierz dane
    data = fetch_data("example.com/api", 5)
    print(f"Pobrane dane: {data}")
    
    # Krok 2: Filtruj dane
    filtered_data = filter_data(data, "data_3")
    print(f"Przefiltrowane dane: {filtered_data}")
    
    # Krok 3: Transformuj dane
    transformed_data = transform_data(filtered_data, "json")
    print(f"Przetransformowane dane: {transformed_data}")
    
    # Krok 4: Zapisz dane
    save_result = save_data(filtered_data, "database")
    print(f"Wynik zapisywania: {save_result}")
    
    # Krok 5: Analizuj dane
    analysis = analyze_data(data)
    print(f"Wynik analizy: {analysis}")
    
    print("=== Zakończenie przepływu danych ===")

def generate_static_html():
    """Generuje statyczny HTML z wizualizacjami"""
    # Generuj wizualizacje
    print("Generowanie sieci dekoratorów...")
    decorator_network = generate_decorator_network()
    
    print("Generowanie diagramu przepływu danych...")
    flow_diagram = generate_flow_diagram()
    
    print("Generowanie kolorowanego kodu...")
    code_html = generate_code_html()
    
    print("Generowanie logów wykonania...")
    import io
    import sys
    
    # Przechwyć stdout
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    
    # Wykonaj przepływ danych
    generate_execution_log()
    
    # Przywróć stdout i pobierz logi
    sys.stdout = old_stdout
    log = new_stdout.getvalue()
    
    # Przygotuj dane dla szablonu
    function_info = generate_function_info()
    
    # Wygeneruj HTML
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Wizualizacja dekoratorów Devopy</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
            .section {{ margin-bottom: 30px; }}
            h1, h2 {{ color: #333; }}
            .diagram {{ max-width: 100%; border: 1px solid #ddd; border-radius: 5px; }}
            pre {{ background: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }}
            .function-card {{ border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin-bottom: 15px; }}
            .decorator-tag {{ display: inline-block; padding: 3px 8px; border-radius: 3px; margin-right: 5px; font-size: 0.8em; }}
            .text2python {{ background: #e6f7ff; color: #0066cc; }}
            .restapi {{ background: #e6ffe6; color: #006600; }}
            .graphql {{ background: #ffe6f0; color: #cc0066; }}
            .grpc {{ background: #fff2e6; color: #cc6600; }}
            .tabs {{ display: flex; }}
            .tab {{ padding: 10px 20px; cursor: pointer; background: #f0f0f0; border: 1px solid #ddd; }}
            .tab.active {{ background: #fff; border-bottom: none; }}
            .tab-content {{ display: none; padding: 20px; border: 1px solid #ddd; }}
            .tab-content.active {{ display: block; }}
        </style>
    </head>
    <body>
        <h1>Wizualizacja dekoratorów Devopy</h1>
        
        <div class="section">
            <h2>Diagramy</h2>
            <div class="tabs">
                <div class="tab active" onclick="showTab('decorator-network')">Sieć dekoratorów</div>
                <div class="tab" onclick="showTab('flow-diagram')">Przepływ danych</div>
            </div>
            <div id="decorator-network" class="tab-content active">
                <img src="{decorator_network.replace('generated/', '')}" alt="Sieć dekoratorów" class="diagram">
                <p>Diagram przedstawia połączenia między funkcjami (niebieskie węzły) a dekoratorami (zielone węzły).</p>
            </div>
            <div id="flow-diagram" class="tab-content">
                <img src="{flow_diagram.replace('generated/', '')}" alt="Przepływ danych" class="diagram">
                <p>Diagram przedstawia przepływ danych między funkcjami w systemie.</p>
            </div>
        </div>
        
        <div class="section">
            <h2>Funkcje i ich dekoratory</h2>
    '''
    
    # Dodaj karty funkcji
    for func in function_info:
        html += f'''
        <div class="function-card">
            <h3>{func['name']}{func['signature']}</h3>
            <p>{func['docstring']}</p>
            <div>
        '''
        
        # Dodaj tagi dekoratorów
        for dec in func['decorators']:
            if dec['type'] == 'text2python_task':
                html += f'<span class="decorator-tag text2python">@text2python_task</span>'
            elif dec['type'] == 'restapi_task':
                html += f'<span class="decorator-tag restapi">@restapi_task {dec["method"]} {dec["route"]}</span>'
            elif dec['type'] == 'graphql_task':
                html += f'<span class="decorator-tag graphql">@graphql_task</span>'
            elif dec['type'] == 'grpc_task':
                html += f'<span class="decorator-tag grpc">@grpc_task {dec["service"]}</span>'
        
        html += '''
            </div>
        </div>
        '''
    
    # Dodaj kolorowany kod
    with open(code_html, 'r') as f:
        code_content = f.read()
    
    html += f'''
        <div class="section">
            <h2>Kod źródłowy</h2>
            {code_content}
        </div>
        
        <div class="section">
            <h2>Logi wykonania</h2>
            <pre id="execution-log">{log}</pre>
        </div>
        
        <script>
            function showTab(tabId) {{
                // Ukryj wszystkie zakładki
                document.querySelectorAll('.tab-content').forEach(tab => {{
                    tab.classList.remove('active');
                }});
                document.querySelectorAll('.tab').forEach(tab => {{
                    tab.classList.remove('active');
                }});
                
                // Pokaż wybraną zakładkę
                document.getElementById(tabId).classList.add('active');
                document.querySelector(`.tab[onclick="showTab('${{tabId}}')"]`).classList.add('active');
            }}
        </script>
    </body>
    </html>
    '''
    
    # Zapisz HTML
    with open('generated/visualizations/index.html', 'w') as f:
        f.write(html)
    
    return 'generated/visualizations/index.html'

if __name__ == "__main__":
    # Inicjalizacja rejestrów dekoratorów
    text2python_task.registry = {}
    restapi_task.registry = {}
    graphql_task.registry = {}
    grpc_task.registry = {}
    
    # Generuj statyczny HTML
    print("Generowanie statycznego HTML...")
    html_file = generate_static_html()
    
    print(f"\nWizualizacja została wygenerowana i zapisana w pliku: {html_file}")
    print("Możesz otworzyć ten plik w przeglądarce, aby zobaczyć wizualizację.")
