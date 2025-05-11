from django.db import models

# Create your models here.
from django.db import models
from accounts.models import CustomUser
from receipts.models import ExpenseCategory

class Report(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField()  # Stores the month of the report (e.g., "2025-05-01")
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)

    def __str__(self):
        return f"Report for {self.user.username} - {self.month}"

