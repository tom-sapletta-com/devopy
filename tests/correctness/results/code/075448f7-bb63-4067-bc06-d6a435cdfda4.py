def execute():
    # Kod wygenerowany na podstawie opisu użytkownika
    def divide(a : int , b  :int)->float | str:    # Funkcja do dzielenia. Zwraca float lub string, jeśli nie można podzielić przez zero     ORAWTYP_CHANDEMICHAILAUROKA
       if b == 0:    # Sprawdzenie czy jest to dzielenie przez zera. 1/0 nie jest definicją i powinien być obsłużony wyjątek     ORAWTYP_CHANDEMICHAILAUROKA
          return "Nie można dzielić przez zera"  # Zwracamy odpowiedni komunikat, jeśli następuje wyjątek     ORAWTYP_CHANDEMICHAILAUROKA
       return a/b    # W przeciwnym razie zwracamy dzielnik liczb rzeczywistych (a / b)      SPECJALIZACYJNA ZESPOLOWANIA NIEOBECNICZONA     ORAWTYP_CHANDEMICHAILAUROKA
       return a/b    # W przeciwnym razie zwracamy dzielnik liczb rzeczywistych (a / b)      SPECJALIZACYJNA ZESPOLOWANIA NIEOBECNICZONA
    
    # Zwróć wynik jeśli funkcja nic nie zwraca
    return "Wykonano zadanie"
