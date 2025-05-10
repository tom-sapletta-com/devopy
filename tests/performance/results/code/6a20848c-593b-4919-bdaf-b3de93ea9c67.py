def execute():
    text = 'Python is very interesting'
    
    vowels_in_text = 0
  
    for char in text.lower(): # lower() method to convert all characters into a common case (lowercase) 
        if char == "a" or char == "e" or char == "i" or char == 'o' or char=='u':      
            vowels_in_text += 1  
    
    return vowels_in_text # Returning the count of found samoglosek in text. 
execute()