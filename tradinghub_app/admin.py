from django.contrib import admin
from .models import TradingAccount, Trade, Watchlist


@admin.register(TradingAccount)
class TradingAccountAdmin(admin.ModelAdmin):
    list_display = ("user", "provider", "external_account_id", "is_connected", "created_at")
    list_filter = ("provider", "is_connected")
    search_fields = ("user__username", "external_account_id")


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ("user", "symbol", "trade_type", "stake", "status", "created_at")
    list_filter = ("status", "trade_type")
    search_fields = ("user__username", "symbol")


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("user", "symbol", "added_at")
    search_fields = ("user__username", "symbol")