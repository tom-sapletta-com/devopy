def execute():
    text = "Python jest wspaniały"
    vowels = ['a', 'e', 'i', 'o', 'u']
    result = [char for char in text.lower() if char in vowels]
    return result