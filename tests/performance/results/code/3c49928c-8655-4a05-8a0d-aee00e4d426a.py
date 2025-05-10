def execute(text):
    vowels = ['a', 'e', 'i', 'o', 'u']
    return [char for char in text.lower() if char in vowels]