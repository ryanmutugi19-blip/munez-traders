from urllib.parse import urlsplit

from django.conf import settings
from django.shortcuts import render, redirect
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required

from .models import TradingAccount, Trade, Watchlist
from django.contrib import messages
from django.shortcuts import render



@login_required
def home(request):
    accounts = TradingAccount.objects.filter(user=request.user)
    trades = Trade.objects.filter(
        user=request.user
    ).order_by('-created_at')
    watchlist = Watchlist.objects.filter(
        user=request.user
    ).order_by('-added_at')
    demo_markets = [
        {
            'symbol': 'EUR/USD',
            'price': '1.0845',
            'change': '+0.25%',
            'direction': 'up',
        },
        {
            'symbol': 'GBP/USD',
            'price': '1.2710',
            'change': '-0.18%',
            'direction': 'down',
        },
        {
            'symbol': 'USD/JPY',
            'price': '149.50',
            'change': '+0.12%',
            'direction': 'up',
        },
        {
            'symbol': 'GOLD',
            'price': '2,350.00',
            'change': '+0.40%',
            'direction': 'up',
        },
    ]

    context = {
        'accounts': accounts,
        'trades': trades,
        'watchlist': watchlist,
        'total_trades': trades.count(),
        'open_trades': trades.filter(status='open').count(),
        'connected_accounts': accounts.filter(
            is_connected=True
        ).count(),
        'demo_markets': demo_markets,
        'affiliate_enabled': bool(settings.DERIV_AFFILIATE_URL),
        'deriv_app_id': settings.DERIV_APP_ID,
    }

    return render(request, 'index.html', context)

@login_required
def add_watchlist(request):
    if request.method != 'POST':
        return redirect('home')

    symbol = request.POST.get('symbol', '').strip().upper()

    if not symbol:
        messages.error(request, 'Please enter a symbol.')
        return redirect('home')

    if len(symbol) > 30:
        messages.error(request, 'The symbol must be 30 characters or fewer.')
        return redirect('home')

    if not all(char.isalnum() or char in '._-' for char in symbol):
        messages.error(
            request,
            'Use only letters, numbers, dots, underscores, or hyphens.'
        )
        return redirect('home')

    item, created = Watchlist.objects.get_or_create(
        user=request.user,
        symbol=symbol
    )

    if created:
        messages.success(request, f'{symbol} added to your watchlist.')
    else:
        messages.warning(request, f'{symbol} is already in your watchlist.')

    return redirect('home')

@login_required
def remove_watchlist(request, item_id):
    if request.method != 'POST':
        return redirect('home')

    item = Watchlist.objects.filter(
        id=item_id,
        user=request.user
    ).first()

    if item:
        symbol = item.symbol
        item.delete()
        messages.success(
            request,
            f'{symbol} removed from your watchlist.'
        )
    else:
        messages.error(
            request,
            'Watchlist item not found.'
        )

    return redirect('home')


def register_page(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {
        'form': form,
        'affiliate_enabled': bool(settings.DERIV_AFFILIATE_URL),
    })


def login_page(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {
        'form': form,
        'affiliate_enabled': bool(settings.DERIV_AFFILIATE_URL),
    })


@login_required
def history_page(request):
    trades = Trade.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(request, 'history.html', {'trades': trades})


@login_required
def strategies_page(request):
    return render(request, 'strategies.html')


@login_required
def logout_page(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')

    return redirect('home')

@login_required
def deriv_market_page(request):
    return render(request, 'deriv_market.html', {
        'deriv_app_id': settings.DERIV_APP_ID,
        'affiliate_enabled': bool(settings.DERIV_AFFILIATE_URL),
    })


def deriv_signup(request):
    affiliate_url = settings.DERIV_AFFILIATE_URL
    if not affiliate_url:
        return HttpResponse(
            'Deriv partner signup is not configured yet.',
            status=503,
        )

    parsed_url = urlsplit(affiliate_url)
    hostname = parsed_url.hostname or ''
    if (
        parsed_url.scheme != 'https'
        or not (
            hostname == 'deriv.com'
            or hostname.endswith('.deriv.com')
        )
        or parsed_url.username
        or parsed_url.password
    ):
        raise ImproperlyConfigured(
            'DERIV_AFFILIATE_URL must be an HTTPS Deriv partner URL.'
        )

    return redirect(affiliate_url)

@login_required
def settings_page(request):
    defaults = {
        'preferred_market': 'EUR/USD',
        'chart_timeframe': '1h',
        'notifications': True,
        'confirm_trades': True,
    }

    saved_settings = request.session.get('trading_settings', {})
    settings = {**defaults, **saved_settings}

    if request.method == 'POST':
        preferred_market = request.POST.get(
            'preferred_market', 'EUR/USD'
        )
        chart_timeframe = request.POST.get('chart_timeframe', '1h')

        allowed_markets = [
            'EUR/USD', 'GBP/USD', 'USD/JPY', 'GOLD'
        ]
        allowed_timeframes = [
            '1m', '5m', '15m', '1h', '4h', '1d'
        ]

        if (
            preferred_market not in allowed_markets
            or chart_timeframe not in allowed_timeframes
        ):
            messages.error(request, 'Please select valid settings.')
        else:
            settings = {
                'preferred_market': preferred_market,
                'chart_timeframe': chart_timeframe,
                'notifications': request.POST.get('notifications') == 'on',
                'confirm_trades': request.POST.get('confirm_trades') == 'on',
            }

            request.session['trading_settings'] = settings
            messages.success(request, 'Your settings have been saved.')

        return redirect('settings')

    context = {
        'settings': settings,
        'username': request.user.username,
        'email': request.user.email,
    }

    return render(request, 'settings.html', context)

@login_required
def markets_page(request):
    demo_markets = [
        {'symbol': 'EUR/USD', 'price': '1.0845', 'change': '+0.25%', 'direction': 'up'},
        {'symbol': 'GBP/USD', 'price': '1.2710', 'change': '-0.18%', 'direction': 'down'},
        {'symbol': 'USD/JPY', 'price': '149.50', 'change': '+0.12%', 'direction': 'up'},
        {'symbol': 'GOLD', 'price': '2,350.00', 'change': '+0.40%', 'direction': 'up'},
    ]

    return render(request, 'markets.html', {
        'demo_markets': demo_markets,
    })

def intro_page(request):
    return render(request, 'intro.html')
def entry_page(request):
    return render(request, 'intro.html')