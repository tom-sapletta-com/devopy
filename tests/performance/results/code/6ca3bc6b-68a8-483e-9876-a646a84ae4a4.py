import datetime  # Utworzenie modułu do obsługi dat d/b timestampów w języku python.
def execute():   # Wtyczamy nazwę funkcji 'execute' i odpowiednik zwraca obecną data oraz godzinę, która będzie ustawiona na aktualnej datie.
    current_date = datetime.datetime.now()   # Utworzeniemy wystąpienie typu 'datetim' zbierając obecną data i godzinę za pomocą moduly pythonowego
    print(current_date)  # Wypisywaniu aktualnej daty oraz godziny.
execute()   # Wywołujemy funkcje 'exec' do wyswietlania obecnego czasu zbieranego przez modul datetime