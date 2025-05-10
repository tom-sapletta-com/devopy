from functools import wraps

# Prosty rejestr usług REST w pamięci procesu
RESTAPI_TASK_REGISTRY = []

def restapi_task(route: str, method: str = "GET"):
    """
    Dekorator do rejestracji funkcji jako endpoint REST API.
    Przykład: @restapi_task("/fibonacci", method="GET")
    Lub: @restapi_task("GET http://localhost:8000/fibonacci")
    """
    # Pozwala na format: "GET /endpoint" lub "GET http://..."
    if " " in route:
        method, route = route.split(" ", 1)
        route = route.replace("http://localhost:8000", "")
    def decorator(func):
        # Zachowaj oryginalne atrybuty funkcji
        original_attrs = {k: getattr(func, k) for k in dir(func) if k.startswith('_')}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Dodaj nowe atrybuty
        wrapper._restapi_route = route
        wrapper._restapi_method = method.upper()
        
        # Przywróć oryginalne atrybuty
        for k, v in original_attrs.items():
            setattr(wrapper, k, v)
        
        # Zarejestruj funkcję
        RESTAPI_TASK_REGISTRY.append((wrapper, route, method.upper()))
        
        return wrapper
    return decorator

def get_registered_restapi_tasks():
    return RESTAPI_TASK_REGISTRY
