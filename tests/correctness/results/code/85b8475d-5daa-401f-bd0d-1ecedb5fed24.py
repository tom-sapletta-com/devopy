def execute(num1=0 , num2 = 0): #deklaracja i inicjalizacja parametrów wewnątrz funkcji, domyślnie przyjmuje wartości 0 dla liczb nieokreślonych
    try: #wywołanie bloku try-except zawierający sposób obsługi błędów/wartykwentruj i wysyła do funkcji jak następuje dzielenie przez 0
        result = num1 / num2 #działanie na liczbach (num_dividend and divisor) oraz zapisujemy rezultat wyniku do variable 'result'
    except ZeroDivisionError:   #wywołaję obsługi błędów dla przypadków, gdy użytkownicy poda 0 jako drugiej liczbie (lub tylko wartość 'num2' i nawet bez definiuje 'dividend')
        return "Błąd: Nie można dzielić przez zero!" # zwraca odpowiedni komunikat błędu, jeśli wystąpi ZeroDivisionError (np. użytkownicy nie podali drugiej liczby)
    except TypeError: 
        return "Błąd: Wprowadzone są różne typy danych - musi być tylko wartości numeryczne!" # obsługa błędu gdy użytkownicy nie podają liczb i operand przy obliczeniu
    except Exception as e: 
        return f"Błąd: {e}"   # wszelkich innych sytuacji będziemy odpowiadać za niepowodujace rzeczywistości, dlatego tylko zawiera to
    return result