from django.contrib import admin
from .models import *

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
	list_display = [field.name for field in ExpenseCategory._meta.fields]
	
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
	list_display = [field.name for field in Transaction._meta.fields]
	
@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
	list_display = [field.name for field in Receipt._meta.fields]