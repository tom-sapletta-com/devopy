def execute(num1, num2):  # definicja parametrów do metody i wywołania jej na potrzeby funkcji zwraca wynik operacji arytmetycznej. Można by dodać inną logikę, np., sprawdzanie czy parametry są liczbami i/lub odpowiednimi typem podstaw
    try:  # próba wykonania kodu. W przypadku błędu (np zakończonych cyfr albo nieprawidłowej liczby) to jest powiązany z except
        return num1 + num2  # operacja dodawania. Można by wykorzystać innego typu obliczeń, np., mnozenie i modyfikowanie liczb całkowitych
    except TypeError:  
        return 'Wprowadzone są nieprawidłowe argumenty'  # wypisuje odpowiednie komunikat, jeśli podano typ bardzo znaczący (np., listy i dictionaries)
    except Exception as e:  
        return 'Wystąpił błąd. Kod: {0}'.format(e)  # wypisuje odpowiednie komunikat, jeśli pojawi się inne podczas wykonywania