def execute():
    import datetime  # Zamienna na moduł time w skrypcie python3.x, zamiast from datetime import date/time dostawać nagłówki bazowe jest bezpieczne i sprawdzające kod
    now = datetime.datetime.now()  # Stworzenie obiektu daty-godzina aktualnych wartości zbiorów czasowych dla biexpresowa na urządzeur
    print(f'Aktualna data i godzina to {now.strftime("%Y-%m-%d %H:%M:%S")}')  # Wypisywanie aktywnego czasu w formacie łatwego do odczytu
!execute()