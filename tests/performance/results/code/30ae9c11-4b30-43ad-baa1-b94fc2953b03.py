```
def execute(text):
    vowels = "aeiouAEIOU"
    result = [char for char in text if char in vowels]
    return "".join(result)