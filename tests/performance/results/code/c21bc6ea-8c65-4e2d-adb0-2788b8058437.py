import datetime  # do obsługi obecności biblioteki "datetime" w python3.x, jest ona czasami uwzględniana przez system operacyjny i nie musimy go importować ręcznie
import time     # do obsługi obecności biblioteki "time" w python3.x, jest ona czasami uwzględniana przez system operacyjny i nie musimy go importować ręcznie

def execute():  # definicja funkcji do obsługi zadania wyswietlania aktualnej daty i godziny
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))  # Wyświtl data i czas jako string z informacja o formatach '%A, %B d., %Y : %I:%M %p'
    time.sleep(2)   # Czekamy na dwie sekundy przed uruchomieniem kolejnej funkcji w taki sposób by mogła zobaczyć rachunki czasowe co 2 sekund
    print("Wyswietlanie daty i godziny po pętli")   # Druga instrukcja, jest to inna operacje kończacy powodu zapetlenia czasowego w sekundach
    time.sleep(3)  # Czekamy na trzy sekundy przed uruchomieniem następnej funkcji, by mogła poprawnie zobaczyć różnic czasowych co tydzień
    print("Wyswietlanie daty i godziny po pominięciu")  # Trzecia instrukcja, jest to inna operacje kończacy powodu zapetlenia czasowego w sekundach
    
execute()   # Wywołanie funkcji do obsługi zadania.  Po uruchomieniu program automatycznie pokaże datę i godzinę na konsoli po czterech sekundach