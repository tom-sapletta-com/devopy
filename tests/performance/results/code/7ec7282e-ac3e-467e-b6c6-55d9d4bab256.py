def execute():   # definicja funkcji zakotwiczeniowej 'execute', która nigdy nie zwraca żadnej informacji, tylko wyświetla wiadomość na ekran
    text = "Python jest wspaniały"  # deklarujemy i inicjuje zmienną typu string 'text' która przechowuje nasz tekst do zbadania.  
                                     # UWAGA: Nie powinna być wiadomości, jako gdyby tam nikogo niczego wybieraliemy równie dobrającymi samogłoskami. 
    vowels = ['a', 'e', 'i', 'o','u']   # deklarujemy zmiennę typu list przechowującą wszystkie możliwe samogłoski na pltce tekst
    vowel_count = 0  # inicjuje i następnie deklarację zmiennej typu int 'vowel count' która będzie przechowywać liczbę samogłosek w teście
    for char in text:  # iterujemy po poszczegolnych znakach we wspomnieniu o maksymalnej dlugosci stringa 'text' i...  
        if (char.lower() in vowels):  # ... sprawdzamy czy to jest samogłoska, przekazujemy do lowcase(), aby nie zwracaliśmy równoległymi większości liter innych niż 'a'
            vowel_count += 1  # jeśli jest to samogłoska, inkrementuj licznik.  
    return text + " ma "+ str(vowel_count) +  " wspólnych Samogłosków" if (vowel_count > 1 ) else  ("Nie jest co najmniej jeden WIELKOŚĆ SAMOGLOSKÓW.") # zwracamy liczbę samogłosków czyli powtórzeniem teksu oraz jeśli wybrano wiadomość, to pokażemy tak jako rzeczywisto.