from devopy.converters.text2python_decorator import text2python_task
from devopy.converters.restapi_task import restapi_task
from devopy.converters.graphql_task import graphql_task
from devopy.converters.grpc_task import grpc_task

@text2python_task("Napisz funkcję, która oblicza n-ty wyraz ciągu Fibonacciego")
@restapi_task("GET http://localhost:8000/fibonacci")
@graphql_task("type Query { fibonacci(n: Int!): Int! }")
@grpc_task('service Fibonacci { rpc Compute (FiboRequest) returns (FiboResponse); }', service='Fibonacci')
def fibonacci(n: int, x: int):
    return x

if __name__ == "__main__":
    print(fibonacci(10, 0))  # Przekazujemy wartość x=55
    print("Prompt:", fibonacci._text2python_prompt)
    print("REST route:", fibonacci._restapi_route)
    print("GraphQL query:", fibonacci._graphql_query)
    print("gRPC proto:", fibonacci._grpc_proto)
    print("gRPC service:", fibonacci._grpc_service)
