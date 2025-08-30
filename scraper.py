# scraper.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re

# --- USTAWIENIA ---
URL = "https://showup.tv"
STATS_SELECTOR = "h4" 
OUTPUT_FILE = "dane.csv"
# ----------------------------------------------------

def gather_stats():
    """Pobiera statystyki ze strony i zwraca je jako krotkę (uzytkownicy, transmisje)."""
    try:
        # --- POCZĄTEK ZMIANY ---
        # Dodajemy więcej nagłówków, aby lepiej symulować prawdziwą przeglądarkę
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
        # --- KONIEC ZMIANY ---

        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        stats_element = soup.select_one(STATS_SELECTOR)

        if not stats_element:
            print("Nie znaleziono elementu ze statystykami.")
            return "SELEKTOR BŁĘDNY", "SELEKTOR BŁĘDNY"

        full_text = stats_element.get_text(strip=True)
        numbers = re.findall(r'\d+', full_text)
        
        if len(numbers) >= 2:
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
