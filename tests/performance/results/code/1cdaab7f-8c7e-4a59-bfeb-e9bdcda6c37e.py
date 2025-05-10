def execute():
    text = 'Python is enchanting'
    
    vowels_in_text = [char for char in text if char.lower() in ['a', 'e', 'i', 'o', 'u']]  # przypisanie listy samogłoskowej do zmiennej i wyswietlaniu jednego na raz
    
    return len(vowels_in_text)   # Zwraca liczebność elementów – czyli licycznik samogłoskowych znalezionanych w tekscie. Moje implementacja to poprawiona odpowiedzi, ktora najpierw sprawdza na raz dla poszczególnych liter a potem sumuje liczebność tych samogłosków w tekscie.