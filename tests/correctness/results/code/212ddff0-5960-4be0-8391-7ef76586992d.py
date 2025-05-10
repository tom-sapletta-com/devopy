def execute(a, b):  # Funkcja powinna być nazwana 'execute' i zwraca wynik działania. Zapewnij logiczności a dokladnie to o co prosi uzytkownika (liczebne liczby).
    if isinstance(a, int) and isinstance(b, int):  # Sprawdzamy czy wartosci sa liczbami. Dajemy spoko kodowi na to jesli sie powtarza tak i nie zwracasz błędów
        return a + b  
    else:  # W przeciwnym wypadku możemy podać odpowiedni komunikat lub obsługujemy rzeczy, do czego dopisywanie zamiaru nie jest obecny.
        return "Należy wejść liczebne wartości."  # Następnym razem uwrażamy, że kod ten można dostosować do naszych potrzeb.