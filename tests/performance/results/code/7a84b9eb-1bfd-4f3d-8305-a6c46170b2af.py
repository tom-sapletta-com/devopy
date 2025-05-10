def execute():
    # Kod wygenerowany na podstawie opisu użytkownika
    def find_vowels(text):  #Funkcja odpowiedzialna za znalezienie wszystkich samoglosek.  
        vowel = 'aeiouAEIOU'                                       
         return [char for char in text if char in vowel]       
    print(find_vowels('Python is very interesting'))  #Przykładowy wywołanie funkcji z argumentem.
    
    # Zwróć wynik jeśli funkcja nic nie zwraca
    return "Wykonano zadanie"
