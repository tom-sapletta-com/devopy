def execute():
    # Kod wygenerowany na podstawie opisu użytkownika
    def divide(a, b):  # deklaracja i inicjalizacja funkcji o nazwie 'divide' wraz ze sprawdzeniem czy parametry są liczbami (int/float) oraz jeśli jest to równoległe.
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):  # sprawdzanie czy parametry są liczbami
            raise ValueError("Wartości argumentów muszą być typu int lub float.")   # wyjątek odpowiedzialny za błędne dane wejściowe – zabezpieczenie przed naruszeniem programu
        if a == 0 and b != 0:     # sprawdzanie czy jedna z liczb to wartość zero, inaczej oblicza się dzielenie. (wymaga odpowiedzi na pytanie)
            return "Brak rozwiązania"     # Zwraca komunikat informujący iż nie można dzielić przez zero   – tylko wtedy gdy jedna z liczb to zero
        elif a == 0 and b==0:      # sprawdzanie czy oba parametry są równoległe (dobieramy kwestie logiczne) – nastawienia odpowiedzi na pytanie.   Python zwraca 'None' jeśli wszystko ok, a dla b=0 jest pusta string
            return None     # Zwracanie komunikatu informującego iż niespodziane rozwiązywanie – tylko gdy oba parametry są równoległe. (wymaga odpowiedzi na pytanie)
        else:          # wszystkie innne przypadki - zwraca dzielenie liczb a/ b, czyli obliczenia i-tego rozwiązania. (wymaga odpowiedzi na pytanie)
            return  float(a / b )     # Zabezpieczone przed naruszeniem danych wejściowych, którymi jest wprowadzanie systemu. (wyjaśnienia poufny)
    
    # Zwróć wynik jeśli funkcja nic nie zwraca
    return "Wykonano zadanie"
