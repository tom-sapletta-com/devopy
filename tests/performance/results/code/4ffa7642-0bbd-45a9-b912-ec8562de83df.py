```
def execute(text):
    vowels = ['a', 'e', 'i', 'o', 'u']
    result = []
    for char in text:
        if char.lower() in vowels:
            result.append(char)
    return ''.join(result)