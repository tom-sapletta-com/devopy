from functools import wraps

# Prosty rejestr usług Docker w pamięci procesu
DOCKER_TASK_REGISTRY = []

def docker_task(image: str, port: int = None, env_vars: dict = None, command: str = None):
    """
    Dekorator do rejestracji funkcji jako usługi Docker.
    Przykład: @docker_task("python:3.9", port=8000, env_vars={"DEBUG": "true"})
    """
    def decorator(func):
        # Zachowaj oryginalne atrybuty funkcji
        original_attrs = {k: getattr(func, k) for k in dir(func) if k.startswith('_')}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Dodaj nowe atrybuty
        wrapper._docker_image = image
        wrapper._docker_port = port
        wrapper._docker_env_vars = env_vars or {}
        wrapper._docker_command = command
        
        # Przywróć oryginalne atrybuty
        for k, v in original_attrs.items():
            setattr(wrapper, k, v)
        
        # Zarejestruj funkcję
        DOCKER_TASK_REGISTRY.append((wrapper, image, port, env_vars, command))
        
        return wrapper
    return decorator

def get_registered_docker_tasks():
    return DOCKER_TASK_REGISTRY

def generate_dockerfile(func):
    """Generuje zawartość pliku Dockerfile dla funkcji"""
    dockerfile = f"FROM {func._docker_image}\n\n"
    
    if hasattr(func, "_docker_command") and func._docker_command:
        dockerfile += f"CMD {func._docker_command}\n"
    
    return dockerfile

def generate_docker_compose(tasks):
    """Generuje zawartość pliku docker-compose.yml dla listy zadań"""
    compose = "version: '3'\n\nservices:\n"
    
    for i, (func, image, port, env_vars, command) in enumerate(tasks):
        service_name = func.__name__
        compose += f"  {service_name}:\n"
        compose += f"    image: {image}\n"
        
        if port:
            compose += f"    ports:\n"
            compose += f"      - \"{port}:{port}\"\n"
        
        if env_vars:
            compose += f"    environment:\n"
            for key, value in env_vars.items():
                compose += f"      - {key}={value}\n"
        
        if command:
            compose += f"    command: {command}\n"
        
        # Dodaj sieć, jeśli to nie ostatnia usługa
        if i < len(tasks) - 1:
            compose += "\n"
    
    return compose
