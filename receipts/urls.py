from django.urls import path
from .views import receipt_scan_view

urlpatterns = [
    path('scan-receipt/', receipt_scan_view),
]