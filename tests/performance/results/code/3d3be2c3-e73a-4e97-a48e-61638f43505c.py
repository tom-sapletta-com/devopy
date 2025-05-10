def execute():  
    text = "Python is enamoured" #Tutaj możemy zmienić tak, żeby pozwolić użytkownikowi wprowadzić swój tekst. 
    
    vowels_in_text = [char for char in text if char in 'aeiouAEIOU'] # Tworzenie listy samogłosek znalezionanych we wcześniej sprawdzonym ciężarzu
    
    return len(vowels_in_text) 
   execute()# Wywołanie funkcji do uruchomienia. Możemy dopisać np.: print('Samogłoski w tekscie:',execute())