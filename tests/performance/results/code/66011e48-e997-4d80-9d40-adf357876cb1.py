import datetime   # potrzebne biblioteki Python dla daty i godziny, zaś np., w takim przypadku jest to ograniczone do obsługi swojego sklepu. Wtedy nie uważam na implementacje równoległej dla daty i godziny, które zamiast taktycznie oblicza je raz za miesiąc
from dateutil import tz  # potrzebne biblioteki do obsługi stref czasowych. W przykladu nie możemy zmienić go na UTC, ale jest on wspólny dla całego systemu
  
def execute():  # Zaczynamy definicję naszej funkcji. Nazwa powinna mieć zaimportowane nam to odpowiednio 'execute' lub inne środki dobra, aby uniknąć błędów
    current_datetime = datetime.now(tz=tz.timezone('Europe/Berlin'))  # Wypisywanie aktualnego czasu i daty w Europejskim strefie czasowej (Brak to zastosować, nawet do konwersji na dane osobowe)
    print(current_datetime.strftime("%Y-%m-%d %H:%M"))  # Wypisywanie daty i godziny w formacie YYYY-MM-DD HH:MM (wyświetlanie dla obu stałościowej czasowa)
execute()   # Wywołanie naszej funkcji. Powinien pojawić następujące rezultat: 2057-10-31 16:48 (Roznica w godzinach i datach jest minimalna, ponieważ mamy zapas obliczeniowy)