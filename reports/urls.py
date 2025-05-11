from django.urls import path
from .views import MonthlyReportView

urlpatterns = [
    path('monthly/<int:year>/<int:month>/', MonthlyReportView.as_view(), name='monthly-report'),
]
