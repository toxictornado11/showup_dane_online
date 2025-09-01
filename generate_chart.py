# generate_chart.py - WERSJA Z FINALNYM, KOMPAKTOWYM INTERFEJSEM v12 (ROBUST BUTTON LOGIC)
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime
from zoneinfo import ZoneInfo

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
        mode='lines+markers', line=dict(color='royalblue', width=2), marker=dict(size=5),
        hovertemplate='<b>Użytkownicy:</b> %{y}<extra></extra>'
    ), secondary_y=False)
    
    fig.add_trace(go.Scatter(
        x=df['data_i_godzina'], y=df['aktywne_transmisje'], name='Aktywne transmisje',
        mode='lines+markers', line=dict(color='firebrick', width=2), marker=dict(size=5),
        hovertemplate='<b>Transmisje:</b> %{y}<extra></extra>'
    ), secondary_y=True)

    fig.update_layout(
        title=dict(
            text='Statystyki ShowUp.tv',
            x=0.5,
            xanchor='center'
        ),
        template='plotly_dark',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=100, b=20),
        dragmode='pan',
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="rgba(17, 17, 17, 0.8)",
            bordercolor="rgba(150, 150, 150, 0.8)"
        )
    )
    
    # --- POCZĄTEK ZMIANY: Ujednolicenie logiki przycisków na "backward" ---
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                # Używamy "backward" dla wszystkich przycisków, aby zapewnić 100% niezawodności
                dict(count=1, label="1h", step="hour", stepmode="backward"),
                dict(count=6, label="6h", step="hour", stepmode="backward"),
                dict(count=12, label="12h", step="hour", stepmode="backward"),
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=7, label="7d", step="day", stepmode="backward"),
                dict(step="all", label="All")
            ]),
            x=0.01,
            y=1.15,
            xanchor="left",
            yanchor="top",
            bgcolor="#333",
            activecolor="#555",
            bordercolor="#666",
            font=dict(color="#FFFFFF")
        ),
        range=[df['data_i_godzina'].max() - pd.Timedelta(days=1), df['data_i_godzina'].max()]
    )
    # --- KONIEC ZMIANY ---
    
    fig.update_yaxes(title_text='<b>Użytkownicy online</b>', secondary_y=False, color='royalblue')
    fig.update_yaxes(title_text='<b>Aktywne transmisje</b>', secondary_y=True, color='firebrick')
    
    config = {'modeBarButtonsToRemove': ['zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d'], 'scrollZoom': True}

    now = datetime.now(ZoneInfo("Europe/Warsaw"))
    df_current_month = df[(df['data_i_godzina'].dt.year == now.year) & (df['data_i_godzina'].dt.month == now.month)]
    total_seconds_used = df_current_month['czas_wykonania_s'].sum()
    total_minutes_used = total_seconds_used / 60
    
    avg_duration = df[df['czas_wykonania_s'] > 0]['czas_wykonania_s'].mean()
    runs_per_day_current = 24 * 6
    monthly_usage_current = (avg_duration * runs_per_day_current * 30) / 60 if avg_duration > 0 else 0
    
    analysis_html = f"""
    <div class="analyzer">
        <div class="stats-grid">
            <div>
                <p class="stat-label">Dotychczasowe zużycie (w tym miesiącu):</p>
                <p class="stat-value">{total_minutes_used:.2f} / 2000 minut</p>
            </div>
            <div>
                <p class="stat-label">Średni czas zadania (całkowity):</p>
                <p class="stat-value">{avg_duration:.2f} sekund</p>
            </div>
            <div>
                <p class="stat-label">Szacowane zużycie miesięczne (co 10 min):</p>
                <p class="stat-value" style="color: {'orange' if monthly_usage_current > 1800 else 'lightgreen'};">{monthly_usage_current:.0f} / 2000 minut</p>
            </div>
        </div>
    </div>
    """

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
                    .chart-container {{ width: 100%; height: 70vh; }}
                    .analyzer {{ background-color: #1e1e1e; padding: 15px; border-radius: 10px; }}
                    .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; text-align: center; }}
                    .stat-label {{ margin: 0 0 5px 0; font-size: 14px; color: #aaa; }}
                    .stat-value {{ margin: 0; font-size: 18px; font-weight: bold; }}
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
