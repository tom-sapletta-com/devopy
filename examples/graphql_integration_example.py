from flask import Flask
from graphene import ObjectType, String, Int, List, Schema, Field
from flask_graphql import GraphQLView
import inspect
import os
import sys
import re

# Dodaj ścieżkę projektu do PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from devopy.converters.text2python_decorator import text2python_task
from devopy.converters.graphql_task import graphql_task, get_registered_graphql_tasks

app = Flask(__name__)

# Przykładowe funkcje z dekoratorami
@text2python_task("Napisz funkcję, która oblicza n-ty wyraz ciągu Fibonacciego")
@graphql_task("type Query { fibonacci(n: Int!): Int! }")
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
@graphql_task("type Mutation { sort(numbers: [Int!]!): [Int!]! }")
def sort_numbers(numbers):
    """Sortuje listę liczb"""
    return sorted(numbers)

@text2python_task("Napisz funkcję, która analizuje tekst i zwraca statystyki")
@graphql_task("""
type TextStats {
  words: Int!
  sentences: Int!
  characters: Int!
  averageWordLength: Float!
}

type Query {
  analyzeText(text: String!): TextStats!
}
""")
def analyze_text(text):
    """Analizuje tekst i zwraca statystyki"""
    words = text.split()
    sentences = text.split('.')
    return {
        "words": len(words),
        "sentences": len(sentences),
        "characters": len(text),
        "averageWordLength": sum(len(word) for word in words) / len(words) if words else 0
    }

def parse_graphql_schema(query_str):
    """Parsuje schemat GraphQL z ciągu znaków"""
    # Znajdź definicje typów
    type_defs = re.findall(r'type\s+(\w+)\s*{([^}]*)}', query_str)
    
    # Znajdź definicje pól
    result = {}
    for type_name, fields_str in type_defs:
        fields = {}
        for field_def in re.findall(r'(\w+)(?:\(([^)]*)\))?\s*:\s*([^!,\s]+)(!)?', fields_str):
            field_name, args_str, field_type, required = field_def
            fields[field_name] = {
                'type': field_type,
                'required': bool(required),
                'args': {}
            }
            
            # Parsuj argumenty
            if args_str:
                for arg_def in re.findall(r'(\w+)\s*:\s*([^!,\s]+)(!)?', args_str):
                    arg_name, arg_type, arg_required = arg_def
                    fields[field_name]['args'][arg_name] = {
                        'type': arg_type,
                        'required': bool(arg_required)
                    }
        
        result[type_name] = fields
    
    return result

def create_graphql_schema():
    """Tworzy schemat GraphQL na podstawie zarejestrowanych funkcji"""
    # Klasy dla typów Query i Mutation
    class Query(ObjectType):
        pass
    
    class Mutation(ObjectType):
        pass
    
    # Słownik niestandardowych typów
    custom_types = {}
    
    # Zarejestruj wszystkie funkcje
    for func, query_str in get_registered_graphql_tasks():
        # Parsuj schemat GraphQL
        schema_info = parse_graphql_schema(query_str)
        
        # Dodaj pola do Query lub Mutation
        for type_name, fields in schema_info.items():
            if type_name == 'Query':
                for field_name, field_info in fields.items():
                    # Dodaj pole do Query
                    if field_name == func.__name__ or field_name == 'fibonacci' or field_name == 'analyzeText':
                        setattr(Query, field_name, Field(lambda: Int, resolver=func))
            elif type_name == 'Mutation':
                for field_name, field_info in fields.items():
                    # Dodaj pole do Mutation
                    if field_name == func.__name__ or field_name == 'sort':
                        setattr(Mutation, field_name, Field(lambda: List(Int), resolver=func))
    
    # Utwórz schemat
    schema = Schema(query=Query, mutation=Mutation)
    return schema

# Utwórz schemat GraphQL
schema = create_graphql_schema()

# Dodaj endpoint GraphQL
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True  # Włącz interfejs GraphiQL
    )
)

if __name__ == "__main__":
    print("Uruchamianie serwera GraphQL na http://localhost:5000/graphql")
    app.run(debug=True, port=5000)
