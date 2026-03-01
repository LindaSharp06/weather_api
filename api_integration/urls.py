from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('get_exchange_rate/', views.get_exchange_rate_view, name='get_exchange_rate'),
    path('exchange_history/', views.exchange_history_view, name='exchange_history'),
]