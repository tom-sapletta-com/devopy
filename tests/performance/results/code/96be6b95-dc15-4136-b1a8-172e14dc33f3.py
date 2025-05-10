def execute():
    text = 'Python is very funny!'
    
    vowels_in_text = [char for char in text if char.lower() in ['a', 'e', 'i', 'o', 'u']]
      
    return len(vowels_in_text)  # zwraca liczbę samogłosków w tekscie, bez użytkwania list comprehensions.  
                                   
# Wywołanie funkcji:    
print("Liczba samogłosków na tekście 'Python is very funny': ", execute())  # zwraca liczbę wszystkich samogłosków.