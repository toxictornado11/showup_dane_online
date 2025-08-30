# scraper.py - WERSJA DIAGNOSTYCZNA v2 (ZAPIS DO PLIKU)
import cloudscraper
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys

BASE_URL = "https://showup.tv/"
OUTPUT_FILENAME = "page_content.html"

def save_page_source():
    """Pobiera stronę i zapisuje jej kod źródłowy do pliku do późniejszej analizy."""
    try:
        scraper = cloudscraper.create_scraper()
        
        print("DIAGNOSTYKA: Krok 1: Omijanie Cloudflare...")
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
            print("DIAGNOSTYKA: Krok 2: Wysyłanie formularza...")
            scraper.post(post_url, data=form_data, timeout=30).raise_for_status()
            
            print("DIAGNOSTYKA: Krok 3: Pobieranie finalnej strony...")
            main_page_response = scraper.get(BASE_URL, timeout=30)
            main_page_response.raise_for_status()
        
        print(f"DIAGNOSTYKA: Zapisywanie kodu strony do pliku {OUTPUT_FILENAME}...")
        with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
            f.write(main_page_response.text)
        
        print("DIAGNOSTYKA: Plik zapisany pomyślnie. Misja zakończona.")

    except Exception as e:
        print(f"DIAGNOSTYKA: Wystąpił krytyczny błąd: {e}")
        sys.exit(1)

if __name__ == "__main__":
    save_page_source()
