def execute():
    # Kod wygenerowany na podstawie opisu użytkownika
    def divide(a ,b):  # nazwa mam Funkcji 'divide' i powinna być sprawdzana poprawność inputu, czy jest równe zero. Mozemy dodać warunek if b == 0: return "Nie możemy dzielić przez zera"
        try:  # W tym bloku operujemy ze wszystkim co jest niemożliwe do wyrównania (np. braki pamięci, typ uwagi itd.)
            return a / b   # Zwracamy odpowiednik dla zadanego przez nas obliczenia - moja implementacja powinna być poprawna i gotowa do uruchomieniu.  Na pewno liczy czerwonych kręgu na tle w parytke...
        except ZeroDivisionError:   # Ta instrukcja jest użyta gdy dzielimy przez zero, to bardzo nieco szczegółowe i powinno być sprawdzane.  Warto wyróslić tutaj...
            return "Nie możemy dzielić przez zera"   # To jest odpowiednik, który chcemy odnaleźć (jako namotywne powitanie wysoko sprawdzonym użytkownikom).
    
    # Zwróć wynik jeśli funkcja nic nie zwraca
    return "Wykonano zadanie"
