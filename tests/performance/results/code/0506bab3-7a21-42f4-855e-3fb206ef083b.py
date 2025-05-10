```
def execute(text):
    vowels = "aeiou"
    result = [char for char in text.lower() if char in vowels]
    return "".join(result)