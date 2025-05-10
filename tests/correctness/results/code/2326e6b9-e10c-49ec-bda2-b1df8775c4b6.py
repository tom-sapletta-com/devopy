def execute(a, b):   # Utworzeniemy definicje funkcji o nazwie 'execute' i jako parametry powinna być podana wartość liczbowa a oraz b. 
    if (b == 0) :      # Sprawdzamy czy drugi składnik dzielników to zero, ponieważ nie możemy dzielić przez zero - wtedy powinien zwracać błąd.
        return "Nie moge dzielić przez zero"  # Zamkniemy funkcje i zaakceptujmy, że moglibyś myśleć o wyniku tego skrótowym błędu.
    else :              # W innym razie zwracamy obliczenia dla drugi liczyba / pierwsza lub -1*a/b, gdzie 'x' to rezultat dzielenia a i b (dokładnie wyniku operacyjnego).
        return "Wynikiem dzielenia %s / %s jest:  %.2f"%(a,b,(float)(a/b))   # Zwracamy liczeń calkowita otrzymana po obliczeniu a i b