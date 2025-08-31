# generate_chart.py - WERSJA Z FINALNYM INTERFEJSEM
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

DATA_FILE = 'dane.csv'
OUTPUT_FILE = 'index.html'

def clean_and_load_data():
    """Wczytuje dane i czyści je z historycznych błędów."""
    try:
        df = pd.read_csv(DATA_FILE, header=0)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return None
    except pd.errors.ParserError:
        print(f"Błąd formatowania w pliku {DATA_FILE}. Resetuję plik.")
        os.remove(DATA_FILE)
        return None

    df['uzytkownicy_online'] = pd.to_numeric(df['uzytkownicy_online'], errors='coerce')
    df['aktywne_transmisje'] = pd.to_numeric(df['aktywne_transmisje'], errors='coerce')
    
    if 'czas_wykonania_s' not in df.columns:
        df['czas_wykonania_s'] = 0
    df['czas_wykonania_s'] = pd.to_numeric(df['czas_wykonania_s'], errors='coerce').fillna(0)

    df['data_i_godzina'] = pd.to_datetime(df['data_i_godzina'])
    
    return df

def create_dashboard():
    df = clean_and_load_data()

    if df is None or df.empty:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write("<html><head><title>Statystyki</title></head><body><h1>Brak danych. Czekam na pierwszy odczyt...</h1></body></html>")
        return

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        x=df['data_i_godzina'], y=df['uzytkownicy_online'], name='Użytkownicy online',
        mode='lines+markers', line=dict(color='royalblue', width=2), marker=dict(size=5)
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=df['data_i_godzina'], y=df['aktywne_transmisje'], name='Aktywne transmisje',
        mode='lines+markers', line=dict(color='firebrick', width=2, dash='dot'), marker=dict(size=5)
    ), secondary_y=True)

    # --- ZMIANY W UKŁADZIE WYKRESU ---
    fig.update_layout(
        title_text='Statystyki ShowUp.tv w Czasie',
        template='plotly_dark',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=50, b=20),
        dragmode='pan', # Ustawiamy "Pan" (przesuwanie) jako domyślne narzędzie
        xaxis_rangeslider_visible=True, # Dodajemy suwak zakresu (Range Slider) pod wykresem
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1h", step="hour", stepmode="backward"),
                    dict(count=6, label="6h", step="hour", stepmode="backward"),
                    dict(count=12, label="12h", step="hour", stepmode="backward"),
                    dict(count=1, label="24h", step="day", stepmode="backward"),
                    dict(count=7, label="7d", step="day", stepmode="backward"),
                    dict(step="all", label="Całość")
                ]),
                bgcolor="#333", bordercolor="#555", font=dict(color="white")
            )
        )
    )
    fig.update_yaxes(title_text='<b>Użytkownicy online</b>', secondary_y=False, color='royalblue')
    fig.update_yaxes(title_text='<b>Aktywne transmisje</b>', secondary_y=True, color='firebrick')
    
    # Konfiguracja paska narzędzi - usuwamy narzędzia zoomu
    config = {'modeBarButtonsToRemove': ['zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d'], 'scrollZoom': True}

    total_seconds_used = df['czas_wykonania_s'].sum()
    total_minutes_used = total_seconds_used / 60
    start_date = df['data_i_godzina'].min().strftime('%Y-%m-%d')
    end_date = df['data_i_godzina'].max().strftime('%Y-%m-%d')

    # --- ZMIANA W ANALIZATORZE: Poprawka wyświetlania tekstu ---
    analysis_html = f"""
    <div class="analyzer">
        <h2>Analizator Limitu GitHub Actions</h2>
        <p><strong>Dotychczasowe zużycie:</strong></p>
        <div class="usage-bar">
            <div class="usage-fill" style="width: {min(total_minutes_used / 2000 * 100, 100):.2f}%;"></div>
            <span class="usage-text">{total_minutes_used:.2f} / 2000 minut</span>
        </div>
        <p class="info"><i>Dane zebrane w okresie od {start_date} do {end_date}. Limit odnawia się co miesiąc.</i></p>
    </div>
    """

    # Zmieniamy sposób generowania HTML, aby przekazać konfigurację
    chart_div = fig.to_html(full_html=False, include_plotlyjs='cdn', config=config)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"""
        <!DOCTYPE html>
        <html lang="pl">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Statystyki ShowUp.tv</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #111; color: white; margin: 0; padding: 15px; }}
                    .container {{ display: flex; flex-direction: column; gap: 20px; }}
                    .chart-container {{ width: 100%; height: 65vh; }}
                    .analyzer {{ background-color: #1e1e1e; padding: 20px; border-radius: 10px; }}
                    .analyzer h2 {{ margin-top: 0; border-bottom: 2px solid #555; padding-bottom: 10px; }}
                    /* --- ZMIANY W STYLACH PASKA POSTĘPU --- */
                    .usage-bar {{ position: relative; background-color: #333; border-radius: 5px; overflow: hidden; height: 30px; border: 1px solid #555; }}
                    .usage-fill {{ background-color: #00cc96; height: 100%; transition: width 0.5s ease-in-out; }}
                    .usage-text {{ position: absolute; top: 0; left: 0; right: 0; bottom: 0; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; text-shadow: 1px 1px 2px black; }}
                    .info {{ font-size: 12px; color: #888; text-align: center; margin-top: 10px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="chart-container">{chart_div}</div>
                    {analysis_html}
                </div>
            </body>
        </html>
        """)
    print(f"Dashboard został zapisany do pliku {OUTPUT_FILE}")

if __name__ == "__main__":
    create_dashboard()
