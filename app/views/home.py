from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.interpolate import make_interp_spline

#  Metric label mappings 
metrics = {
    'GDP Growth Rate': 'GDP Growth (%)',
    'CPI (Inflation)': 'Inflation Rate (%)',
    'Unemployment Rate': 'Unemployment Rate (%)',
    'Federal Funds Rate': 'Interest Rate (%)',
    'Consumer Confidence': 'Consumer Confidence Index'
}

#  Render combined line chart 
def render_combined_chart(selected_metrics, timeframe='month'):
    if not selected_metrics:
        return ''

    timeframe = timeframe.lower()
    if timeframe not in ['year', 'quarter', 'month']:
        timeframe = 'quarter'

    fig, ax1 = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor('#f0f0f0')
    ax1.set_facecolor('#0d1b2a')
    ax2 = ax1.twinx() if len(selected_metrics) > 1 else None

    for i, label in enumerate(selected_metrics):
        column_name = metrics[label]
        query = f"""
            SELECT DATE_TRUNC('{timeframe}', "Date") AS "Date", AVG("{column_name}")
            FROM real_econ_data
            GROUP BY DATE_TRUNC('{timeframe}', "Date")
            ORDER BY DATE_TRUNC('{timeframe}', "Date")
        """

        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

        if not rows or len(rows[0]) < 2:
            continue

        df = pd.DataFrame(rows, columns=["Date", "Value"])
        if df.empty:
            continue

        min_y = float(df["Value"].min()) * 0.9
        max_y = float(df["Value"].max()) * 1.1
        color = ['#219ebc', '#fb8500'][i % 2]
        
        x = pd.to_datetime(df["Date"]).map(pd.Timestamp.toordinal).to_numpy()
        y = df["Value"].to_numpy()

        if len(x) < 4:            
            continue

        x_smooth = np.linspace(x.min(), x.max(), 300)
        spl = make_interp_spline(x, y, k=1)
        y_smooth = spl(x_smooth)
        x_smooth_dates = [pd.Timestamp.fromordinal(int(val)) for val in x_smooth]

        if i == 0:
            ax1.plot(x_smooth_dates, y_smooth, linewidth=1, color=color, label=label)
            ax1.set_ylabel(label, color=color)
            ax1.tick_params(axis='y', labelcolor=color)
            ax1.set_ylim([min_y, max_y])
        elif ax2:
            ax2.plot(x_smooth_dates, y_smooth, linewidth=1, color=color, label=label)
            ax2.set_ylabel(label, color=color)
            ax2.tick_params(axis='y', labelcolor=color)
            ax2.set_ylim([min_y, max_y])

    ax1.tick_params(axis='x', labelsize=6, color='white')
    ax1.tick_params(axis='y', labelsize=6)
    if ax2:
        ax2.tick_params(axis='y', labelsize=6)

    ax1.set_title("Dual Metric Comparison" if len(selected_metrics) > 1 else selected_metrics[0], fontsize=10, color='white')
    ax1.xaxis.set_tick_params(rotation=30)
    fig.patch.set_facecolor('#0d1b2a')
    
    ax1.grid(True, which='major', color='#EAEFEF', linewidth=0.1)
    if ax2:
        ax2.grid(False) 

    for label in ax1.get_xticklabels():
        label.set_color('white') 
    
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=200, facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


