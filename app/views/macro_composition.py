import io
import base64
import matplotlib.pyplot as plt
import numpy as np
from django.shortcuts import render
from django.db import connection
import pandas as pd
from django.http import JsonResponse

#  Macro composition main view 
def macro_composition(request):
    agg = request.GET.get('agg', 'year')

    #  Fetch data from DB 
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                "Date",
                "GDP Growth (%)" AS gdp_growth_percent,
                "Inflation Rate (%)" AS inflation_rate_percent,
                "Unemployment Rate (%)" AS unemployment_rate_percent,
                "Interest Rate (%)" AS interest_rate_percent
            FROM real_econ_data;
        """)
        rows = cursor.fetchall()

    columns = [
        'Date',
        'gdp_growth_percent',
        'inflation_rate_percent',
        'unemployment_rate_percent',
        'interest_rate_percent',
    ]

    df = pd.DataFrame(rows, columns=columns)
    df['Date'] = pd.to_datetime(df['Date'])

    #  Add additional indicators 
    np.random.seed(0)
    n = len(df)
    df['Corporate Profits (Billion USD)'] = np.random.uniform(100, 500, size=n)
    df['Consumer Spending (Billion USD)'] = np.random.uniform(300, 700, size=n)
    df['Government Debt (Billion USD)'] = np.random.uniform(200, 600, size=n)
    df['Retail Sales (Billion USD)'] = np.random.uniform(150, 400, size=n)

    #  Aggregate by period 
    if agg == 'quarter':
        df['Period'] = df['Date'].dt.to_period('Q').dt.start_time
    else:
        df['Period'] = df['Date'].dt.to_period('Y').dt.start_time

    grouped = df.groupby('Period').agg({
        'gdp_growth_percent': 'mean',
        'inflation_rate_percent': 'mean',
        'unemployment_rate_percent': 'mean',
        'interest_rate_percent': 'mean',
        'Corporate Profits (Billion USD)': 'sum',
        'Consumer Spending (Billion USD)': 'sum',
        'Government Debt (Billion USD)': 'sum',
        'Retail Sales (Billion USD)': 'sum',
    }).reset_index()

    #  Normalize selected columns 
    cols_to_normalize = [
        'gdp_growth_percent',
        'inflation_rate_percent',
        'unemployment_rate_percent',
        'interest_rate_percent'
    ]

    for col in cols_to_normalize:
        grouped[col] = pd.to_numeric(grouped[col], errors='coerce')
    grouped[cols_to_normalize] = grouped[cols_to_normalize].fillna(0)

    vals = grouped[cols_to_normalize].values.astype(float)
    row_sums = vals.sum(axis=1).reshape(-1, 1)
    row_sums[row_sums == 0] = 1
    normalized_vals = vals / row_sums

    #  Plot bar chart 
    labels = grouped['Period'].dt.strftime('%Y-%m-%d')
    components = cols_to_normalize
    colors = ['#79aea3', '#ebebeb', '#deb72b', '#f3663f']

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor('#0d1b2a')
    ax.set_facecolor('#0d1b2a')

    bottom = np.zeros(len(labels))
    for i, comp in enumerate(components):
        ax.bar(labels, normalized_vals[:, i], bottom=bottom,
               label=comp.replace('_', ' ').title(), color=colors[i])
        bottom += normalized_vals[:, i]

    ax.grid(True, which='major', color='#EAEFEF', linewidth=0.2)
    ax.set_xlabel('Date', color='#ebebeb')
    ax.set_ylabel('Normalized Contribution', color='#ebebeb')
    ax.set_title('Economic Composition Over Time (Normalized)', color='#ebebeb')
    ax.legend(loc='upper left', facecolor='#0d1b2a', labelcolor='#ebebeb', edgecolor='none')
    ax.tick_params(axis='x', colors='#ebebeb')
    ax.tick_params(axis='y', colors='#ebebeb')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    #  Save and encode chart 
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=200, facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')

    #  Return JSON or render template 
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'chart': image_base64})

    return render(request, 'macro-composition.html', {
        'chart': image_base64,
        'agg': agg,
    })
