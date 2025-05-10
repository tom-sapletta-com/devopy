def execute(text):
    vowels = 'aeiouAEIOU'  # Znaki, które są we wszystkich języku polskim i angielskim.
    
    count = 0                # Licznik liczby samogłosek. Inicjalizujemy na zeru aby dopasować każdego nowego char'u przez petle poniżej.. 
                             # i nie bylibym wliczać liczyc samoglosek powtarzających sie. Zawsze zaczynamy od togo, co jeszcze dodano do tekstu - inicjalizujemy na zero.. 
    for char in text:         # Petla przeszukiwania całego wejsciowego wsrod znaków.  
        if char in vowels :     # Jesli to jest samogloska, tak liczy do mnie na 1 i dalej.. (+=)   => count = +count + 1; -> Zwraca ilosc wystapien sampledlowych boksow.
            count += 1          # Jesli nie to samogloska, przejdz do kolejnego znaku i powtarza ten swoje procedura.. (+=)  => Zwraca dodatkowa liczyba wystapien sampledlowych boksow.
    return count              # Po skonczeniu petli, mamy tylko jedną linię zwrotu - każdym samogloseku powtórzonego we wskazanym tekście liczy dopasowanego ilosc. 
                                # Wszystko to co już było, aby mieli możliwość zwracać tę samoglosek wersjonalną.. (return count) -> Zapewnia odpowiedni komunikat do użytkownika.