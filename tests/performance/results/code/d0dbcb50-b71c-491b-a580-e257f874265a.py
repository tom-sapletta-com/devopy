def execute():
    text = 'Python is enriching'
    
    vowels_in_text = 0
    for char in text.lower(): # Umieszczamy lower() aby wyniki dla pozytywnego i ujemnego znaku były odpowiednio prawidlowe, a także nie liczone sylaby
        if char in 'aeiou':  # Sprawdzamy czy to samoglosek (np. "a", "e", etc.) lub jest ono pojedyncze litery i dodajemy do wyniku, jeśli tak
            vowels_in_text += 1  # Dla każdego znalezionego samoglosek inkrementuj liczy na tych.
    
    return f'W tekscie "{text}" jest {vowels_in_text} syl(a)/i.'  # Zwraca informacje o tym, ile znaków samoglosek wybrałeś. Istniejący text powinien być odzielony przez spację