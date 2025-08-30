# generate_chart.py
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

DATA_FILE = 'dane.csv'
OUTPUT_FILE = 'index.html'

def create_chart():
    """Wczytuje dane z CSV i generuje interaktywny wykres w pliku HTML."""
    try:
        df = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        print(f"Plik {DATA_FILE} nie istnieje. Tworzę pusty plik HTML.")
        with open(OUTPUT_FILE, 'w') as f:
            f.write("<html><body><h1>Brak danych do wygenerowania wykresu.</h1></body></html>")
        return

    # Konwertujemy kolumnę z datą na faktyczny typ daty
    df['data_i_godzina'] = pd.to_datetime(df['data_i_godzina'])

    # Tworzymy wykres z dwiema osiami Y
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Dodajemy ślad dla użytkowników online (lewa oś Y)
    fig.add_trace(
        go.Scatter(x=df['data_i_godzina'], y=df['uzytkownicy_online'], name='Użytkownicy online',
                   line=dict(color='royalblue', width=2)),
        secondary_y=False,
    )

    # Dodajemy ślad dla aktywnych transmisji (prawa oś Y)
    fig.add_trace(
        go.Scatter(x=df['data_i_godzina'], y=df['aktywne_transmisje'], name='Aktywne transmisje',
                   line=dict(color='firebrick', width=2, dash='dot')),
        secondary_y=True,
    )

    # Ustawienia tytułów i osi
    fig.update_layout(
        title_text='Statystyki ShowUp.tv w Czasie',
        xaxis_title='Data i Godzina',
        legend_title='Legenda',
        template='plotly_dark'
    )
    fig.update_yaxes(title_text='<b>Użytkownicy online</b>', secondary_y=False, color='royalblue')
    fig.update_yaxes(title_text='<b>Aktywne transmisje</b>', secondary_y=True, color='firebrick')

    # Dodajemy przyciski do zmiany zakresu czasu
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1h", step="hour", stepmode="backward"),
                dict(count=6, label="6h", step="hour", stepmode="backward"),
                dict(count=12, label="12h", step="hour", stepmode="backward"),
                dict(count=1, label="24h", step="day", stepmode="backward"),
                dict(count=7, label="1d", step="day", stepmode="backward"),
                dict(step="all")
            ]),
            bgcolor="#333",
            bordercolor="#555",
            font=dict(color="white")
        )
    )

    # Zapisujemy wykres do pliku HTML
    fig.write_html(OUTPUT_FILE, include_plotlyjs='cdn')
    print(f"Wykres został zapisany do pliku {OUTPUT_FILE}")

if __name__ == "__main__":
    create_chart()
