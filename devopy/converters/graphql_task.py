from functools import wraps

# Prosty rejestr usług GraphQL w pamięci procesu
GRAPHQL_TASK_REGISTRY = []

def graphql_task(query: str):
    """
    Dekorator do rejestracji funkcji jako resolver GraphQL.
    Przykład: @graphql_task("type Query { fibonacci(n: Int!): Int! }")
    """
    def decorator(func):
        # Zachowaj oryginalne atrybuty funkcji
        original_attrs = {k: getattr(func, k) for k in dir(func) if k.startswith('_')}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Dodaj nowe atrybuty
        wrapper._graphql_query = query
        
        # Przywróć oryginalne atrybuty
        for k, v in original_attrs.items():
            setattr(wrapper, k, v)
        
        # Zarejestruj funkcję
        GRAPHQL_TASK_REGISTRY.append((wrapper, query))
        
        return wrapper
    return decorator

def get_registered_graphql_tasks():
    return GRAPHQL_TASK_REGISTRY
