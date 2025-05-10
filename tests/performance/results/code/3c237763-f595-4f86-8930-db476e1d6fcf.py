```
def execute(text):
    vowels = ['a', 'e', 'i', 'o', 'u']
    result = [char for char in text.lower() if char in vowels]
    return ''.join(result)