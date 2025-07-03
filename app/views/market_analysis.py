from django.shortcuts import render
from django.db import connection
from matplotlib import pyplot as plt
import pandas as pd
import io
import base64
import matplotlib.dates as mdates
from matplotlib import style
import matplotlib
from mplfinance.original_flavor import candlestick_ohlc
import numpy as np
from sklearn.linear_model import LinearRegression
from django.http import JsonResponse

matplotlib.use('Agg')
style.use('ggplot')

# ----- Table mapping -----
TABLE_MAP = {
    'Dow Jones': 'dow_jones',
    'S&P 500': 'sp_500',
    'Nasdaq': 'nasdaq',
}

# ----- Fetch available stock indexes -----
def fetch_stock_indexes():
    return list(TABLE_MAP.keys())

# ----- Fetch OHLC data -----
def fetch_ohlc_data(stock_index, method):
    table = TABLE_MAP.get(stock_index)
    if not table:
        return pd.DataFrame()

    with connection.cursor() as cursor:
        if method == 'average':
            sql = f"""
                SELECT DATE_TRUNC('month', "Date") AS month,
                       AVG("Open Price") AS open,
                       AVG("High Price") AS high,
                       AVG("Low Price") AS low,
                       AVG("Close Price") AS close,
                       AVG("Trading Volume") AS volume
                FROM {table}
                GROUP BY month
                ORDER BY month
            """
        else:
            sql = f"""
                WITH monthly_data AS (
                    SELECT 
                        DATE_TRUNC('month', "Date") AS month,
                        "Date",
                        "Open Price",
                        "Close Price",
                        "High Price",
                        "Low Price",
                        "Trading Volume"
                    FROM {table}
                ),
                ranked_data AS (
                    SELECT *,
                        ROW_NUMBER() OVER (PARTITION BY month ORDER BY "Date" ASC) AS rn_open,
                        ROW_NUMBER() OVER (PARTITION BY month ORDER BY "Date" DESC) AS rn_close
                    FROM monthly_data
                )
                SELECT 
                    month,
                    MAX(CASE WHEN rn_open = 1 THEN "Open Price" END) AS open,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY "High Price") AS high,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY "Low Price") AS low,
                    MAX(CASE WHEN rn_close = 1 THEN "Close Price" END) AS close,
                    SUM("Trading Volume") AS volume
                FROM ranked_data
                GROUP BY month
                ORDER BY month;
            """

        cursor.execute(sql)
        rows = cursor.fetchall()
        return pd.DataFrame(rows, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])

# ----- Compute overlays -----
def compute_linear_regression(df):
    X = mdates.date2num(df['Date']).reshape(-1, 1)
    y = df['Close'].values
    model = LinearRegression()
    model.fit(X, y)
    trend = model.predict(X)
    return trend

def compute_sma(df, window=5):
    return df['Close'].rolling(window=window).mean()

def compute_ema(df, span=5):
    return df['Close'].ewm(span=span, adjust=False).mean()

def compute_vwap(df):
    high = df['High'].astype(float)
    low = df['Low'].astype(float)
    close = df['Close'].astype(float)
    volume = df['Volume'].astype(float)
    typical_price = (high + low + close) / 3
    vwap = (typical_price * volume).cumsum() / volume.cumsum()
    return vwap

# ----- Generate candlestick chart -----
def generate_candlestick_chart(df, overlay='none'):
    df['Date'] = pd.to_datetime(df['Date'])
    df['Date_Num'] = mdates.date2num(df['Date'])

    ohlc = df[['Date_Num', 'Open', 'High', 'Low', 'Close']]
    volume = df['Volume']

    fig, ax1 = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('#0d1b2a')
    ax1.set_facecolor('#0d1b2a')
    ax2 = ax1.twinx()
    ax2.set_facecolor('#0d1b2a')

    candlestick_ohlc(ax1, ohlc.values, width=10, colorup='lime', colordown='tomato', alpha=0.8)
    ax2.fill_between(df['Date_Num'], 0, volume, facecolor='lightblue', alpha=0.3)

    ax1.xaxis_date()
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

    ax1.set_ylabel('Price', color='white')
    ax2.set_ylabel('Volume', color='white')
    ax1.set_xlabel('Date', color='white')
    ax1.set_title('OHLC Market Analysis with Volume', color='white')

    ax1.tick_params(axis='x', colors='white')
    ax1.tick_params(axis='y', colors='white')
    ax2.tick_params(axis='y', colors='white')

    if overlay == 'regression':
        trend = compute_linear_regression(df)
        ax1.plot(df['Date_Num'], trend, color='cyan', label='Linear Regression', linewidth=2)
    elif overlay == 'sma':
        sma = compute_sma(df)
        ax1.plot(df['Date_Num'], sma, color='orange', label='SMA (5 months)', linewidth=2)
    elif overlay == 'ema':
        ema = compute_ema(df)
        ax1.plot(df['Date_Num'], ema, color='magenta', label='EMA (5 months)', linewidth=2)
    elif overlay == 'vwap':
        vwap = compute_vwap(df)
        ax1.plot(df['Date_Num'], vwap, color='cyan', label='VWAP', linewidth=2)

    if overlay in ('regression', 'sma', 'ema', 'vwap'):
        legend = ax1.legend()
        for text in legend.get_texts():
            text.set_color("white")
        legend.get_frame().set_facecolor('#0d1b2a')
        legend.get_frame().set_edgecolor('none')

    ax1.grid(True, which='major', color='#415a77', linewidth=0.2)
    ax2.grid(False)

    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=200, facecolor=fig.get_facecolor())
    plt.close(fig)
    buffer.seek(0)

    return base64.b64encode(buffer.read()).decode('utf-8')

# ----- Market analysis main view -----
def market_analysis(request):
    selected_index = request.GET.get('index', 'Dow Jones')
    method = request.GET.get('method', 'absolute')
    overlay = request.GET.get('overlay', 'none')

    indexes = fetch_stock_indexes()
    df = fetch_ohlc_data(selected_index, method)
    chart_base64 = generate_candlestick_chart(df, overlay) if not df.empty else None

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'chart': chart_base64})

    return render(request, 'market-analysis.html', {
        'chart': chart_base64,
        'indexes': indexes,
        'selected_index': selected_index,
        'method': method,
        'overlay': overlay,
    })
