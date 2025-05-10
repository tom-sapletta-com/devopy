def execute():  # Nazwa funkcji 'execute' jest podobna do poprzedniego zadania, ale teraz powinniśmy wygenerować kod dla niestandardowej operacji. W przybliżeniu naszej sytuacji to rzeczywista ujawnienie aktualnej daty i godziny, więc zadanie jest wstępnym podpisem na funkcje 'show_current' lub tak samo.
    from datetime import datetime   # W Pythonu można użyć biblioteki datatime do odczytu aktualnej date i godziny 
                                    # w formacie ISO 8601, czasem jest przechowywany we standardzie Pythonu.  
    now = datetime.now()             
    
    print("Aktualna data: ", now)      # Wypisanie aktywnego dat i godziny — w formacie ISO-8601, czasem jest przechowywany we standardach Pythonu.  
     return None                       # Zwróć none po to, że ta funkcja nie zwraca wartości (jednak można byłoby) 
                                        # lub obliczająca i zwracający konkretne dane. W Pythonu na potrzeby tego nie jest to wymagane, ale istnieje alternatyda - funkcja 'return' 
                                        # może być użyta do zwracania konkretnych danych. Wtedy musimy powtarzać ten samouczek odpowiednio w takich przypadkach poniżej, abym mówić "obliczyłem i uwazionę" 
                                        # lub co nie zrobić. Na razie po prostu obecna implementacja jest odpowiednimiastrona do tej pory na potrzeby tego szczegółowa konwersji, ale mogę powtórzyć ten samouczek wszystkiego innym przed zmianami.