from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("charts/sector.png", views.chart_sector, name="chart_sector"),
    path("charts/country.png", views.chart_country, name="chart_country"),
    path("charts/daily.png", views.chart_daily, name="chart_daily"),
    path("api/tenders/", views.api_tenders, name="api_tenders"),
]
