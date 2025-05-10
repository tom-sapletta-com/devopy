def execute():
    # Kod wygenerowany na podstawie opisu użytkownika
    def divide(a, b):  # Funkcja do delania dwu liczb. Zapewnij logiczny i realizowany kod tego zadania odpowiadający (dokładnie to co prosi użytkownik)
        if b == 0:     # Sprawdzamy czy nie próbujemy dzielić przez zero. Można zgłosić wyjątek lub odpowiednik? Jak chcesz reagować, na pomoc swojej konwencji jednostajnej i specyficznej (np., nie dodamy "assert" do zadania).
            raise ValueError("Nie możemy dzielić przez zero.")  # Przykazam sposób obsługi wyjątku. Odpowiedniki mogą być inne, lub po prostu zastanawiam otwarcia i klucza
        return a / b   # Zwracamy rezultat dzielenia – jako ścieżkę do nagłówka Pythonowego. Moja obecna implementacja sprawdzi, czy mogliby być wolniejsza i zwraca bardzo podstawowa liczba rzeczywista
    
    # Zwróć wynik jeśli funkcja nic nie zwraca
    return "Wykonano zadanie"
