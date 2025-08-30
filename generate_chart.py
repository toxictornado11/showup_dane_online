# generate_chart.py - WERSJA Z ANALIZATOREM
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

DATA_FILE = 'dane.csv'
OUTPUT_FILE = 'index.html'

# --- NOWA FUNKCJA DO CZYSZCZENIA DANYCH ---
def clean_and_load_data():
    """Wczytuje dane i czyści je z historycznych błędów."""
    try:
        df = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        return None

    # Konwertujemy kolumny na liczby, a wszystkie błędy (stare teksty) zamieniamy na puste komórki (NaN)
    df['uzytkownicy_online'] = pd.to_numeric(df['uzytkownicy_online'], errors='coerce')
    df['aktywne_transmisje'] = pd.to_numeric(df['aktywne_transmisje'], errors='coerce')
    
    # Jeśli kolumna czasu wykonania nie istnieje, stwórz ją i wypełnij zerami
    if 'czas_wykonania_s' not in df.columns:
        df['czas_wykonania_s'] = 0
    df['czas_wykonania_s'] = pd.to_numeric(df['czas_wykonania_s'], errors='coerce').fillna(0)

    # Konwertujemy kolumnę z datą
    df['data_i_godzina'] = pd.to_datetime(df['data_i_godzina'])
    
    return df

def create_chart_and_analysis():
    df = clean_and_load_data()

    if df is None or df.empty:
        print(f"Plik {DATA_FILE} nie istnieje lub jest pusty.")
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write("<html><body><h1>Brak danych do wygenerowania wykresu.</h1></body></html>")
        return

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df['data_i_godzina'], y=df['uzytkownicy_online'], name='Użytkownicy online', line=dict(color='royalblue', width=2)), secondary_y=False)
    fig.add_trace(go.Scatter(x=df['data_i_godzina'], y=df['aktywne_transmisje'], name='Aktywne transmisje', line=dict(color='firebrick', width=2, dash='dot')), secondary_y=True)

    fig.update_layout(title_text='Statystyki ShowUp.tv w Czasie', template='plotly_dark')
    fig.update_yaxes(title_text='<b>Użytkownicy online</b>', secondary_y=False, color='royalblue')
    fig.update_yaxes(title_text='<b>Aktywne transmisje</b>', secondary_y=True, color='firebrick')
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1h", step="hour", stepmode="backward"),
                dict(count=6, label="6h", step="hour", stepmode="backward"),
                dict(count=12, label="12h", step="hour", stepmode="backward"),
                dict(count=1, label="24h", step="day", stepmode="backward"),
                dict(count=7, label="7d", step="day", stepmode="backward"),
                dict(step="all")
            ]),
            bgcolor="#333", bordercolor="#555", font=dict(color="white")
        )
    )

    # --- NOWA SEKCJA: ANALIZA CZASU WYKONANIA ---
    avg_duration = df[df['czas_wykonania_s'] > 0]['czas_wykonania_s'].mean()
    runs_per_day_20min = 24 * 3
    runs_per_day_30min = 24 * 2
    
    monthly_usage_20min = (avg_duration * runs_per_day_20min * 30) / 60 if avg_duration > 0 else 0
    monthly_usage_30min = (avg_duration * runs_per_day_30min * 30) / 60 if avg_duration > 0 else 0

    analysis_html = f"""
    <div style="font-family: Arial, sans-serif; color: white; background-color: #111; padding: 20px; border-radius: 10px; margin-top: 20px;">
        <h2 style="border-bottom: 2px solid #555; padding-bottom: 10px;">Analizator Limitu GitHub Actions</h2>
        <p><strong>Średni czas wykonania jednego zadania:</strong> {avg_duration:.2f} sekund</p>
        <hr style="border-color: #333;">
        <h4 style="margin-bottom: 5px;">Scenariusz: Uruchomienie co 20 minut (72 / dobę)</h4>
        <p><strong>Szacowane miesięczne zużycie:</strong> <strong style="color: {'orange' if monthly_usage_20min > 1800 else 'lightgreen'};">{monthly_usage_20min:.0f}</strong> / 2000 minut</p>
        <h4 style="margin-bottom: 5px;">Scenariusz: Uruchomienie co 30 minut (48 / dobę)</h4>
        <p><strong>Szacowane miesięczne zużycie:</strong> <strong style="color: {'orange' if monthly_usage_30min > 1800 else 'lightgreen'};">{monthly_usage_30min:.0f}</strong> / 2000 minut</p>
        <p style="font-size: 12px; color: #888;"><i>Powyższe dane są szacunkowe i bazują na dotychczasowych uruchomieniach. Darmowy limit dla repozytoriów publicznych to 2000 minut/miesiąc.</i></p>
    </div>
    """

    # Łączymy wykres i analizę w jeden plik HTML
    chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"""
        <html>
            <head><title>Statystyki ShowUp.tv</title></head>
            <body style="background-color: #111;">
                {chart_html}
                {analysis_html}
            </body>
        </html>
        """)
    print(f"Wykres i analiza zostały zapisane do pliku {OUTPUT_FILE}")

if __name__ == "__main__":
    create_chart_and_analysis()
