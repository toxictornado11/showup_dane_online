# scraper.py - WERSJA PRODUKCYJNA
import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re
from urllib.parse import urljoin

# --- USTAWIENIA ---
BASE_URL = "https://showup.tv/"
STATS_SELECTOR = "h4"  # Wracamy do pierwotnego selektora, który teraz powinien zadziałać
OUTPUT_FILE = "dane.csv"
# ----------------------------------------------------

def gather_stats():
    """Pobiera statystyki, realizując pełen, trójstopniowy proces logowania."""
    try:
        scraper = cloudscraper.create_scraper() 
        
        # KROK 1: Wejdź na stronę, aby ominąć Cloudflare i pobrać stronę z regulaminem.
        print("Krok 1: Omijanie Cloudflare i pobieranie strony z regulaminem...")
        rules_page_response = scraper.get(BASE_URL, timeout=30)
        rules_page_response.raise_for_status()
        print("Ochrona Cloudflare ominięta.")

        # KROK 2: Wyślij formularz akceptacji, aby ustawić ciasteczko w sesji.
        soup_rules = BeautifulSoup(rules_page_response.text, 'html.parser')
        form = soup_rules.find('form', {'id': 'acceptrules'})
        
        if not form:
            # Jeśli nie ma formularza, to znaczy, że jesteśmy już na stronie głównej.
            print("Nie znaleziono formularza, zakładam, że jesteśmy na stronie głównej.")
            main_page_response = rules_page_response
        else:
            action_url = form.get('action', '')
            post_url = urljoin(BASE_URL, action_url)
            form_data = {'decision': 'true'}
            
            print(f"Krok 2: Wysyłanie formularza akceptacji na adres: {post_url}")
            # Ta operacja głównie ustawia ciasteczko, treść odpowiedzi nie jest istotna.
            post_response = scraper.post(post_url, data=form_data, timeout=30)
            post_response.raise_for_status()
            print("Formularz wysłany, sesja powinna być aktywna.")

            # KROK 3: Wejdź PONOWNIE na stronę główną, aby odczytać dane z aktywnej sesji.
            print("Krok 3: Pobieranie strony głównej z aktywną sesją...")
            main_page_response = scraper.get(BASE_URL, timeout=30)
            main_page_response.raise_for_status()
        
        print("Pobrano finalną wersję strony głównej.")
        return parse_stats_from_page(main_page_response.text)

    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {e}")
        return "BŁĄD KRYTYCZNY", str(e)

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
