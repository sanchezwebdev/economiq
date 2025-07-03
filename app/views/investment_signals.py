from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib
import io, base64
import numpy as np

matplotlib.use("Agg")

# ----- Field and color definitions -----
FIELDS = {
    'USD/EUR': 'usd_eur_rate',
    'USD/JPY': 'usd_jpy_rate',
    'Crude Oil Price': 'crude_oil_price',
    'Gold Price': 'gold_price'
}

COLORS = {
    'background': '#0d1b2a',
    'primary': '#415a77',
    'secondary': '#acb8c3',
    'text': '#f5f5f4',
    'highlight': '#ffcf33',
}

# ----- Normalize series helper -----
def normalize(series):
    return (series - series.min()) / (series.max() - series.min())

# ----- Plot stacked ICI chart -----
def plot_investment_climate_index(df):
    fig, ax1 = plt.subplots(figsize=(10, 4))
    df['Date'] = pd.to_datetime(df['Date'])

    fig.patch.set_facecolor(COLORS['background'])
    ax1.set_facecolor(COLORS['background'])

    ax1.stackplot(
        df['Date'],
        df['vc_funding_volume'],
        df['corporate_profits'],
        labels=["VC Funding", "Corporate Profits"],
        colors=[COLORS['primary'], COLORS['secondary']],
        alpha=0.85
    )
    ax1.set_ylabel("USD Volume", color=COLORS['text'])
    ax1.tick_params(axis='y', labelcolor=COLORS['text'])
    ax1.legend(loc='upper left', facecolor=COLORS['background'], edgecolor='none', labelcolor=COLORS['text'])

    ax2 = ax1.twinx()
    ax2.set_facecolor(COLORS['background'])
    ax2.plot(df['Date'], df['Investment Climate Index'], color=COLORS['highlight'], linewidth=2, label='ICI Ratio')
    ax2.set_ylabel("ICI Ratio", color=COLORS['highlight'])
    ax2.tick_params(axis='y', labelcolor=COLORS['highlight'])
    ax2.legend(loc='upper right', facecolor=COLORS['background'], edgecolor='none', labelcolor=COLORS['text'])

    ax1.set_title("Investment Climate Index (VC Funding / Corporate Profits)", color=COLORS['text'])
    ax1.set_xlabel("Date", color=COLORS['text'])
    ax1.tick_params(axis='x', labelcolor=COLORS['text'])

    ax1.grid(True, which='major', color='#EAEFEF', linewidth=0.1)
    if ax2:
        ax2.grid(False)
    fig.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=200, facecolor=fig.get_facecolor())
    chart_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()
    return chart_data

# ----- Investment signals main view -----
def investment_signals(request):
    field1_label = request.GET.get('field1', 'USD/EUR')
    field2_label = request.GET.get('field2', 'Gold Price')

    if field1_label == field2_label:
        field2_label = next(f for f in FIELDS if f != field1_label)

    field1 = FIELDS[field1_label]
    field2 = FIELDS[field2_label]

    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT "Date", {field1}, {field2}, vc_funding_volume, corporate_profits
            FROM real_econ_data
            WHERE "Date" >= '2007-01-01'
            ORDER BY "Date"
        """)
        data = cursor.fetchall()

    df = pd.DataFrame(data, columns=[
        "Date", "field1", "field2", "vc_funding_volume", "corporate_profits"
    ])
    df["Date"] = pd.to_datetime(df["Date"])
    df.dropna(inplace=True)
    df["vc_funding_volume"] = df["vc_funding_volume"].astype(float)
    df["corporate_profits"] = df["corporate_profits"].astype(float)

    df["norm1"] = normalize(df["field1"])
    df["norm2"] = normalize(df["field2"])

    fig, ax1 = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor(COLORS['background'])
    ax1.set_facecolor(COLORS['background'])
    ax2 = ax1.twinx()

    ax1.plot(df["Date"], df["norm1"], label=field1_label, color=COLORS['secondary'])
    ax2.plot(df["Date"], df["norm2"], label=field2_label, color=COLORS['highlight'])

    ax1.set_ylabel(f"{field1_label} (normalized)", color=COLORS['secondary'])
    ax2.set_ylabel(f"{field2_label} (normalized)", color=COLORS['highlight'])
    ax1.tick_params(axis='y', labelcolor=COLORS['secondary'])
    ax2.tick_params(axis='y', labelcolor=COLORS['highlight'])
    ax1.tick_params(axis='x', labelcolor=COLORS['text'])
    ax2.tick_params(axis='x', labelcolor=COLORS['text'])
    ax1.set_xlabel("Date", color=COLORS['text'])

    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    fig.autofmt_xdate()

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc="upper left", facecolor=COLORS['background'], labelcolor=COLORS['text'])

    ax1.grid(True, which='major', color='#EAEFEF', linewidth=0.1)
    if ax2:
        ax2.grid(False)
    fig.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=200, facecolor=fig.get_facecolor())
    chart_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()

    df["Investment Climate Index"] = df["vc_funding_volume"] / df["corporate_profits"]
    chart_stacked = plot_investment_climate_index(df)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'chart': chart_data,
            'chart_stacked': chart_stacked
        })
    else:
        return render(request, 'investment-signals.html', {
            "chart": chart_data,
            "chart_stacked": chart_stacked,
            "fields": list(FIELDS.keys()),
            "selected_field1": field1_label,
            "selected_field2": field2_label
        })

# ----- Plot business health score heatmap -----
def plot_health_score_heatmap(df):
    df["Date"] = pd.to_datetime(df["Date"])
    df["Business Health Score"] = df["mna_deals_volume"] / df["bankruptcy_rate"]
    df.sort_values("Date", inplace=True)

    norm_scores = (df["Business Health Score"] - df["Business Health Score"].min()) / \
                  (df["Business Health Score"].max() - df["Business Health Score"].min())

    fig, ax = plt.subplots(figsize=(10, 1.5))
    fig.patch.set_facecolor(COLORS['background'])

    colors = plt.cm.RdYlGn(norm_scores)

    for i, (date, score) in enumerate(zip(df["Date"], norm_scores)):
        ax.bar(date, 1, width=15, color=colors[i], align='center')

    ax.set_facecolor(COLORS['background'])
    ax.set_yticks([])
    ax.set_xlim(df["Date"].min(), df["Date"].max())
    ax.set_title("Business Health Score Over Time", color=COLORS['text'])
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.tick_params(axis='x', labelcolor=COLORS['text'])

    fig.autofmt_xdate()
    fig.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=200, facecolor=fig.get_facecolor())
    chart_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()
    plt.close(fig)
    return chart_data
