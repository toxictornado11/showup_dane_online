# scraper.py - WERSJA OSTATECZNA (PRODUKCJA)
import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re
from urllib.parse import urljoin

BASE_URL = "https://showup.tv/"
OUTPUT_FILE = "dane.csv"
# Wyrażenie regularne szukające liczb obok kluczowych słów
STREAMS_REGEX = r'(\d+)\s*transmisji'
USERS_REGEX = r'(\d+)\s*oglądających'

def gather_stats():
    """Pobiera statystyki, realizując pełen proces i szukając danych za pomocą regex."""
    try:
        scraper = cloudscraper.create_scraper() 
        
        print("Krok 1: Omijanie Cloudflare...")
        rules_page_response = scraper.get(BASE_URL, timeout=30)
        rules_page_response.raise_for_status()

        soup_rules = BeautifulSoup(rules_page_response.text, 'html.parser')
        form = soup_rules.find('form', {'id': 'acceptrules'})
        
        if not form:
            main_page_response = rules_page_response
        else:
            action_url = form.get('action', '')
            post_url = urljoin(BASE_URL, action_url)
            form_data = {'decision': 'true'}
            print("Krok 2: Wysyłanie formularza akceptacji...")
            scraper.post(post_url, data=form_data, timeout=30).raise_for_status()
            
            print("Krok 3: Pobieranie finalnej strony głównej...")
            main_page_response = scraper.get(BASE_URL, timeout=30)
            main_page_response.raise_for_status()
        
        print("Pobrano stronę, rozpoczynam szukanie danych...")
        return parse_stats_from_text(main_page_response.text)

    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {e}")
        return "BŁĄD KRYTYCZNY", "BŁĄD KRYTYCZNY"

def parse_stats_from_text(html_content):
    """Wyciąga dane z całego tekstu strony za pomocą wyrażeń regularnych."""
    soup = BeautifulSoup(html_content, 'html.parser')
    page_text = soup.get_text(" ", strip=True) # Pobierz cały tekst ze strony

    streams_match = re.search(STREAMS_REGEX, page_text)
    users_match = re.search(USERS_REGEX, page_text)
    
    if streams_match and users_match:
        active_streams = streams_match.group(1)
        users_online = users_match.group(1)
        print(f"Sukces! Znaleziono dane: {users_online} użytkowników, {active_streams} transmisji.")
        return users_online, active_streams
    else:
        print("Nie znaleziono wzorców statystyk w tekście strony.")
        return "WZORZEC NIEZGODNY", "WZORZEC NIEZGODNY"

def save_to_csv(data):
    file_exists = os.path.isfile(OUTPUT_FILE)
    with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
        if not file_exists:
            f.write("data_i_godzina,uzytkownicy_online,aktywne_transmisje\n")
        f.write(f"{data[0]},{data[1]},{data[2]}\n")

if __name__ == "__main__":
    print("Rozpoczynam zbieranie danych...")
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    users, streams = gather_stats()
    save_to_csv((current_time, users, streams))
    print(f"Dane zostały zapisane do pliku {OUTPUT_FILE}")
