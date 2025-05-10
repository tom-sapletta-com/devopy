```
def execute(text):
    vowels = ['a', 'e', 'i', 'o', 'u']
    return ''.join([char for char in text.lower() if char in vowels])