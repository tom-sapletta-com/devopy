import pytest
from devopy.converters.text2python_decorator import text2python_task
from devopy.converters.restapi_task import restapi_task, get_registered_restapi_tasks
from devopy.converters.graphql_task import graphql_task, get_registered_graphql_tasks
from devopy.converters.grpc_task import grpc_task, get_registered_grpc_tasks

def test_text2python_decorator():
    @text2python_task("Test prompt")
    def test_func(x):
        return x
    
    assert test_func._text2python_prompt == "Test prompt"
    assert hasattr(test_func, "_text2python_model")
    assert test_func(42) == 42

def test_restapi_decorator():
    @restapi_task("GET /test")
    def test_func(x):
        return x
    
    assert test_func._restapi_route == "/test"
    assert test_func._restapi_method == "GET"
    assert test_func(42) == 42
    
    # Sprawdź, czy funkcja została zarejestrowana
    tasks = get_registered_restapi_tasks()
    assert any(func.__name__ == test_func.__name__ for func, _, _ in tasks)

def test_graphql_decorator():
    @graphql_task("type Query { test(x: Int!): Int! }")
    def test_func(x):
        return x
    
    assert test_func._graphql_query == "type Query { test(x: Int!): Int! }"
    assert test_func(42) == 42
    
    # Sprawdź, czy funkcja została zarejestrowana
    tasks = get_registered_graphql_tasks()
    assert any(func.__name__ == test_func.__name__ for func, _ in tasks)

def test_grpc_decorator():
    @grpc_task("service Test { rpc Run(Request) returns (Response); }", service="Test")
    def test_func(x):
        return x
    
    assert test_func._grpc_proto == "service Test { rpc Run(Request) returns (Response); }"
    assert test_func._grpc_service == "Test"
    assert test_func(42) == 42
    
    # Sprawdź, czy funkcja została zarejestrowana
    tasks = get_registered_grpc_tasks()
    assert any(func.__name__ == test_func.__name__ for func, _, _ in tasks)

def test_multiple_decorators():
    @text2python_task("Multi test")
    @restapi_task("GET /multi")
    @graphql_task("type Query { multi(x: Int!): Int! }")
    @grpc_task("service Multi { rpc Run(Request) returns (Response); }", service="Multi")
    def test_func(x):
        return x
    
    # Sprawdź, czy wszystkie metadane są dostępne
    assert test_func._text2python_prompt == "Multi test"
    assert test_func._restapi_route == "/multi"
    assert test_func._graphql_query == "type Query { multi(x: Int!): Int! }"
    assert test_func._grpc_proto == "service Multi { rpc Run(Request) returns (Response); }"
    assert test_func._grpc_service == "Multi"
    
    # Sprawdź, czy funkcja działa poprawnie
    assert test_func(42) == 42
