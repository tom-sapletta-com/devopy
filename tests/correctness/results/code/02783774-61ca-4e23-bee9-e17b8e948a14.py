def execute():
    # Kod wygenerowany na podstawie opisu użytkownika
    def divide(a : float , b :float) -> str:  # Definicja funkcji do dzielenia. Parametry to liczby calkowite i sa opisane jako typy nazywane na poziomie Pythonu np int, double
        try:                                           # Blok próbny wypłynęcia programu z powodu błędów wewnętrznych lub danym środowiskiem uruchomionym (np. ZeroDivisionError, ValueError)
            result = a / b                               # Poniżej wpisano swój kod Python do rozwiązywania zadania — cialo nie jest dostosowane powinno być tylko ten blok, aby uruchomić pomyślnie
        except ZeroDivisionError:                       # Wysłanie wyjątku gdy próbujesz podzielić przez zero — dlatego tego typu blok nazywamy "except" i jest opcjonalnym
            return 'Nie można dzielić przez zero'   # Powinien zwrócić informacje o błędzie wykonawczego — najlepiej tylko powinno być ten blok, aby uruchomić pomyślnie
        except TypeError:                               # Powinien zwrócić informacje o błędzie typowym pozbawionego wartosci calkowitej — dlatego ten blok jest opcjonalnym i nazywany "except"
            return 'Niepoprawne wprowadzenie liczbowych argumentów'    # Powinien zwrócić informacje o błędzie typowym — powinniśmy uruchomić ten blok, aby uruchomić pomyślnie
                                                                       # Pamiętaj i wszystko jest ujawnione na stronie https://docs.python.org/3/tutorial/errors.html#catching-and-reporting-exceptions — powinien być ten blok, aby uruchomić pomyślnie
        return result                                   # Powinien zwrócić wynik działania (na razie to jest tylko "result") i nazywać go 'execute' — powinniśmy ujawnić ten blok, aby uruchomić pomyślnie
    
    # Zwróć wynik jeśli funkcja nic nie zwraca
    return "Wykonano zadanie"
