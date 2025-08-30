# scraper.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re # Import modułu do wyrażeń regularnych

# --- USTAWIENIA ---
URL = "https://showup.tv"
# Selektor dla elementu <h4>, który zawiera obie informacje
STATS_SELECTOR = "h4" 
OUTPUT_FILE = "dane.csv"
# ----------------------------------------------------

def gather_stats():
    """Pobiera statystyki ze strony i zwraca je jako krotkę (uzytkownicy, transmisje)."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Znajdź element h4 na stronie
        stats_element = soup.select_one(STATS_SELECTOR)

        if not stats_element:
            print("Nie znaleziono elementu ze statystykami.")
            return "SELEKTOR BŁĘDNY", "SELEKTOR BŁĘDNY"

        # Wyciągnij cały tekst z elementu, np. "70 transmisji i 3254 oglądających"
        full_text = stats_element.get_text(strip=True)
        
        # Użyj wyrażeń regularnych, aby znaleźć wszystkie liczby w tekście
        numbers = re.findall(r'\d+', full_text)
        
        # Sprawdź, czy znaleziono co najmniej dwie liczby
        if len(numbers) >= 2:
            # Na podstawie formatu "XX transmisji i YYYY oglądających"
            active_streams = numbers[0]
            users_online = numbers[1]
            return users_online, active_streams
        else:
            print(f"Nie udało się wyodrębnić liczb z tekstu: '{full_text}'")
            return "BŁĄD PARSOWANIA", "BŁĄD PARSOWANIA"

    except requests.RequestException as e:
        print(f"Błąd połączenia: {e}")
        return "BŁĄD POŁĄCZENIA", "BŁĄD POŁĄCZENIA"
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {e}")
        return "BŁĄD SKRYPTU", "BŁĄD SKRYPTU"

def save_to_csv(data):
    """Zapisuje dane do pliku CSV."""
    file_exists = os.path.isfile(OUTPUT_FILE)

    with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
        if not file_exists:
            f.write("data_i_godzina,uzytkownicy_online,aktywne_transmisje\n")
        
        f.write(f"{data[0]},{data[1]},{data[2]}\n")

if __name__ == "__main__":
    print("Rozpoczynam zbieranie danych...")
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    users, streams = gather_stats()

    print(f"Czas: {current_time}")
    print(f"Użytkownicy online: {users}")
    print(f"Aktywne transmisje: {streams}")

    save_to_csv((current_time, users, streams))
    print(f"Dane zostały zapisane do pliku {OUTPUT_FILE}")