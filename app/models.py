from django.db import models


class EconData(models.Model):
    date = models.DateTimeField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    stock_index = models.TextField(db_column='Stock Index', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    open_price = models.DecimalField(db_column='Open Price', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    close_price = models.DecimalField(db_column='Close Price', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    daily_high = models.DecimalField(db_column='Daily High', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    daily_low = models.DecimalField(db_column='Daily Low', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    trading_volume = models.IntegerField(db_column='Trading Volume', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    gdp_growth_field = models.DecimalField(db_column='GDP Growth (%)', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    inflation_rate_field = models.DecimalField(db_column='Inflation Rate (%)', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    unemployment_rate_field = models.DecimalField(db_column='Unemployment Rate (%)', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    interest_rate_field = models.DecimalField(db_column='Interest Rate (%)', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    consumer_confidence_index = models.IntegerField(db_column='Consumer Confidence Index', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    government_debt_billion_usd_field = models.IntegerField(db_column='Government Debt (Billion USD)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    corporate_profits_billion_usd_field = models.IntegerField(db_column='Corporate Profits (Billion USD)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    forex_usd_eur = models.DecimalField(db_column='Forex USD/EUR', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    forex_usd_jpy = models.DecimalField(db_column='Forex USD/JPY', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    crude_oil_price_usd_per_barrel_field = models.DecimalField(db_column='Crude Oil Price (USD per Barrel)', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    gold_price_usd_per_ounce_field = models.DecimalField(db_column='Gold Price (USD per Ounce)', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    real_estate_index = models.DecimalField(db_column='Real Estate Index', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    retail_sales_billion_usd_field = models.IntegerField(db_column='Retail Sales (Billion USD)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    bankruptcy_rate_field = models.DecimalField(db_column='Bankruptcy Rate (%)', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    mergers_acquisitions_deals = models.IntegerField(db_column='Mergers & Acquisitions Deals', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    venture_capital_funding_billion_usd_field = models.DecimalField(db_column='Venture Capital Funding (Billion USD)', max_digits=65535, decimal_places=65535, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    consumer_spending_billion_usd_field = models.IntegerField(db_column='Consumer Spending (Billion USD)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.

    class Meta:
        managed = False
        db_table = 'real_econ_data'
