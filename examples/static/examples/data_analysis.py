# Przykład analizy danych
# Prosty skrypt pokazujący podstawowe operacje na danych

import numpy as np
import pandas as pd

# Tworzenie przykładowych danych
print("Tworzenie przykładowych danych...")
data = {
    'Imię': ['Anna', 'Jan', 'Maria', 'Piotr', 'Ewa'],
    'Wiek': [28, 34, 29, 42, 31],
    'Miasto': ['Warszawa', 'Kraków', 'Gdańsk', 'Poznań', 'Wrocław'],
    'Wynagrodzenie': [5600, 6200, 5100, 7800, 5900]
}

# Tworzenie DataFrame
df = pd.DataFrame(data)
print("\nDane:")
print(df)

# Podstawowe statystyki
print("\nPodstawowe statystyki dla wieku:")
print(df['Wiek'].describe())

# Filtrowanie danych
print("\nOsoby powyżej 30 lat:")
print(df[df['Wiek'] > 30])

# Grupowanie danych
print("\nŚrednie wynagrodzenie według miasta:")
print(df.groupby('Miasto')['Wynagrodzenie'].mean())

# Dodawanie nowej kolumny
df['Premia'] = df['Wynagrodzenie'] * 0.1
print("\nDane z premią:")
print(df)

# Obliczanie korelacji
print("\nKorelacja między wiekiem a wynagrodzeniem:")
print(np.corrcoef(df['Wiek'], df['Wynagrodzenie'])[0, 1])
