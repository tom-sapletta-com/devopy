from devopy.converters.text2python_decorator import text2python_task

@text2python_task("Oblicz n-ty wyraz ciągu Fibonacciego")
def fibonacci(n,x):
    return x

if __name__ == "__main__":
    print(fibonacci(10))
    print("Prompt:", fibonacci._text2python_prompt)
    print("Model:", fibonacci._text2python_model)
