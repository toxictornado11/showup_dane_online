# scraper.py - WERSJA DIAGNOSTYCZNA
import cloudscraper
import sys

BASE_URL = "https://showup.tv/"

def run_diagnostics():
    """Pobiera stronę i drukuje jej kod źródłowy do logów."""
    try:
        scraper = cloudscraper.create_scraper() 
        
        # Krok 1: Ominięcie Cloudflare
        print("DIAGNOSTYKA: Krok 1: Inicjowanie sesji i omijanie Cloudflare...")
        response_rules_page = scraper.get(BASE_URL, timeout=30)
        response_rules_page.raise_for_status()
        print("DIAGNOSTYKA: Ochrona Cloudflare ominięta.")

        # Krok 2: Wysłanie formularza
        # Używamy prostej logiki z poprzedniej wersji, aby przejść przez bramkę
        from bs4 import BeautifulSoup
        from urllib.parse import urljoin
        
        soup_rules = BeautifulSoup(response_rules_page.text, 'html.parser')
        form = soup_rules.find('form', {'id': 'acceptrules'})
        
        if form:
            action_url = form.get('action')
            post_url = urljoin(BASE_URL, action_url)
            form_data = {'decision': 'true'}
            
            print(f"DIAGNOSTYKA: Krok 2: Wysyłanie formularza na adres: {post_url}")
            final_page_response = scraper.post(post_url, data=form_data, timeout=30)
            final_page_response.raise_for_status()
            print("DIAGNOSTYKA: Formularz wysłany.")
        else:
            # Jeśli nie ma formularza, to pierwsza odpowiedź jest stroną docelową
            final_page_response = response_rules_page
            print("DIAGNOSTYKA: Krok 2: Nie znaleziono formularza, zakładam, że jesteśmy na stronie głównej.")

        # --- NAJWAŻNIEJSZA CZĘŚĆ ---
        # Drukujemy cały kod HTML strony, którą otrzymaliśmy
        print("\n\n--- POCZĄTEK KODU HTML ---")
        print(final_page_response.text)
        print("--- KONIEC KODU HTML ---\n\n")
        
        # Celowo powodujemy błąd, aby zatrzymać workflow i nie zapisywać nic do pliku.
        # To ułatwi nam analizę logów.
        print("DIAGNOSTYKA: Misja zakończona. Celowo zatrzymuję skrypt.")
        sys.exit(1) # Zakończ z kodem błędu

    except Exception as e:
        print(f"DIAGNOSTYKA: Wystąpił krytyczny błąd: {e}")
        # Wydrukuj również odpowiedź, jeśli ją mamy, to może pomóc.
        if 'final_page_response' in locals():
            print("\n--- KOD HTML (z błędu) ---")
            print(final_page_response.text)
            print("--- KONIEC KODU HTML (z błędu) ---\n")
        sys.exit(1)

if __name__ == "__main__":
    run_diagnostics()
