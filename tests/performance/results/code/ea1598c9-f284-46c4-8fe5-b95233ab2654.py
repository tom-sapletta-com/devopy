def execute():
    text = 'Python is engrossing'
    
    vowels_in_text = 0   # Zmienna do zamieszania liczebności samoglosek w tekście. 
                         # Poza to, że ta funkcja nigdy nie będzie sprawdzić czy jest on poprawna dobra reprezentacje lub danych wejściowych zatwierdzonego.
    vowels = ['a', 'e', 'i', 'o', 'u']  # Tablica samoglosek prawidłowych jako char w Pythonie, są to tylko litery a i u (np: execute()).
    
    for letter in text.lower():   # Zamieszanie poziomu na małe znaki ASCII aby nie sprawdzać czy jest on poprawna dobra reprezentacja lub danych wejściowego
        if letter in vowels:       # Sprawdzamy, czy literka byłaby samogloską. W załączniku to szukanie w każdej liczbie znaków we fragmencie text dla tej samej litery
            vowels_in_text += 1    # Jeśli jest on poprawnym samoglossiem, teraz mamy do pewności obliczyć liczebność wszystkich liter 'a', zwracających błąd.
    
    return vowels_in_text   # Wynik dla tej samej litery i nie sprawdzania czy jest on poprawnym samoglossiem, możemy odpytać użytkownika o współrzędnąc swoje zadanie.