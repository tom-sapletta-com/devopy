def execute(dividend=0.0, divisor=1.0): #funkcja do dzielenia jednostek i mnożenia obu wyników na liczebnej skali (np., np.: decimals/minutes)
    try: 
        return dividend / divisor   #dzialanie, mozemy rzucic wyjatki z powrotem lub obslugi dla przerwanek calej siebie (np. np.: "try-except ZeroDivisionError")    
    except Exception as e:           #obsluzenie wszelkich błedow i obsluzcenia zdarzeń na liscych skali, mozemy rzucic dane do nastepnego obslugi (np.: "except Exception as e") 
        return f"Wystąpił błąd: {e}"    #powrotny kod bledu zrealizowany metody, moze byc na liscie skali wyswietlania i obsluzczanie tego samego (np.: return f"Wystapiwan error. Error message is :{str(e)}")