```
def execute(text):
    vowels = "aeiouy"
    result = [char for char in text if char.lower() in vowels]
    return "".join(result)