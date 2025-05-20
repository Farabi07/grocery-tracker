from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from datetime import datetime
from .models import Report
from receipts.models import Transaction, ExpenseCategory
from django.utils import timezone
from authentication.permissions import IsAdmin


def calculate_profit_for_month(start_date, end_date):
    income = Transaction.objects.filter(
        type='income',
        receipt__date__gte=start_date,
        receipt__date__lt=end_date
    ).aggregate(Sum('price'))['price__sum'] or 0

    expenses = Transaction.objects.filter(
        type='expense',
        receipt__date__gte=start_date,
        receipt__date__lt=end_date
    ).aggregate(Sum('price'))['price__sum'] or 0

    return income - expenses


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def monthly_report_view(request, year, month):
    # Validate year and month inputs
    try:
        year = int(year)
        month = int(month)
        start_date = datetime(year, month, 1)
    except ValueError:
        return Response({"error": "Invalid year or month"}, status=status.HTTP_400_BAD_REQUEST)

    # Calculate last day of the month properly
    from calendar import monthrange
    last_day = monthrange(year, month)[1]
    end_date = datetime(year, month, last_day, 23, 59, 59)

    transactions = Transaction.objects.filter(
        receipt__date__gte=start_date,
        receipt__date__lte=end_date
    )

    spending_by_category = {}
    for category in ExpenseCategory.objects.all():
        total_spent = transactions.filter(category=category).aggregate(Sum('price'))['price__sum'] or 0
        spending_by_category[category.name] = total_spent

        # Update or create the Report entry
        report, created = Report.objects.get_or_create(
            user=request.user,
            month=start_date.date(),
            category=category,
            defaults={'total_spent': total_spent}
        )
        if not created:
            report.total_spent = total_spent
            report.save()

    return Response({'spending_by_category': spending_by_category}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def monthly_statistics_view(request):
    now = timezone.now()
    current_year = now.year

    monthly_data = []
    for month in range(1, 13):
        start_date = datetime(current_year, month, 1)
        if month == 12:
            end_date = datetime(current_year + 1, 1, 1)
        else:
            end_date = datetime(current_year, month + 1, 1)

        transactions = Transaction.objects.filter(
            receipt__date__gte=start_date,
            receipt__date__lt=end_date
        )

        expenditure = transactions.aggregate(Sum('price'))['price__sum'] or 0
        profit = calculate_profit_for_month(start_date, end_date)

        monthly_data.append({
            'month': start_date.strftime('%b'),
            'expenditure': expenditure,
            'profit': profit
        })

    return Response(monthly_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_orders_view(request):
    recent_transactions = Transaction.objects.select_related('category').order_by('-receipt__date')[:10]
    data = [
        {
            'date': txn.receipt.date.strftime('%Y-%m-%d'),
            'product': txn.item_name,  # Fixed from 'description' to 'item_name'
            'category': txn.category.name,
            'amount': txn.price
        }
        for txn in recent_transactions
    ]
    return Response(data)
