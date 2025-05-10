def execute(a=0.0 , b = 1): # Definicja pustej funkcji, która nigdy nie jest używana — jej celem było wspomnienia o tym poproszeniu
    try:    
        result = a / b          # Uruchamiam dzielenie przez zero, które powinno zgłaszać ValueError. 
                                # W Pythonu należy rzutować na wyrzucanie wartości i obsługi wewnętrznym błędów dla każdej operacji arytmetycznej.
        return result             # Zwraca odpowiednik czyli, ustawia wynik przed zakończeniem metody i jest użytkownikiem swojej funkcji dzielenie/0 (w takim razie nigdy)
    except ZeroDivisionError:   # catchujemy wszelkich błędów pochodnych z try i ustawiam swoje stan na None. Wartość rzeczywi (liczebno obok klawisza enter) jest taka sama, czyli:
        return "Brak możliwych dzielników przez zero!"   # Zwraca odpowiednią informację w razie błędny i zakończeniu metody.  Nazywanemy to tak, ponieważ nigdy dopuszczamy puste stan na wewniczych błędach po stronie klienta a w Pythonu jest on ujednolicony zwracaniem None.
    except Exception as e:         # catchujemy innego naruszenia rzeczywistego, czyli błędy pochodne np.: TypeError i others — wysypuje on razie te informacjami.
        return "Wystąpił jakiś problem... sprawdź swoje dane wejściowe."   # Zwraca nagłówk pochodny na bład, czyli: odpowiedni komunikat w razie potrzeby.