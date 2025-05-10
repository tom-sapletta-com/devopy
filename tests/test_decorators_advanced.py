import pytest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock

from devopy.converters.text2python_decorator import text2python_task
from devopy.converters.restapi_task import restapi_task, get_registered_restapi_tasks
from devopy.converters.graphql_task import graphql_task, get_registered_graphql_tasks
from devopy.converters.grpc_task import grpc_task, get_registered_grpc_tasks

class TestDecoratorsAdvanced:
    """Zaawansowane testy dla dekoratorów"""
    
    def test_restapi_task_url_parsing(self):
        """Test parsowania różnych formatów URL w restapi_task"""
        
        # Format "GET /endpoint"
        @restapi_task("GET /test")
        def test_func1(x):
            return x
        
        assert test_func1._restapi_route == "/test"
        assert test_func1._restapi_method == "GET"
        
        # Format "POST http://localhost:8000/endpoint"
        @restapi_task("POST http://localhost:8000/submit")
        def test_func2(x):
            return x
        
        assert test_func2._restapi_route == "/submit"
        assert test_func2._restapi_method == "POST"
        
        # Format z parametrami
        @restapi_task("/users", method="PUT")
        def test_func3(x):
            return x
        
        assert test_func3._restapi_route == "/users"
        assert test_func3._restapi_method == "PUT"
    
    def test_multiple_registrations(self):
        """Test rejestracji wielu funkcji w rejestrach"""
        
        # Wyczyść rejestry przed testem
        from devopy.converters.restapi_task import RESTAPI_TASK_REGISTRY
        from devopy.converters.graphql_task import GRAPHQL_TASK_REGISTRY
        from devopy.converters.grpc_task import GRPC_TASK_REGISTRY
        
        RESTAPI_TASK_REGISTRY.clear()
        GRAPHQL_TASK_REGISTRY.clear()
        GRPC_TASK_REGISTRY.clear()
        
        # Zarejestruj kilka funkcji
        @restapi_task("GET /func1")
        def func1(x):
            return x
        
        @restapi_task("GET /func2")
        def func2(x):
            return x
        
        @graphql_task("type Query { func3(x: Int!): Int! }")
        def func3(x):
            return x
        
        @grpc_task("service Test { rpc Func4(Request) returns (Response); }")
        def func4(x):
            return x
        
        # Sprawdź, czy wszystkie funkcje zostały zarejestrowane
        rest_tasks = get_registered_restapi_tasks()
        graphql_tasks = get_registered_graphql_tasks()
        grpc_tasks = get_registered_grpc_tasks()
        
        assert len(rest_tasks) == 2
        assert len(graphql_tasks) == 1
        assert len(grpc_tasks) == 1
        
        # Sprawdź, czy funkcje są poprawnie zarejestrowane
        rest_func_names = [func.__name__ for func, _, _ in rest_tasks]
        graphql_func_names = [func.__name__ for func, _ in graphql_tasks]
        grpc_func_names = [func.__name__ for func, _, _ in grpc_tasks]
        
        assert "func1" in rest_func_names
        assert "func2" in rest_func_names
        assert "func3" in graphql_func_names
        assert "func4" in grpc_func_names
    
    @patch('os.getenv')
    def test_text2python_model_from_env(self, mock_getenv):
        """Test pobierania modelu z zmiennych środowiskowych"""
        
        # Ustaw mock dla os.getenv
        mock_getenv.return_value = "gpt-4"
        
        @text2python_task("Test prompt")
        def test_func(x):
            return x
        
        # Sprawdź, czy model został pobrany z zmiennych środowiskowych
        assert test_func._text2python_model == "gpt-4"
        
        # Sprawdź, czy mock został wywołany z odpowiednim argumentem
        mock_getenv.assert_called_with('MODEL_NAME', 'codellama:7b-code')
    
    def test_function_execution_with_decorators(self):
        """Test wykonania funkcji z dekoratorami"""
        
        @text2python_task("Test prompt")
        @restapi_task("GET /calculate")
        @graphql_task("type Query { calculate(a: Int!, b: Int!): Int! }")
        def add(a, b):
            return a + b
        
        # Sprawdź, czy funkcja działa poprawnie
        assert add(2, 3) == 5
        assert add(10, 20) == 30
        
        # Sprawdź, czy metadane są dostępne
        assert add._text2python_prompt == "Test prompt"
        assert add._restapi_route == "/calculate"
        assert add._restapi_method == "GET"
        assert add._graphql_query == "type Query { calculate(a: Int!, b: Int!): Int! }"

    def test_function_with_complex_arguments(self):
        """Test funkcji z złożonymi argumentami"""
        
        @restapi_task("POST /process")
        def process_data(data, options=None):
            if options is None:
                options = {}
            return {"processed": data, "options": options}
        
        # Wywołaj funkcję z różnymi argumentami
        result1 = process_data("test")
        result2 = process_data("test", {"verbose": True})
        
        assert result1 == {"processed": "test", "options": {}}
        assert result2 == {"processed": "test", "options": {"verbose": True}}
        
        # Sprawdź, czy metadane są dostępne
        assert process_data._restapi_route == "/process"
        assert process_data._restapi_method == "POST"
