def execute():
    import datetime  # wymagane przez moduł ctime do odczytu dnia/godziny zegara systemowego, który bazujemy na strefie czasowej. Następnie formatujemy tę datę i godzinę przedstawiamy je jako string
    now = datetime.datetime.now()  # pobieramy aktualną data/godzinę zegara systemowego, która bazuje na strefie czasowej (czyli miejsce użytkownika)
    print(now.strftime("%Y-%m-%d %H:%M:%S"))  # przekształcam dnię, godzinę i czas do formatu rozszerzonego daty/godziny