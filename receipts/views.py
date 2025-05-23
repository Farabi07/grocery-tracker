from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Receipt, Transaction, ExpenseCategory
from authentication.permissions import IsEmployee
from django.conf import settings
from django.utils import timezone
import requests
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import Receipt, Transaction, ExpenseCategory
from authentication.permissions import IsEmployee
from reports.models import Report
import json
from core.views import extract_text_from_local_image, categorize_receipt_with_gpt
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['POST'])
# @permission_classes([IsAuthenticated, IsEmployee])
@parser_classes([MultiPartParser, FormParser])
def receipt_scan_view(request):
    if 'receipt' not in request.FILES:
        return Response({"message": "Receipt file is missing"}, status=status.HTTP_400_BAD_REQUEST)

    file = request.FILES['receipt']

    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
        for chunk in file.chunks():
            temp_file.write(chunk)
        temp_path = temp_file.name

    try:
        extracted_text = extract_text_from_local_image(temp_path)
        json_output = categorize_receipt_with_gpt(extracted_text)
        ocr_data = json.loads(json_output)
    except Exception as e:
        return Response({"message": f"OCR processing error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if not ocr_data:
        return Response({"message": "Error processing receipt data"}, status=status.HTTP_400_BAD_REQUEST)

    total_cost = ocr_data.get('total_cost', 0.0)
    items = ocr_data.get('items', [])

    try:
        with transaction.atomic():
            receipt = Receipt.objects.create(user=request.user, image=file, total_amount=total_cost)
            category_totals = {}

            for item in items:
                category_name = item.get('category', 'Unknown').capitalize()
                price = item.get('total_price', 0.0)
                item_name = item.get('name', 'Unknown')

                category, _ = ExpenseCategory.objects.get_or_create(name=category_name)
                Transaction.objects.create(
                    receipt=receipt,
                    category=category,
                    item_name=item_name,
                    price=price
                )
                category_totals[category] = category_totals.get(category, 0) + price

            # Update or create report entries per category for the current month
            month_start = timezone.now().date().replace(day=1)
            for category, total_spent in category_totals.items():
                report, created = Report.objects.get_or_create(
                    user=request.user,
                    month=month_start,
                    category=category,
                    defaults={
                        'total_spent': total_spent,
                        'created_by': request.user,
                        'updated_by': request.user
                    }
                )
                if not created:
                    from django.db.models import F
                    report.total_spent = F('total_spent') + total_spent
                    report.updated_by = request.user
                    report.save()
    except Exception as e:
        return Response({"message": "Database error: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"message": "Receipt processed successfully"}, status=status.HTTP_201_CREATED)
