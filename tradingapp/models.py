from django.contrib.auth.models import User
from django.db import models

class CryptoHolding(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=20, decimal_places=8)

    def __str__(self):
        return f"{self.user.username} - {self.symbol}: {self.amount}"

class VirtualBalance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    usdc_balance = models.DecimalField(max_digits=12, decimal_places=2, default=10000)

    def __str__(self):
        return f"{self.user.username} - Balance: ${self.usdc_balance}"


class PortfolioBalance(models.Model):
    balance = models.FloatField(default=0.0)

    def __str__(self):
        return f"Balance: ${self.balance}"



