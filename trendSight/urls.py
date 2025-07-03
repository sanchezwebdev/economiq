from django.contrib import admin
from django.urls import path, include
from app.views.home import home, get_radar_data, combined_chart_view, update_combined_chart
from app.views.market_analysis import market_analysis
from app.views.macro_composition import macro_composition
from app.views.investment_signals import investment_signals


urlpatterns = [
    # path("__reload__/", include("django_browser_reload.urls")),
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('market-analysis', market_analysis, name='market_analysis'),
    path('macro-composition', macro_composition, name='macro_composition'),
    path('investment-signals', investment_signals, name='investment_signals'),
    path('', home, name='home'),
    path('', home, name='home'),
    path('get-radar-data', get_radar_data, name='get_radar_data'), 
    path('get-combined-chart', combined_chart_view, name='combined_chart_view'), 
    path('update-combined-chart', update_combined_chart, name='update_combined_chart'), 
]
