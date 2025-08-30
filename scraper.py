# scraper.py - WERSJA Z ANALIZATOREM CZASU
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime
import os
import re
from zoneinfo import ZoneInfo
import time # --- ZMIANA: Importujemy moduł do mierzenia czasu ---

BASE_URL = "https://showup.tv/"
OUTPUT_FILE = "dane.csv"
STATS_REGEX = r'(\d+)\s*transmisji\s*i\s*(\d+)\s*oglądających'

def gather_stats():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36')
    
    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.get(BASE_URL)

        try:
            enter_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Wchodzę')]"))
            )
            enter_button.click()
        except TimeoutException:
            pass # Ignorujemy, jeśli nie ma przycisku

        try:
            stats_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'transmisji')]"))
            )
            stats_text = stats_element.text
            
            match = re.search(STATS_REGEX, stats_text)
            if match:
                active_streams = match.group(1)
                users_online = match.group(2)
                print(f"Sukces! Znaleziono: {users_online} użytkowników, {active_streams} transmisji.")
                return users_online, active_streams
            else:
                # --- ZMIANA: Zwracamy puste wartości zamiast tekstu błędu ---
                return '', ''
        except TimeoutException:
            # --- ZMIANA: Zwracamy puste wartości zamiast tekstu błędu ---
            return '', ''

    except Exception as e:
        print(f"Wystąpił krytyczny błąd Selenium: {e}")
        # --- ZMIANA: Zwracamy puste wartości zamiast tekstu błędu ---
        return '', ''
    finally:
        if driver:
            driver.quit()

def save_to_csv(data):
    file_exists = os.path.isfile(OUTPUT_FILE)
    with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
        # --- ZMIANA: Dodajemy nową kolumnę do nagłówka ---
        if not file_exists or os.path.getsize(OUTPUT_FILE) == 0:
            f.write("data_i_godzina,uzytkownicy_online,aktywne_transmisje,czas_wykonania_s\n")
        
        # --- ZMIANA: Zapisujemy cztery wartości ---
        f.write(f"{data[0]},{data[1]},{data[2]},{data[3]}\n")

if __name__ == "__main__":
    start_time = time.time() # --- ZMIANA: Zapisujemy czas startu ---
    
    print("Rozpoczynam zbieranie danych za pomocą Selenium...")
    current_time = datetime.now(ZoneInfo("Europe/Warsaw")).strftime('%Y-%m-%d %H:%M:%S')
    users, streams = gather_stats()
    
    end_time = time.time() # --- ZMIANA: Zapisujemy czas końca ---
    duration = round(end_time - start_time, 2) # --- ZMIANA: Obliczamy czas trwania ---
    
    print(f"Czas wykonania skryptu: {duration}s")
    
    # --- ZMIANA: Przekazujemy czas trwania do funkcji zapisującej ---
    save_to_csv((current_time, users, streams, duration))
    print(f"Dane zostały zapisane do pliku {OUTPUT_FILE}")
