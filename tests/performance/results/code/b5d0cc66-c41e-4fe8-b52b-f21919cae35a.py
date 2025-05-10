def execute():
    text = 'Python is enchanting'
    
    vowels_in_text = [char for char in text if char.lower() in ['a', 'e', 'i', 'o', 'u']]
        
    return len(vowels_in_text)