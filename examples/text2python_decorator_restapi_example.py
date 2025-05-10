from devopy.converters.text2python_decorator import text2python_task
from devopy.converters.restapi_task import restapi_task, get_registered_restapi_tasks

@text2python_task("Napisz funkcję, która oblicza n-ty wyraz ciągu Fibonacciego")
@restapi_task("GET http://localhost:8000/fibonacci")
def fibonacci(n: int):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

if __name__ == "__main__":
    print(fibonacci(10))
    print("Prompt:", fibonacci._text2python_prompt)
    print("Model:", fibonacci._text2python_model)
    print("REST route:", fibonacci._restapi_route)
    print("REST method:", fibonacci._restapi_method)
    print("Zarejestrowane endpointy:", get_registered_restapi_tasks())
