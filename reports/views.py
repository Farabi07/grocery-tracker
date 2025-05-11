from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from datetime import datetime
from .models import Report
from receipts.models import Transaction, ExpenseCategory
from django.utils import timezone
from accounts.permissions import IsAdmin
from rest_framework.permissions import IsAuthenticated

class MonthlyReportView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]  # Only Admins can view the reports

    def get(self, request, year, month):
        # Fetch the date range for the requested month
        start_date = f"{year}-{month}-01"
        end_date = f"{year}-{month}-31"  # For simplicity, we assume 31 days in the month

        # Get all transactions for the specified month
        transactions = Transaction.objects.filter(
            receipt__date__gte=start_date, 
            receipt__date__lte=end_date
        )

        # Calculate total spending by category
        spending_by_category = {}
        for category in ExpenseCategory.objects.all():
            total_spent = transactions.filter(category=category).aggregate(Sum('price'))['price__sum']
            if total_spent:
                spending_by_category[category.name] = total_spent
            else:
                spending_by_category[category.name] = 0

        # Optionally, create or update the report in the database
        for category, total_spent in spending_by_category.items():
            category_obj = ExpenseCategory.objects.get(name=category)
            report, created = Report.objects.get_or_create(
                user=request.user, 
                month=start_date, 
                category=category_obj,
                defaults={'total_spent': total_spent}
            )
            if not created:
                report.total_spent = total_spent
                report.save()

        return Response({
            'spending_by_category': spending_by_category
        }, status=status.HTTP_200_OK)
