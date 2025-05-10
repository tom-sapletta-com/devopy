def execute():
    # Kod wygenerowany na podstawie opisu użytkownika
    def divide(a=0.0, b=0.0): # Zapewniamy wartości domyślne do a i b jako 0 (bezu wpłynników na przykladze) by nie powstrzymac dostępu
        if isinstance(a, int): # Sprawdzamy czy 'a' to liczba całkowita. Wtedy sprawdzone musi zawsze mniejsza wartość (b), bo a i b są równe
            return "Dzielenie przez zero" if isinstance(a, float) and abs(abs(a)-abs(b)) < 0.1 else divmod(int(a/float(b)), 2)[1] # Zamieniamy 'divide' na '/', następnie podajemy dzielnik i numerator (dla liczebności)
        elif isinstance(b, int):# Sprawdzamy czy b to liczba całkowita. Wtedy sprawdzone musi mniejsza wartość a dobrany zamiast dodatniających (a), bo a i b są równe
            return "Dzielenie przez zero" if isinstance(b, float) and abs((abs(float(a)-abs(b))-1)/2 ) < 0.1 else divmod(int(b/float(a)), 2)[1] # Zamieniamy 'divide' na '/', następnie podajemy dzielnik i numerator (dla liczebności)
        return "Duże wartość" if abs(abs(a)-abs(b)) > 0.1 else divmod((int(a/float(b)))[1] # Zamieniamy 'divide' na '/', następnie podajemy dzielnik i numerator (dla liczebności)
    
    # Zwróć wynik jeśli funkcja nic nie zwraca
    return "Wykonano zadanie"
