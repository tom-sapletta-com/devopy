import datetime   # importowanie modułu do obsługi dat działających w python, zapewnieniu nam możliwości uaktualniania data i godzin. Należy pamiętać o tym aspektach na podstawie swojego stosu kodowania
from datetime import timedelta  # do obsługi obliczeń czasowych w python, zapewnieniem nam možliwości dodatkowej logiki aplikacji o różnych terminach.
  
def execute():     # definiowanie funkcji i jego parametrze  - 'execute' zostaje wywolana przy kazdej uruchomieniu programu, natomiast dane wejsciowe są obslugiwanem do osiagnienia maksymalnych rozmiarów
    current_date = datetime.datetime.now()  # wyświetlanie aktualnej daty i godziny, data jest automatcznie uaktualniana przez moduł 'timedelta' do momentu następnego dnia
    print("Aktualna data: ", current_date.strftime("%d-%m-%Y"))  # formatowanie date i godzin w formacie strf (string formatted) - sformatowywanie na podstawie zdefiniowanych warunków
    print("Aktualna godzina: ", current_date.strftime("%H:%M:%S"))   # formatuje datę i czas w formacie strf - sformatowywanie na podstawie zdefiniowanych warunków
    
execute()  # uruchamianie funkcji 'execut' sprawdza, że dane wejściowe będziemo przekazywać do wywołania modułami odpowiednimi na podstawie szerokości stosu kodów