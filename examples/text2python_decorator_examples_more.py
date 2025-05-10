from devopy.converters.text2python_decorator import text2python_task

@text2python_task("Napisz funkcję, która sortuje listę liczb algorytmem quicksort")
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

@text2python_task("Napisz funkcję, która analizuje plik CSV i generuje wykres liczby wierszy na kolumnę")
def analyze_csv_and_plot(filename):
    import pandas as pd
    import matplotlib.pyplot as plt
    df = pd.read_csv(filename)
    df.count().plot(kind='bar')
    plt.title('Liczba wierszy na kolumnę')
    plt.savefig('output.png')
    return 'output.png'

@text2python_task("Napisz funkcję, która wyjaśnia działanie podanego kodu Python")
def explain_code(code):
    return "To przykładowe wyjaśnienie kodu."

@text2python_task("Napisz funkcję, która ulepsza podany kod Python")
def improve_code(code):
    return code + "\n# Kod został ulepszony."

if __name__ == "__main__":
    print("Quicksort:", quicksort([5,3,8,2,1]))
    print("Prompt quicksort:", quicksort._text2python_prompt)
    print("Model quicksort:", quicksort._text2python_model)
    print("Wyjaśnienie kodu:", explain_code('def foo(): pass'))
    print("Ulepszony kod:", improve_code('def foo(): pass'))
