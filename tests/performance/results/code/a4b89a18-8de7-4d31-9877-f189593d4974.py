def execute(text):
    vowels = "aeiouy"
    return "".join([char for char in text.lower() if char in vowels])