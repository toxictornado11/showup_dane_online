# scraper.py - WERSJA OSTATECZNA (SELENIUM)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime
import os
import re

BASE_URL = "https://showup.tv/"
OUTPUT_FILE = "dane.csv"
# Wyrażenie regularne do wyciągania liczb
STATS_REGEX = r'(\d+)\s*transmisji\s*i\s*(\d+)\s*oglądających'

def gather_stats():
    """Używa pełnej przeglądarki Selenium do interakcji ze stroną."""
    # Ustawienia przeglądarki Chrome do działania w tle na serwerze
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36')
    
    driver = None
    try:
        print("Uruchamianie wirtualnej przeglądarki Chrome...")
        driver = webdriver.Chrome(options=options)
        driver.get(BASE_URL)
        print("Strona załadowana. Sprawdzanie, czy jest bramka...")

        # KROK 1: Kliknij przycisk "Wchodzę", jeśli istnieje
        try:
            # Czekamy maksymalnie 10 sekund na pojawienie się przycisku
            enter_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Wchodzę')]"))
            )
            print("Znaleziono przycisk 'Wchodzę'. Klikam...")
            enter_button.click()
        except TimeoutException:
            print("Nie znaleziono przycisku 'Wchodzę' w ciągu 10 sekund. Zakładam, że jesteśmy na stronie głównej.")

        # KROK 2: Poczekaj na załadowanie danych
        print("Czekanie na pojawienie się danych na stronie głównej...")
        try:
            # Czekamy maksymalnie 20 sekund, aż pojawi się element h4 zawierający słowo "transmisji"
            stats_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'transmisji')]"))
            )
            print("Dane załadowane. Odczytywanie...")
            stats_text = stats_element.text # Pobieramy tekst, np. "79 transmisji i 3682 oglądających"
            
            # KROK 3: Wyciągnij liczby z tekstu
            match = re.search(STATS_REGEX, stats_text)
            if match:
                active_streams = match.group(1)
                users_online = match.group(2)
                print(f"Sukces! Znaleziono: {users_online} użytkowników, {active_streams} transmisji.")
                return users_online, active_streams
            else:
                print("Nie udało się wyciągnąć danych z tekstu: " + stats_text)
                return "BŁĄD PARSOWANIA", "BŁĄD PARSOWANIA"

        except TimeoutException:
            print("Dane nie pojawiły się na stronie w ciągu 20 sekund.")
            return "TIMEOUT DANYCH", "TIMEOUT DANYCH"

    except Exception as e:
        print(f"Wystąpił krytyczny błąd Selenium: {e}")
        return "BŁĄD KRYTYCZNY", "BŁĄD KRYTYCZNY"
    finally:
        if driver:
            driver.quit()
            print("Przeglądarka zamknięta.")

def save_to_csv(data):
    file_exists = os.path.isfile(OUTPUT_FILE)
    with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
        if not file_exists:
            f.write("data_i_godzina,uzytkownicy_online,aktywne_transmisje\n")
        f.write(f"{data[0]},{data[1]},{data[2]}\n")

if __name__ == "__main__":
    print("Rozpoczynam zbieranie danych za pomocą Selenium...")
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    users, streams = gather_stats()
    save_to_csv((current_time, users, streams))
    print(f"Dane zostały zapisane do pliku {OUTPUT_FILE}")
