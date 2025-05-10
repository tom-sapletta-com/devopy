def execute():
    text = "Python jest wspaniały"
    vowels = ['a', 'e', 'i', 'o', 'u']
    result = [char for char in text if char.lower() in vowels]
    return result