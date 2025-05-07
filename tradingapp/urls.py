from django.urls import path
from tradingapp import tradingapp_views


app_name='tradingapp'
urlpatterns = [
    path('', tradingapp_views.index_2, name="index"),
    path('index-2/',tradingapp_views.index_2,name="index-2"),
    path('market/',tradingapp_views.market,name="market"),
    path('coin-details/',tradingapp_views.coin_details,name="coin-details"),
    path('api/candlestick/<str:symbol>/', tradingapp_views.candlestick_data, name='candlestick-data'),
    path('api/bar-chart/', tradingapp_views.coinmarketcap_bar_data, name='bar_chart_data'),
    path('coinmarketcap-bar-data/', tradingapp_views.coinmarketcap_bar_data, name="coinmarketcap_bar_data"),
    path('api/buy/', tradingapp_views.buy_crypto, name='buy_crypto'),
    path('deposit/', tradingapp_views.deposit_funds, name='deposit_funds'),
    path("buy-btc/", tradingapp_views.buy_btc, name="buy_btc"),
    path('api/get-balance/', tradingapp_views.get_user_balance, name='get_user_balance'),
    path("sell-btc/", tradingapp_views.sell_btc, name="sell_btc"),
    path('future/',tradingapp_views.future,name="future"),






    path('page-login/',tradingapp_views.page_login,name="page-login"),
    path('page-register/',tradingapp_views.page_register,name="page-register"),
    path('logout/', tradingapp_views.user_logout, name='logout'),

    path('page-error-404/',tradingapp_views.page_error_404,name="page-error-404"),


]
