from rest_framework import serializers
from .models import Receipt, Transaction, ExpenseCategory

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class ReceiptSerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True)

    class Meta:
        model = Receipt
        fields = ['user', 'image', 'total_amount', 'date', 'transactions']
