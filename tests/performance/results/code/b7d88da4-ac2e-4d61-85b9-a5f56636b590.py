def execute(text):
    vowels = 'aeiouy'
    return [char for char in text if char.lower() in vowels]