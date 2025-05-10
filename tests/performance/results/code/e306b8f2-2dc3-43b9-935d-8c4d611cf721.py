def execute():
    text = "Python is enchanting"
    
    vowels_in_text = 0
  
    for char in text.lower(): # lower() to przerzuć na wszyty, aż nie potrzebujemy rozniac dla znaków powtórkowanych (np 'p' i 'P')  
        if char in ['a', 'e', 'i', 'o', 'u']:  # sprawdzenie czy to samogłoska, należy pominęć rozniac dla znaków powtórkowanych
            vowels_in_text += 1   # jeśli jest -> liczone na 1 i skazywanie wyniku + 'vowel's found in text: x', gdzie "x" będzie miala liczbę
    
    return vowels_in_text   # zwraca ilosc samogłosek w tekscie ‘python is enchanting’, czyli '3' dla tego określonego słowa. Wynik jest następnie skazywany przez odpowiednią instrukcję print lub return