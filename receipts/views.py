from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import requests
from django.conf import settings
from .models import ExpenseCategory, Receipt, Transaction
from authentication.permissions import IsEmployee

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsEmployee])
@parser_classes([MultiPartParser, FormParser])
def receipt_scan_view(request):
    # Check if file is in request
    if 'receipt' not in request.FILES:
        return Response({"message": "Receipt file is missing"}, status=status.HTTP_400_BAD_REQUEST)

    file = request.FILES['receipt']
    files = {'receipt': file}

    # OCR service URL from settings
    ocr_service_url = settings.OCR_SERVICE_URL

    try:
        # Send receipt to OCR service
        response = requests.post(ocr_service_url, files=files)
    except requests.RequestException as e:
        return Response({"message": f"Error connecting to OCR service: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Process OCR response
    if response.status_code == 200:
        ocr_data = response.json()

        if ocr_data.get('status') == 'success':
            # Create the Receipt once here, using total_cost from OCR data
            total_cost = ocr_data.get('total_cost', 0.0)
            receipt = Receipt.objects.create(
                user=request.user,
                image=file,
                total_amount=total_cost
            )

            for item in ocr_data.get('items', []):
                category_name = item.get('category', 'Unknown')
                price = item.get('total_price', 0.0)  # Use total_price instead of price if available
                item_name = item.get('name', 'Unknown')

                # Get or create category
                category, _ = ExpenseCategory.objects.get_or_create(name=category_name)

                # Create transaction linked to the single receipt
                Transaction.objects.create(
                    receipt=receipt,
                    category=category,
                    item_name=item_name,
                    price=price
                )

            return Response({"message": "Receipt processed successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Error processing receipt data from OCR"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message": "OCR service returned an error"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
