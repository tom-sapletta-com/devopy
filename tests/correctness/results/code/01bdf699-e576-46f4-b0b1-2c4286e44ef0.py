def execute(a=0.0, b=1.0):  # deklaracja funkcji o wartościach domyśnych a = 0 i b = nieokreślony (będzie dzielić przez siebie)
    if isinstance(a, int):  # sprawdzenie czy pierwsza licba jest liczbą całkowitą. Jeśli tak to uwagi zostaną wypisane na temat dzielenia przez zero
        print("Należy podać różne licby, a nie używać 0 jako pierwszych.")
    if isinstance(b, int):   # sprawdzenie czy druga licba ma być całkowita. Jeśli tak to wypiszemu ostrzeżenia na temat dzielenia przez zero i zwróci null
        print("Należy podać różne licby, a nie używać 0 jako drugich.")   # tak wypisuje ostrzeżenie na temat dzielenia przez zero i zwraca null
    return None if b==1.0 else (a/b)  # logiczny kod, po napisaniu prawidłowo funkcja jest gotowa do uruchomienia oraz czytelników - ostrzeżenie przed dzieleniem przez zero i zwracające wyniki