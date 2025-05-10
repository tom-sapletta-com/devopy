# Przykład Hello World
# Prosty skrypt pokazujący podstawowe operacje w Pythonie

print("Hello, World!")

# Zmienne i typy danych
name = "Devopy"
age = 1
is_awesome = True

print(f"Nazwa: {name}, Wiek: {age}, Czy jest super? {is_awesome}")

# Prosta pętla
print("\nLiczenie do 5:")
for i in range(1, 6):
    print(f"Liczba: {i}")

# Funkcja
def greet(person):
    return f"Witaj, {person}!"

# Wywołanie funkcji
message = greet("Programisto")
print(f"\n{message}")
