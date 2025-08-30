# scraper.py
import cloudscraper # Zamiast requests, importujemy cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re
from urllib.parse import urljoin # Będziemy tego używać do budowania poprawnych adresów URL

# --- USTAWIENIA ---
BASE_URL = "https://showup.tv/"
STATS_SELECTOR = "h4"
OUTPUT_FILE = "dane.csv"
# ----------------------------------------------------

def gather_stats():
    """Pobiera statystyki, używając cloudscraper do ominięcia ochrony Cloudflare."""
    try:
        # --- KLUCZOWA ZMIANA: Tworzymy scraper zdolny do ominięcia Cloudflare ---
        # Ta linijka zastępuje całą naszą poprzednią logikę z sesją i nagłówkami.
        scraper = cloudscraper.create_scraper() 
        
        # --- KROK 1: Pierwsze wejście na stronę ---
        # Scraper automatycznie rozwiąże wyzwanie JS i zdobędzie ciasteczko cf_clearance.
        # W odpowiedzi dostaniemy stronę z bramką regulaminu.
        print("Krok 1: Inicjowanie sesji i omijanie Cloudflare...")
        response_rules_page = scraper.get(BASE_URL, timeout=25)
        response_rules_page.raise_for_status()
        print("Ochrona Cloudflare ominięta.")

        # --- KROK 2: Znajdź formularz i wyślij go ---
        # Musimy odczytać dynamiczny adres URL z atrybutu 'action' formularza.
        soup_rules = BeautifulSoup(response_rules_page.text, 'html.parser')
        form = soup_rules.find('form', {'id': 'acceptrules'})
        
        if not form:
            print("Nie znaleziono formularza akceptacji na stronie.")
            # Jeśli nie ma formularza, to może od razu jesteśmy na stronie głównej
            # Spróbujmy od razu odczytać statystyki
            return parse_stats_from_page(response_rules_page.text)

        action_url = form.get('action')
        # Używamy urljoin, aby poprawnie połączyć adres bazowy z adresem z 'action'
        post_url = urljoin(BASE_URL, action_url)
        
        form_data = {'decision': 'true'}
        
        print(f"Krok 2: Wysyłanie formularza na adres: {post_url}")
        response_after_post = scraper.post(post_url, data=form_data, timeout=25)
        response_after_post.raise_for_status()
        print("Formularz wysłany, powinniśmy być na stronie głównej.")

        # --- KROK 3: Odczytaj dane ze strony głównej ---
        return parse_stats_from_page(response_after_post.text)

    except requests.exceptions.RequestException as e:
        print(f"Błąd połączenia (prawdopodobnie Cloudflare): {e}")
        return "BŁĄD POŁĄCZENIA", "BŁĄD POŁĄCZENIA"
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {e}")
        return "BŁĄD SKRYPTU", "BŁĄD SKRYPTU"

def parse_stats_from_page(html_content):
    """Pomocnicza funkcja do wyciągania danych z kodu HTML strony."""
    soup = BeautifulSoup(html_content, 'html.parser')
    stats_element = soup.select_one(STATS_SELECTOR)

    if not stats_element:
        print("Nie znaleziono elementu ze statystykami.")
        return "SELEKTOR BŁĘDNY", "SELEKTOR BŁĘDNY"

    full_text = stats_element.get_text(strip=True)
    numbers = re.findall(r'\d+', full_text)
    
    if len(numbers) >= 2:
        active_streams = numbers[0]
        users_online = numbers[1]
        print(f"Znaleziono dane: {users_online} użytkowników, {active_streams} transmisji.")
        return users_online, active_streams
    else:
        print(f"Nie udało się wyodrębnić liczb z tekstu: '{full_text}'")
        return "BŁĄD PARSOWANIA", "BŁĄD PARSOWANIA"

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
    save_to_csv((current_time, users, streams))
    print(f"Dane zostały zapisane do pliku {OUTPUT_FILE}")
