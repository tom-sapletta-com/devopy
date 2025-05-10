from devopy.converters.text2python_decorator import text2python_task

@text2python_task("Napisz funkcję, która oblicza n-ty wyraz ciągu Fibonacciego")
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

if __name__ == "__main__":
    print(fibonacci(10))
    print("Prompt:", fibonacci._text2python_prompt)
    print("Model:", fibonacci._text2python_model)