#  Render small individual chart 
def render_mini_chart(metric_label, column_name):
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT DATE_TRUNC('month', "Date") AS "Date", AVG("{column_name}") 
            FROM real_econ_data 
            GROUP BY DATE_TRUNC('month', "Date") 
            ORDER BY DATE_TRUNC('month', "Date")
        """)
        rows = cursor.fetchall()
        if not rows:
            return None
        df = pd.DataFrame(rows, columns=["Date", "Value"])
        fig, ax = plt.subplots(figsize=(4, 2))
        fig.patch.set_facecolor('#f0f0f0')
        ax.set_facecolor('#0d1b2a')
        ax.plot(df["Date"], df["Value"], color='#e0e1dd', linewidth=0.2)        
        ax.tick_params(axis='x', labelsize=6)
        ax.tick_params(axis='y', labelsize=6)        
        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100)
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode('utf-8')


#  Calculate year-over-year percent changes 
def calculate_percent_changes(year):
    values = []
    allowed_columns = set(metrics.values())

    with connection.cursor() as cursor:
        for label, column in metrics.items():
            if column not in allowed_columns:
                raise ValueError(f"Invalid column name: {column}")

            sql = """
                SELECT
                    EXTRACT(MONTH FROM "Date") AS month,
                    AVG("{col}") AS avg_value
                FROM real_econ_data
                WHERE "Date" BETWEEN '{year}-01-01' AND '{year}-12-31'
                  AND EXTRACT(MONTH FROM "Date") IN (1, 12)
                GROUP BY month
                ORDER BY month;
            """.format(col=column, year=year)

            try:
                cursor.execute(sql)
                rows = cursor.fetchall()

                if len(rows) < 2:
                    values.append(0)
                    continue
                
                rows.sort(key=lambda x: x[0])
                jan_value = rows[0][1]
                dec_value = rows[1][1]

                if jan_value is None or dec_value is None:
                    values.append(0)
                    continue

                avg = (jan_value + dec_value) / 2
                if avg == 0:
                    values.append(0)
                    continue

                pct_change = ((dec_value - jan_value) / avg) * 100
                values.append(pct_change)

            except Exception as e:
                print(f"Error processing {column}: {e}")
                values.append(0)

    return values


#  Render radar chart 
def render_radar_chart(values, labels, year):
    num_vars = len(values)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(4, 3), subplot_kw=dict(polar=True))
    ax.plot(angles, values, color='#7b2cbf', linewidth=1)
    ax.fill(angles, values, color='#c77dff', alpha=0.25)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_title(f"Year-over-Year % Change: {year}", fontsize=10)

    buf = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format='png', dpi=200)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


#  Home view 
def home(request):
    charts = []
    for label, column in metrics.items():
        chart_img = render_mini_chart(label, column)
        if chart_img:
            charts.append({'label': label, 'img': chart_img})

    with connection.cursor() as cursor:
        cursor.execute('SELECT MIN("Date"), MAX("Date") FROM real_econ_data')
        start_date, end_date = cursor.fetchone()
    start_year = start_date.year
    end_year = end_date.year
    
    if end_date.month < 12:
        valid_years = list(range(start_year, end_year))
    else:
        valid_years = list(range(start_year, end_year + 1))

    default_metrics = ["GDP Growth Rate", "Unemployment Rate"]
    combined_chart_img = render_combined_chart(default_metrics)
    default_year = valid_years[-1] 
    values = calculate_percent_changes(default_year)
    radar_img = render_radar_chart(values, list(metrics.keys()), default_year)

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM annual_economic_summary ORDER BY year;")
        rows = cursor.fetchall()
        raw_columns = [col[0] for col in cursor.description]

    friendly_column_names = {
        'year': 'Year',
        'avg_gdp_growth': 'Avg GDP Growth (%)',
        'avg_inflation': 'Avg Inflation (%)',
        'avg_unemployment': 'Avg Unemployment Rate (%)',
        'avg_interest_rate': 'Avg Interest Rate (%)',
        'avg_confidence': 'Avg Consumer Confidence',    
    }
    
    columns = [friendly_column_names.get(col, col) for col in raw_columns]

    return render(request, 'index.html', {
        'radar_img': radar_img,
        'charts': charts,
        'years': valid_years,
        'default_year': default_year, 
        'combined_chart_img': combined_chart_img,
        'default_metrics': default_metrics,
        'metrics': metrics,
        'summary_headers': columns,
        'summary_rows': rows
    })


#  API view: radar data 
def get_radar_data(request):
    year = int(request.GET.get('year'))
    values = calculate_percent_changes(year)
    radar_img = render_radar_chart(values, list(metrics.keys()), year)
    return JsonResponse({'img': radar_img})


#  API view: combined chart 
@csrf_exempt
def combined_chart_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_metrics = data.get('metrics', [])
        timeframe = data.get('timeframe', 'quarter')
        chart_img = render_combined_chart(selected_metrics, timeframe)
        return JsonResponse({'chart': chart_img})


#  Legacy update endpoint 
def update_combined_chart(request):
    metrics = request.GET.get('metrics', '')
    metric_list = metrics.split(',') if metrics else []
    img = render_combined_chart(metric_list)
    return JsonResponse({'img': img})
