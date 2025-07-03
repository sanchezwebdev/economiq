# EconomIQ

**EconomIQ** is a data analytics dashboard built with Python, Django, and PostgreSQL. It visualizes key economic indicators using filterable, interactive charts—designed to demonstrate full-stack application development and data analysis skills.

## 📊 Features

- Realistic economic data modeled on real-world indicators
- Custom filterable charts with Matplotlib and mplfinance
- Interactive visualizations: GDP, inflation, unemployment, interest rates, market signals, commodities, and more
- Investment signals and macroeconomic radar charts
- Dynamic chart updates without page refresh using JavaScript
- Responsive layout with Bootstrap + custom CSS

## 🛠️ Tech Stack

- Python · Django · PostgreSQL · Supabase
- psycopg2 · pandas · numpy · sklearn
- matplotlib · mplfinance
- Bootstrap + Custom CSS
- Hosted on Heroku

## 📁 Data

Data is AI-generated and closely modeled after real-world economic data sources. Stored in a PostgreSQL database hosted on Supabase, it includes:

- GDP Growth (%)
- Inflation Rate (%)
- Unemployment Rate (%)
- Interest Rate (%)
- Consumer Confidence Index
- usd/eur and usd/jpy exchange rates
- Crude oil and gold prices
- VC funding volume, M&A deals
- Corporate profits, consumer spending, retail sales
- Bankruptcy rates, economic composition

## 📈 Dashboard Views

- **Landing Page** – Compare key indicators with a dual-metric chart and economic radar graph
- **Market Analysis** – Choose a market (Dow Jones, NASDAQ, S&P500) and chart options (VWAP, EMA, SMA, regression)
- **Economic Composition** – View a normalized stacked area chart showing economic dynamics over time
- **Investment Signals** – Evaluate market conditions with investment climate and commodity price charts

## 🚀 Getting Started

```bash
git clone https://github.com/YOUR_USERNAME/economiq.git
cd economiq
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
