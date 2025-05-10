from functools import wraps

# Prosty rejestr usług gRPC w pamięci procesu
GRPC_TASK_REGISTRY = []

def grpc_task(proto: str, service: str = None):
    """
    Dekorator do rejestracji funkcji jako metoda gRPC.
    Przykład: @grpc_task("service Fibonacci { rpc Compute (FiboRequest) returns (FiboResponse); }", service="Fibonacci")
    """
    def decorator(func):
        # Zachowaj oryginalne atrybuty funkcji
        original_attrs = {k: getattr(func, k) for k in dir(func) if k.startswith('_')}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Dodaj nowe atrybuty
        wrapper._grpc_proto = proto
        wrapper._grpc_service = service
        
        # Przywróć oryginalne atrybuty
        for k, v in original_attrs.items():
            setattr(wrapper, k, v)
        
        # Zarejestruj funkcję
        GRPC_TASK_REGISTRY.append((wrapper, proto, service))
        
        return wrapper
    return decorator

def get_registered_grpc_tasks():
    return GRPC_TASK_REGISTRY
