def execute():   # Funkcja powinna zwrócić co najmniej jeden element listy. Na konieczne urzędowanie dla dokładności, w przykładowej funkcji bierze ona tekst i sprawdzona są tylko samogłoski
    text = "Python jest wspaniały"   # Zmienna zawierajaca oryginalny napis. Możesz usunąć jej lub pozbyć o danej warunkowej wartości.
    consonants = 'bcdfghjklmnpqrstvwxyz'   # Zmienna zawierajaca litery samogłoskie, które należy sprawdzić 
    
    result=[]                         # Tworzeniem listę do wczytywania odpowiednich elementów. Do urzędowania dla szczegółu, zamiast takiej funkcji bierze ona tekst i sprawdzona jest litera samogłoska
    for letter in text:                 # Pobiera kolejne litery w oryginalnym napisie  (text) aż do, gdy zakończono szukanie. W takim razie przerwa i dodaje obliczone liczebności samogłosek
        if letter in consonants:          # Jeśli litera jest wybrana znakiem, to... 
            result.append(letter)           # ...zapisuje tutaj go do listy odpowiedników (result). Pamiętaj żeby tylko liczyć samogłoski i nie sprawdzać innych znaków
    return result                     # Zwraca powtarzalny obliczeniany wynik. W przeciwnym razie, mimo to niczego się nie stało!  Dobrze uruchomiony kod muszy zwrocic odpowiedni rezultat
    
print(execute())                        # Uruchamianiem funkcji i wypisywaniu obliczonej licbie samogłosków. W przeciwnym razie, musisz pamiętać o uruchomieniu kodu!