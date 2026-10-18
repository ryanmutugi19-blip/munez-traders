from django.urls import path
from . import views

urlpatterns = [
    # Website opening animation
    path('', views.entry_page, name='home'),

    # Main website pages
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('history/', views.history_page, name='history'),
    path('strategies/', views.strategies_page, name='strategies'),
    path('logout/', views.logout_page, name='logout'),

    # Watchlist
    path('watchlist/add/', views.add_watchlist, name='add_watchlist'),
    path(
        'watchlist/remove/<int:item_id>/',
        views.remove_watchlist,
        name='remove_watchlist',
    ),

    # Deriv integration
    path('deriv-market/', views.deriv_market_page, name='deriv_market'),
    path('deriv-signup/', views.deriv_signup, name='deriv_signup'),

    # Markets and settings
    path('markets/', views.markets_page, name='markets'),
    path('settings/', views.settings_page, name='settings'),

    # Direct access to the intro
    path('intro/', views.intro_page, name='intro'),
]