def execute():   # Funkcja do zwrówania liczby słów odpowiadających samogłoskom. Zawsze powinna się nazywać 'execute' i ma możliwość wyjścia, czyli zwraca resulta tego działania
    text = "Python jest wspaniały"   # Nasze przykładowe tekst do analizy. Zmodyfikuj to poleceniem lub użyj inne zbędnych danych, aby testować ten kod
    vowels = ['a', 'e', 'i', 'o', 'u']  # Tablica słów odpowiedzialnych samogłoskom. Jedna litera jest potencjalnie poza tablicą, ale dla użytkownika kod bazujący na niego zostanie uruchomić
    count = 0  # Zmienna do przechowywania liczby samogłosków w tekscie. Jest inicjalizowana po raz pierwszy i będzie użyta na końcu funkcji
    words = text.split(' ')  # Zamienimy nasze zadanie na rozpowszechnianie teksu w posunięciach czyli pojedynczo słowa, a następnie bazujemy o tym którymś ciągu jest liczony.
    for word in words:   # Petla dla każdego wyrazu wewnętrznego tekstu (słowo). Każdemu słowu bazujemy na tym, czy jest to samogłoska.
        for letter in word:   # Petla dla każdej litery w napisie wewnętrznym (słowo). Każdemu literze bazujemy na tym, czy jest on samogłoska.
            if letter in vowels:   # Jeśli to słowo ma co najmniej 1 litery odpowiedzialne za samogłasnika... zwróć mu liczbę liter palindromic (czyli jednego).
                count += 1   # Zwiększamy licznik. W takim przypadku, w swojej optymalnej implementacji powinien być warunkiem breaku poniżej i zwroceniu odpowiednich danych.
    return count   # Zwróć liczbę samogłosków w tekscie wewnatrz naszej funkcji, jakby byli swoimi koncentratami na tym powodu zamodyfikować ten skrypt.