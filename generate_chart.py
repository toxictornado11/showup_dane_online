# generate_chart.py - WERSJA Z INTUICYJNYM WYKRESEM I LEPSZYM UX
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime

DATA_FILE = 'dane.csv'
OUTPUT_FILE = 'index.html'
GITHUB_ACTIONS_LIMIT_MINUTES = 2000

def clean_and_load_data():
    """Wczytuje dane i czyści je z historycznych błędów."""
    try:
        df = pd.read_csv(DATA_FILE, header=0)
    except FileNotFoundError:
        return None
    except pd.errors.ParserError:
        print(f"Błąd formatowania w pliku {DATA_FILE}. Plik zostanie zresetowany przy następnym uruchomieniu.")
        os.remove(DATA_FILE)
        return None

    df['uzytkownicy_online'] = pd.to_numeric(df['uzytkownicy_online'], errors='coerce')
    df['aktywne_transmisje'] = pd.to_numeric(df['aktywne_transmisje'], errors='coerce')
    
    if 'czas_wykonania_s' not in df.columns:
        df['czas_wykonania_s'] = 0
    df['czas_wykonania_s'] = pd.to_numeric(df['czas_wykonania_s'], errors='coerce').fillna(0)

    df['data_i_godzina'] = pd.to_datetime(df['data_i_godzina'])
    
    return df

def create_chart_and_analysis():
    df = clean_and_load_data()

    if df is None or df.empty:
        print(f"Plik {DATA_FILE} nie istnieje lub jest pusty. Tworzę pusty plik HTML.")
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write("<html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'></head><body><h1>Brak danych do wygenerowania wykresu. Czekam na pierwszy odczyt...</h1></body></html>")
        return

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(go.Scatter(x=df['data_i_godzina'], y=df['uzytkownicy_online'], name='Użytkownicy online', mode='lines', line=dict(color='royalblue', width=2.5)), secondary_y=False)
    fig.add_trace(go.Scatter(x=df['data_i_godzina'], y=df['aktywne_transmisje'], name='Aktywne transmisje', mode='lines', line=dict(color='firebrick', width=2, dash='dot')), secondary_y=True)

    # --- KLUCZOWE ZMIANY DLA INTUICYJNOŚCI ---
    fig.update_layout(
        title_text='Statystyki ShowUp.tv w Czasie',
        template='plotly_dark',
        hovermode='x unified',  # Ujednolicony tooltip dla osi X
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), # Legenda na górze
        margin=dict(l=20, r=20, t=80, b=20) # Zoptymalizowane marginesy
    )
    
    # Dodanie linii pomocniczych (spike lines) dla lepszej czytelności
    fig.update_xaxes(
        showspikes=True, spikemode='across', spikesnap='cursor', spikedash='dot', spikethickness=1,
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
    fig.update_yaxes(showspikes=True, spikemode='across', spikesnap='cursor', spikedash='dot', spikethickness=1)
    
    # Stylowanie osi Y
    fig.update_yaxes(title_text='<b>Użytkownicy online</b>', secondary_y=False, color='royalblue')
    fig.update_yaxes(title_text='<b>Aktywne transmisje</b>', secondary_y=True, color='firebrick')

    # --- Sekcja analizatora (bez zmian) ---
    now = datetime.now()
    current_month_df = df[df['data_i_godzina'].dt.month == now.month]
    total_seconds_this_month = current_month_df['czas_wykonania_s'].sum()
    total_minutes_this_month = total_seconds_this_month / 60
    usage_percentage = (total_minutes_this_month / GITHUB_ACTIONS_LIMIT_MINUTES) * 100

    avg_duration = df[df['czas_wykonania_s'] > 0]['czas_wykonania_s'].mean()
    runs_per_day_20min = 24 * 3
    runs_per_day_30min = 24 * 2
    
    monthly_usage_20min = (avg_duration * runs_per_day_20min * 30) / 60 if avg_duration > 0 else 0
    monthly_usage_30min = (avg_duration * runs_per_day_30min * 30) / 60 if avg_duration > 0 else 0

    analysis_html = f"""
    <div style="font-family: Arial, sans-serif; color: white; background-color: #1e1e1e; padding: 20px; border-radius: 10px; margin-top: 20px; border: 1px solid #333;">
        <h2 style="border-bottom: 2px solid #555; padding-bottom: 10px;">Analizator Limitu GitHub Actions</h2>
        <h4 style="margin-bottom: 5px;">Zużycie w bieżącym miesiącu ({now.strftime('%B %Y')}):</h4>
        <p style="font-size: 18px; margin-top: 5px;">
            <strong style="color: {'orange' if total_minutes_this_month > 1800 else 'lightgreen'};">{total_minutes_this_month:.0f}</strong> / {GITHUB_ACTIONS_LIMIT_MINUTES} minut
        </p>
        <div style="background-color: #333; border-radius: 5px; padding: 2px; border: 1px solid #555;">
            <div style="width: {usage_percentage:.2f}%; background-color: {'#d9534f' if usage_percentage > 90 else '#f0ad4e' if usage_percentage > 75 else '#5cb85c'}; height: 20px; border-radius: 4px; text-align: center; line-height: 20px; font-size: 12px; color: #fff;">
                {usage_percentage:.1f}%
            </div>
        </div>
        <hr style="border-color: #333; margin-top: 20px;">
        <p><strong>Średni czas wykonania jednego zadania:</strong> {avg_duration:.2f} sekund</p>
        <h4 style="margin-bottom: 5px;">Scenariusz: Uruchomienie co 20 minut (72 / dobę)</h4>
        <p><strong>Szacowane miesięczne zużycie:</strong> <strong style="color: {'orange' if monthly_usage_20min > 1800 else 'lightgreen'};">{monthly_usage_20min:.0f}</strong> / {GITHUB_ACTIONS_LIMIT_MINUTES} minut</p>
        <h4 style="margin-bottom: 5px;">Scenariusz: Uruchomienie co 30 minut (48 / dobę)</h4>
        <p><strong>Szacowane miesięczne zużycie:</strong> <strong style="color: {'orange' if monthly_usage_30min > 1800 else 'lightgreen'};">{monthly_usage_30min:.0f}</strong> / {GITHUB_ACTIONS_LIMIT_MINUTES} minut</p>
        <p style="font-size: 12px; color: #888; margin-top: 15px;"><i>Powyższe dane są szacunkowe. Darmowy limit dla repozytoriów publicznych to {GITHUB_ACTIONS_LIMIT_MINUTES} minut/miesiąc.</i></p>
    </div>
    """

    chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"""
        <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Statystyki ShowUp.tv</title>
            </head>
            <body style="background-color: #111;">
                {chart_html}
                {analysis_html}
            </body>
        </html>
        """)
    print(f"Wykres i analiza zostały zapisane do pliku {OUTPUT_FILE}")

if __name__ == "__main__":
    create_chart_and_analysis()
