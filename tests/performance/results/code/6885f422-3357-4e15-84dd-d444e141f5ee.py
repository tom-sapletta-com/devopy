def execute():
    text = "Python is wonderful"
    
    vowels_in_text = 0
  
    for char in text.lower(): # Sprawdzamy znaki po przecinku i nie zaokręceniu wielkości liter (np: 'p' oraz 'P') 
        if char == "a" or char == "e" or char == "i" or char == "o" or char== "u": # Sprawdzamy czy jest to samogłoska  
            vowels_in_text += 1    # Jeśli tak, zwiększmy liczebność.  (nazywane są też 'count' w nawiasie)     
            
     return(vowels_in_text)   # Zwróćlicze ostateczny rozmiar listy samogłosek po zakończeniu pętli.  (nazywane są też 'return' w nawiasie )
     
print(execute())    # Wywołujemy naszego funkcji i na koniec otrzymamy liczebność samogłosek.  (nazywane są też 'main' w nawiasie )