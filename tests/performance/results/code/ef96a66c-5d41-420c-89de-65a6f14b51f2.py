def execute():  # Definiowanie funkcji 'execute' o nazwie. Nie dajmy zwracanej wartości ani braku potrzebnego importu modułu datatime, a są jednak obliczane automatycznie na podstawowej platformie Python 3.
    from datetime import datetime   # Importujemy bibliotekę do obsługi dat i godzinna w pythonu (tz) oraz inne potrzebne moduły, jeśli nie chcesz obliczać żadnych danych czasowych.
    
    current_date = datetime.now()  # Zapewniamy bibliotekę do pomagania z datami i godzinami w Pythonu (tz) oraz innymi potrzebnymi modułami, jeśli nie chcesz obliczać żadnych danych czasowych.
    
    print("Aktualna data i godzina: ", current_date)  # Wyświetlam aktualną datę oraz godzinę zgodnie ze standardem ISO 8601 (RFC3339). Jeśli potrzebujesz danych w innym formatowaniu, można rozszerzyć taktowo to co następuje.