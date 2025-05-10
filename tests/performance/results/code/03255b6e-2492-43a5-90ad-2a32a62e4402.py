def execute():   #Tworzeniem nowej funkcji o nazwie 'execute'. Nie potrzebujem definicji typu zwracanych.
    text = "Python jest wspaniały"  #Zmienna przeznaczona dla środowiska testingu, może być również używana do obliczeniowa (opcjonalnie).
    vowels = ['a', 'e', 'i','o' , 'u']  #Tablica znaków samogłoskich. Możemy dodatkowo użyć dużej litery, gdy chcemy jednolity typowa funckja do wszystkiej mniejszych liter
    result = [char for char in text if char.lower() in vowels] #List comprehension tworzenia listy samogłosek znaków wejściowych, następnie sprawdzamy czy ich wielkość jest na liście moja_litery.
    return result #zwracam swojemu użytkownikowi liczbę samogłosków i te, co sie znajduje w tesce oraz napis "Samoglosek" na koniec.