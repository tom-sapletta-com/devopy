def execute():
    # Kod wygenerowany na podstawie opisu użytkownika
    def divide(a, b):  #funckja do delania czyli dividing function (divide)  
        try:                            # Zaczynamy blok wywołaniowy związanych z obsługi wyjątków.         
            division = a / b             # Utworzenie instancji i utrzymananie czyli dla przeksztalcenia bloku try-except     
        except ZeroDivisionError:       # Oto miejsce, gdzie następuje obsługa wyjątków.         
            division = "Nie można dzielić przez zero"     # Nadanieniemu stosowania odpowiedniego powodum zmian (ZeroDivisionError)     
        except TypeError:                 # Druga część obsługi wyjątków, gdy nie podano argumentów.         
            division = "Należy wprowadzić liczby"     # Nastawiamu stosowaniu odpowiedniego powodum zmian (TypeError)     
        return float(division)             # Zwracamy czytanie na typ float, jako należyliemna miara wyników działania         
      print execute()                     # Wywołuję funkcję zdefiniowaną przed tym blokiem.
    
    # Zwróć wynik jeśli funkcja nic nie zwraca
    return "Wykonano zadanie"
