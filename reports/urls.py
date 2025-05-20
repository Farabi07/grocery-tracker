from django.urls import path
from .views import monthly_report_view, monthly_statistics_view, recent_orders_view

urlpatterns = [
    path('reports/monthly/<int:year>/<int:month>/', monthly_report_view, name='monthly-report'),
    path('reports/statistics/', monthly_statistics_view, name='monthly-statistics'),
    path('orders/recent/', recent_orders_view, name='recent-orders'),
]
