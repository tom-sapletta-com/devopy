import os
import sys
import inspect
import json
import graphviz
import matplotlib.pyplot as plt
import networkx as nx
from flask import Flask, render_template, jsonify
from pyvis.network import Network
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

# Dodaj ścieżkę projektu do PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from devopy.converters.text2python_decorator import text2python_task
from devopy.converters.restapi_task import restapi_task, get_registered_restapi_tasks
from devopy.converters.graphql_task import graphql_task, get_registered_graphql_tasks
from devopy.converters.grpc_task import grpc_task, get_registered_grpc_tasks

# Aplikacja Flask do wizualizacji
app = Flask(__name__)

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
        if hasattr(func, "_text2python_prompt"):
            info["decorators"].append({
                "type": "text2python_task",
                "prompt": func._text2python_prompt
            })
        
        if hasattr(func, "_restapi_route"):
            info["decorators"].append({
                "type": "restapi_task",
                "route": func._restapi_route,
                "method": func._restapi_method
            })
        
        if hasattr(func, "_graphql_query"):
            info["decorators"].append({
                "type": "graphql_task",
                "query": func._graphql_query
            })
        
        if hasattr(func, "_grpc_proto"):
            info["decorators"].append({
                "type": "grpc_task",
                "proto": func._grpc_proto,
                "service": func._grpc_service
            })
        
        function_info.append(info)
    
    return function_info

def generate_flow_diagram():
    """Generuje diagram przepływu danych między funkcjami"""
    dot = graphviz.Digraph(comment='Data Processing Flow')
    
    # Dodaj węzły dla funkcji
    dot.node('fetch_data', 'Fetch Data\n(REST API)')
    dot.node('filter_data', 'Filter Data\n(GraphQL)')
    dot.node('transform_data', 'Transform Data\n(gRPC)')
    dot.node('save_data', 'Save Data\n(REST API + GraphQL)')
    dot.node('analyze_data', 'Analyze Data\n(REST API)')
    
    # Dodaj krawędzie
    dot.edge('fetch_data', 'filter_data', label='data')
    dot.edge('filter_data', 'transform_data', label='filtered data')
    dot.edge('transform_data', 'save_data', label='transformed data')
    dot.edge('fetch_data', 'analyze_data', label='raw data')
    dot.edge('filter_data', 'analyze_data', label='filtered data')
    
    # Zapisz diagram
    os.makedirs("generated/visualizations", exist_ok=True)
    dot.render('generated/visualizations/data_flow', format='png')
    
    return 'generated/visualizations/data_flow.png'

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
        # Zawsze dodaj text2python_task
        G.add_edge(func.__name__, 'text2python_task')
        
        if hasattr(func, '_restapi_route'):
            G.add_edge(func.__name__, 'restapi_task')
        
        if hasattr(func, '_graphql_query'):
            G.add_edge(func.__name__, 'graphql_task')
        
        if hasattr(func, '_grpc_proto'):
            G.add_edge(func.__name__, 'grpc_task')
    
    # Zapisz wizualizację
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G)
    
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
    plt.savefig('generated/visualizations/decorator_network.png')
    
    # Utwórz interaktywną wizualizację z pyvis
    net = Network(height='600px', width='100%', notebook=False)
    
    # Dodaj węzły
    for node, attr in G.nodes(data=True):
        if attr.get('type') == 'function':
            net.add_node(node, label=node, color='lightblue', title=f"Funkcja: {node}")
        else:
            net.add_node(node, label=node, color='lightgreen', title=f"Dekorator: {node}")
    
    # Dodaj krawędzie
    for edge in G.edges():
        net.add_edge(edge[0], edge[1])
    
    # Zapisz interaktywną wizualizację
    net.save_graph('generated/visualizations/interactive_network.html')
    
    return 'generated/visualizations/decorator_network.png', 'generated/visualizations/interactive_network.html'

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

# Trasy Flask do wizualizacji
@app.route('/')
def index():
    """Strona główna z wizualizacjami"""
    # Generuj wizualizacje
    flow_diagram = generate_flow_diagram()
    decorator_network, interactive_network = generate_decorator_network()
    code_html = generate_code_html()
    
    # Przygotuj dane dla szablonu
    data = {
        'flow_diagram': flow_diagram,
        'decorator_network': decorator_network,
        'interactive_network': interactive_network,
        'code_html': code_html,
        'function_info': generate_function_info()
    }
    
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
            .tabs {{ display: flex; }}
            .tab {{ padding: 10px 20px; cursor: pointer; background: #f0f0f0; border: 1px solid #ddd; }}
            .tab.active {{ background: #fff; border-bottom: none; }}
            .tab-content {{ display: none; padding: 20px; border: 1px solid #ddd; }}
            .tab-content.active {{ display: block; }}
            pre {{ background: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }}
            .function-card {{ border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin-bottom: 15px; }}
            .decorator-tag {{ display: inline-block; padding: 3px 8px; border-radius: 3px; margin-right: 5px; font-size: 0.8em; }}
            .text2python {{ background: #e6f7ff; color: #0066cc; }}
            .restapi {{ background: #e6ffe6; color: #006600; }}
            .graphql {{ background: #ffe6f0; color: #cc0066; }}
            .grpc {{ background: #fff2e6; color: #cc6600; }}
            iframe {{ width: 100%; height: 500px; border: none; }}
        </style>
    </head>
    <body>
        <h1>Wizualizacja dekoratorów Devopy</h1>
        
        <div class="section">
            <h2>Diagram przepływu danych</h2>
            <img src="{flow_diagram.replace('generated/', '')}" alt="Diagram przepływu danych" class="diagram">
        </div>
        
        <div class="section">
            <h2>Sieć dekoratorów</h2>
            <div class="tabs">
                <div class="tab active" onclick="showTab('static-network')">Statyczna wizualizacja</div>
                <div class="tab" onclick="showTab('interactive-network')">Interaktywna wizualizacja</div>
            </div>
            <div id="static-network" class="tab-content active">
                <img src="{decorator_network.replace('generated/', '')}" alt="Sieć dekoratorów" class="diagram">
            </div>
            <div id="interactive-network" class="tab-content">
                <iframe src="{interactive_network.replace('generated/', '')}"></iframe>
            </div>
        </div>
        
        <div class="section">
            <h2>Funkcje i ich dekoratory</h2>
    '''
    
    # Dodaj karty funkcji
    for func in generate_function_info():
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
            <pre id="execution-log">Uruchamianie przepływu danych...</pre>
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
            
            // Symulacja logów wykonania
            fetch('/execute')
                .then(response => response.json())
                .then(data => {{
                    document.getElementById('execution-log').textContent = data.log;
                }});
        </script>
    </body>
    </html>
    '''
    
    # Zapisz HTML
    with open('generated/visualizations/index.html', 'w') as f:
        f.write(html)
    
    return html

@app.route('/execute')
def execute():
    """Wykonuje przepływ danych i zwraca logi"""
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
    
    return jsonify({"log": log})

if __name__ == "__main__":
    # Utwórz katalog na wizualizacje
    os.makedirs("generated/visualizations", exist_ok=True)
    
    # Generuj wizualizacje
    print("Generowanie diagramu przepływu danych...")
    flow_diagram = generate_flow_diagram()
    
    print("Generowanie sieci dekoratorów...")
    decorator_network, interactive_network = generate_decorator_network()
    
    print("Generowanie kolorowanego kodu...")
    code_html = generate_code_html()
    
    print("Uruchamianie serwera Flask...")
    app.run(debug=True, port=8080)
