import os
from functools import wraps
from dotenv import load_dotenv

# Automatycznie załaduj zmienne środowiskowe z .env/env.local jeśli istnieją
load_dotenv(os.path.join(os.path.dirname(__file__), '../../sandbox/.env'), override=True)
load_dotenv(os.path.join(os.path.dirname(__file__), '../../sandbox/env.local'), override=True)

MODEL_NAME = os.getenv('MODEL_NAME', 'codellama:7b-code')


def text2python_task(prompt=None, **kwargs):
    """
    Dekorator do oznaczania funkcji generowanych z promptu tekstowego.
    Model jest pobierany automatycznie z .env lub env.local.
    Pozwala na wywołanie zarówno @text2python_task(prompt=...), jak i @text2python_task("prompt...")
    """
    # Obsługa wywołania z pozycyjnym promptem
    if callable(prompt):
        raise TypeError("Dekorator text2python_task musi być wywołany z promptem jako argumentem!")
    def decorator(func):
        # Zachowaj oryginalne atrybuty funkcji
        original_attrs = {k: getattr(func, k) for k in dir(func) if k.startswith('_')}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Dodaj nowe atrybuty
        wrapper._text2python_prompt = prompt
        wrapper._text2python_model = MODEL_NAME
        
        # Przywróć oryginalne atrybuty
        for k, v in original_attrs.items():
            setattr(wrapper, k, v)
        
        return wrapper
    return decorator
