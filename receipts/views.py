import requests
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .models import Receipt, Transaction, ExpenseCategory
from django.conf import settings  # To get the OCR service URL from settings

class ReceiptScanView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        # Receive the uploaded receipt image
        file = request.FILES['receipt']

        # Prepare the file for sending to the AI OCR service
        files = {'receipt': file}

        # The URL of the OCR service (use a demo API for this purpose)
        ocr_service_url = settings.OCR_SERVICE_URL  # Use an environment variable or settings for the URL

        # Send the image to the OCR service
        response = requests.post(ocr_service_url, files=files)

        if response.status_code == 200:
            # The AI service returned structured data (example JSON structure)
            ocr_data = response.json()

            if ocr_data['status'] == 'success':
                # Process the returned items from OCR
                for item in ocr_data['items']:
                    category_name = item.get('category', 'Unknown')
                    price = item.get('price', 0.0)
                    item_name = item.get('name', 'Unknown')

                    # Find or create the category
                    category, created = ExpenseCategory.objects.get_or_create(name=category_name)

                    # Create the receipt entry in the database
                    receipt = Receipt.objects.create(user=request.user, image=file, total_amount=price)

                    # Create the transaction entry for the item
                    Transaction.objects.create(
                        receipt=receipt,
                        category=category,
                        item_name=item_name,
                        price=price
                    )

                return Response({"message": "Receipt processed successfully"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Error processing receipt"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Error connecting to OCR service"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
