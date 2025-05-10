```
def execute(text):
    vowels = "aeiou"
    return "".join([char for char in text.lower() if char in vowels])