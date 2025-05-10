import datetime  # importowanie modułu do wyswietlania dziennikowa/daty czasowej.
                  
def execute():   # definicja funkcji, ktora powinna zwrócić aktualną datę i godzinę na nowo wypisanie 1 linii danych tekstowych "Current date and time: ..."
    current_datetime = datetime.datetime.now()   # użycie modułu do obliczenia aktualnej daty i godziny zgodnie ze standardem ISO 8601 (np.: '2023-04-07T15:39:14.688Z').
    print("Current date and time : ", end="")     # wypisywanie aktualnej daty i godziny na nowo dopasowanego formatu tekstowego z użyciem funkcji 'end' do pominięcia linii.
    print(current_datetime)   # wypisywanie aktualnej daty i godziny na nowa dopasowanego formatu tekstowego z użyciem funkcji 'print' do pominięcia linii.
      
execute()   # wypisywanie aktualnej daty i godziny na nowa dopasowanego formatu tekstowego z użyciem funkcji 'print' do pominięcia linii.