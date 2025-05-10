# Przykład wizualizacji danych
# Prosty skrypt pokazujący podstawowe wykresy z matplotlib

import numpy as np
import matplotlib.pyplot as plt

# Generowanie danych
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)
y3 = np.exp(-0.2*x) * np.sin(x)

# Tworzenie wykresu
plt.figure(figsize=(10, 6))

# Wykres liniowy
plt.subplot(2, 2, 1)
plt.plot(x, y1, 'b-', label='sin(x)')
plt.plot(x, y2, 'r--', label='cos(x)')
plt.title('Funkcje trygonometryczne')
plt.xlabel('x')
plt.ylabel('y')
plt.grid(True)
plt.legend()

# Wykres punktowy
plt.subplot(2, 2, 2)
plt.scatter(x[::5], y3[::5], c='green', s=50, alpha=0.7, label='exp(-0.2x)*sin(x)')
plt.title('Wykres punktowy')
plt.xlabel('x')
plt.ylabel('y')
plt.grid(True)
plt.legend()

# Histogram
plt.subplot(2, 2, 3)
data = np.random.normal(0, 1, 1000)
plt.hist(data, bins=30, alpha=0.7, color='purple')
plt.title('Histogram')
plt.xlabel('Wartość')
plt.ylabel('Częstość')
plt.grid(True)

# Wykres słupkowy
plt.subplot(2, 2, 4)
categories = ['A', 'B', 'C', 'D', 'E']
values = [23, 45, 56, 78, 32]
plt.bar(categories, values, color='orange')
plt.title('Wykres słupkowy')
plt.xlabel('Kategoria')
plt.ylabel('Wartość')
plt.grid(True)

# Dostosowanie układu
plt.tight_layout()

# Wyświetlenie wykresu
plt.savefig('/tmp/visualization.png')
print("Wykres został zapisany jako /tmp/visualization.png")
print("Uwaga: W środowisku Docker możesz nie zobaczyć wykresu bezpośrednio, ale został on zapisany do pliku.")
