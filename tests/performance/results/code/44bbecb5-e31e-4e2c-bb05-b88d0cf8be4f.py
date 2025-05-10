```
def execute(text):
    vowels = "aeiou"
    result = [char for char in text if char.lower() in vowels]
    return "".join(result)