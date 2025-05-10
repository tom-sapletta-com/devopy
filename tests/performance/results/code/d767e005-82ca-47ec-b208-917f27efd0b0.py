```
def execute(text):
    vowels = 'aeiouy'
    return [char for char in text.lower() if char in vowels]