from django.db import models
from django.contrib.auth.models import User


class TradingAccount(models.Model):
    PROVIDERS = [
        ("deriv", "Deriv"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="trading_accounts"
    )
    provider = models.CharField(
        max_length=30,
        choices=PROVIDERS,
        default="deriv"
    )
    external_account_id = models.CharField(
        max_length=100,
        blank=True
    )
    is_connected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.provider}"


class Trade(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("open", "Open"),
        ("closed", "Closed"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="trades"
    )
    symbol = models.CharField(max_length=30)
    trade_type = models.CharField(max_length=10)
    stake = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.symbol} - {self.status}"


class Watchlist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="watchlist"
    )
    symbol = models.CharField(max_length=30)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "symbol"],
                name="unique_user_watchlist_symbol"
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.symbol}"
