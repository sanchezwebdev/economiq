

---

**EconomIQ – Economic Data Analytics Dashboard**

EconomIQ is a full-stack economic data analytics dashboard built to showcase my skills in backend development, data modeling, and real-time data visualization. This project simulates a professional-grade analytics tool that could be used by economists, financial analysts, or business stakeholders to derive insights from macroeconomic indicators. While designed primarily as a portfolio piece, it mirrors real-world functionality and demonstrates the ability to deliver a cohesive application from backend to frontend.

The app is powered by Django and PostgreSQL, with the database hosted on Supabase. The dataset includes realistic economic metrics such as GDP growth, inflation, unemployment, interest rates, consumer confidence, exchange rates (USD/EUR, USD/JPY), commodity prices (gold, crude oil), bankruptcy rates, corporate profits, venture capital funding, M\&A deals, and more. Although the data was generated using OpenAI, it was crafted to closely resemble real historical economic data in structure, trends, and relationships.

Django models were auto-generated using `inspectdb` to reflect the Supabase schema. The application queries data using `psycopg2`, and applies Python tools like pandas, numpy, sklearn, matplotlib, and mplfinance to process, analyze, and visualize the results. The frontend was built using a mix of custom CSS and Bootstrap, and deployed on Heroku at economiq.gerardosanchez.dev.

The dashboard includes several distinct views:

* The **landing page** offers an overview of economic performance, where users can select and compare two key indicators (like GDP vs. inflation) over various timeframes (monthly, quarterly, yearly). A radar chart visualizes year-over-year shifts in multiple indicators.
* The **market analysis page** lets users explore stock market trends by selecting from Dow Jones, NASDAQ, or S\&P 500, with optional overlays like VWAP, EMA, SMA, and linear regression.
* The **economic composition page** features a normalized stacked area chart showing the relative contributions of GDP growth, inflation, unemployment, and interest rates over time.
* The **investment signals page** visualizes market conditions using VC funding volume, corporate profits, currency exchange rates, and commodity prices to assess the economic climate.

One of the biggest challenges in this project was sourcing usable economic data. Many publicly available datasets were outdated, incomplete, or inconsistent. I resolved this by using OpenAI to generate realistic, coherent economic data, ensuring that the visualizations could still provide meaningful insights without relying on fragile sources. The final dataset is structured and consistent enough to demonstrate the kind of analysis one would perform on real-world data.

Another point of pride is the interactivity layer. Users can filter and update charts dynamically without triggering page reloads, which improves the overall user experience. This was achieved using vanilla JavaScript instead of AJAX or React, ensuring performance without added complexity.

EconomIQ demonstrates a wide range of technical capabilities: relational database modeling, data querying, statistical analysis, financial charting, responsive UI design, and full deployment. While the visual design is clean and functional, the standout element is the data analytics engine that drives the application’s insights.

This project is a testament to my ability to take an idea from data modeling to finished product, integrating multiple tools and technologies to deliver an engaging and functional analytics platform.

You can explore the live project at **economiq.gerardosanchez.dev**, and the full source code is available on GitHub.
