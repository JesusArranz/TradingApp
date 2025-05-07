from datetime import datetime

import pandas as pd
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from decimal import Decimal, InvalidOperation
from tradingapp.models import CryptoHolding, VirtualBalance, PortfolioBalance
from tradingapp.services import get_top_cryptos, get_specific_cryptos, get_candlestick_data, get_coinmarketcap_ohlcv, \
     get_coin_price_usdc
import requests
from django.core.cache import cache
import json
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect

@login_required
def dashboard(request):
    # 1. Obtener la lista de criptos (últimos datos de mercado)
    url_listings = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    headers = {
        "X-CMC_PRO_API_KEY": "TU_API_KEY",  # ← reemplaza esto por tu API real
    }
    params = {
        "limit": 10,
        "convert": "USD"
    }

    response = requests.get(url_listings, headers=headers, params=params)
    cryptos = []
    logos = {}

    if response.status_code == 200:
        data = response.json().get("data", [])
        cryptos = data
        ids = [str(crypto["id"]) for crypto in data]

        # 2. Obtener los logos de los IDs
        url_info = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/info"
        params_info = {
            "id": ",".join(ids)
        }

        response_info = requests.get(url_info, headers=headers, params=params_info)
        if response_info.status_code == 200:
            info_data = response_info.json().get("data", {})
            logos = {id_: info_data[id_]["logo"] for id_ in info_data}

        # 3. Añadir logo a cada cripto
        for crypto in cryptos:
            crypto_id = str(crypto["id"])
            crypto["logo"] = logos.get(crypto_id, "")

    return render(request, "dashboard.html", {"cryptos": cryptos})






from decimal import Decimal
from .utils import get_portfolio_summary

@login_required
def index_2(request):
    monedas_fijas = get_specific_cryptos(["BTC", "ETH", "SOL", "ADA", "XRP", "LTC"])
    candlestick_data = get_candlestick_data("BTC")

    balance = Decimal('0')
    portfolio_value = Decimal('0')
    if request.user.is_authenticated:
        vb, _ = VirtualBalance.objects.get_or_create(user=request.user)
        balance = vb.usdc_balance
        _, total_value = get_portfolio_summary(request.user)
        portfolio_value = Decimal(str(total_value))  # Convert float to Decimal

    total_balance = balance + portfolio_value

    return render(request, 'tradingapp/index-2.html', {
        'monedas_fijas': monedas_fijas,
        'candlestick_data': candlestick_data,
        'balance_usdc': float(total_balance)  # Convertimos a float para el template
    })


@login_required
def candlestick_data(request, symbol):
    if symbol.upper() != 'BTC':
        return JsonResponse([], safe=False)

    cache_key = "candlestick_btc"
    cached_data = cache.get(cache_key)
    if cached_data:
        return JsonResponse(cached_data, safe=False)

    url = 'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=7'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        ohlc = df['price'].resample('4H').ohlc().dropna().reset_index()

        ohlcv_data = [
            {
                'timestamp': int(row['timestamp'].timestamp() * 1000),
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close']
            }
            for _, row in ohlc.iterrows()
        ]

        cache.set(cache_key, ohlcv_data, timeout=300)  # cache por 5 minutos

        return JsonResponse(ohlcv_data, safe=False)
    except Exception as e:
        print("[ERROR] CoinGecko API:", e)
        return JsonResponse([], safe=False)

@login_required
#esta vista es para Coin Details UNICAMENTE
def coin_bar_chart_data(request, coin_id):
    url = f'https://api.coingecko.com/api/v3/coins/{coin_id}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        market = data.get('market_data', {})

        return JsonResponse({
            'price': market.get('current_price', {}).get('usd', 0),
            'change24h': market.get('price_change_percentage_24h', 0),
            'volume': market.get('total_volume', {}).get('usd', 0),
            'marketCap': market.get('market_cap', {}).get('usd', 0),
            'high24h': market.get('high_24h', {}).get('usd', 0),
            'low24h': market.get('low_24h', {}).get('usd', 0),
        })
    except Exception as e:
        print("Error:", e)
        return JsonResponse({}, status=500)



@login_required
def buy_btc(request):
    if request.method == 'POST':
        user = request.user

        # Capturar valores
        amount_str = request.POST.get('amount_btc', '0').strip()
        price_str = request.POST.get('price_usdc', '0').strip()
        fee_str = request.POST.get('fee', '0').strip()
        total_str = request.POST.get('total_usdc', '0').strip()

        try:
            amount_btc = Decimal(amount_str)
            price_usdc = Decimal(price_str)
            fee = Decimal(fee_str)
            total_usdc = Decimal(total_str)
        except (InvalidOperation, TypeError):
            print("[ERROR] Datos no válidos en el formulario")
            return redirect('tradingapp:coin-details')

        if amount_btc <= 0 or price_usdc <= 0 or total_usdc <= 0:
            print("[ERROR] Valores inválidos: amount o total_usdc <= 0")
            return redirect('tradingapp:coin-details')

        balance_obj, _ = VirtualBalance.objects.get_or_create(user=user)

        if balance_obj.usdc_balance >= total_usdc:
            balance_obj.usdc_balance -= total_usdc
            balance_obj.save()

            holding, created = CryptoHolding.objects.get_or_create(
                user=user, symbol='BTC',
                defaults={'amount': amount_btc}
            )
            if not created:
                holding.amount += amount_btc
                holding.save()

            print("[SUCCESS] BTC comprado correctamente")
        else:
            print("[ERROR] Fondos insuficientes")

    return redirect('tradingapp:coin-details')



@login_required
def sell_btc(request):
    if request.method == "POST":
        user = request.user

        try:
            amount = Decimal(request.POST.get("amount_btc", "0"))
            price = Decimal(request.POST.get("price_usdc", "0"))
        except (InvalidOperation, ValueError):
            messages.error(request, "Datos inválidos.")
            return redirect("tradingapp:coin-details")

        try:
            holding = CryptoHolding.objects.get(user=user, symbol="BTC")
        except CryptoHolding.DoesNotExist:
            messages.error(request, "No tienes BTC para vender.")
            return redirect("tradingapp:coin-details")

        if amount > holding.amount:
            messages.error(request, "No tienes suficiente BTC.")
            return redirect("tradingapp:coin-details")

        total = amount * price
        fee = total * Decimal("0.01")
        total_after_fee = total - fee

        # Actualiza holdings y balance
        holding.amount -= amount
        holding.save()

        balance, _ = VirtualBalance.objects.get_or_create(user=user)
        balance.usdc_balance += total_after_fee
        balance.save()

        messages.success(request, f"Vendiste {amount:.6f} BTC por ${total_after_fee:.2f} USDC.")
        return redirect("tradingapp:coin-details")

    return redirect("tradingapp:coin-details")



@login_required
def deposit_funds(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if amount:
            try:
                amount = Decimal(amount)
                if amount > 0:
                    balance_obj, created = VirtualBalance.objects.get_or_create(user=request.user)
                    balance_obj.usdc_balance += amount
                    balance_obj.save()
                    return redirect('/index-2')
            except:
                pass  # Aquí podrías capturar el error y mostrar un mensaje

    return render(request, 'tradingapp/page-deposit.html')

@login_required
def get_user_balance(request):
    try:
        vb, _ = VirtualBalance.objects.get_or_create(user=request.user)
        return JsonResponse({'balance': float(vb.usdc_balance)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def coinmarketcap_bar_data(request):
    days = int(request.GET.get("days", 7))
    data = get_coinmarketcap_ohlcv(symbol="bitcoin", days=days)
    return JsonResponse(data)

@login_required
def market(request):
    cryptos = get_top_cryptos(limit=10)  # Puedes ajustar el número si quieres

    for coin in cryptos:
        last_updated = coin.get("last_updated")
        if last_updated:
            try:
                coin["last_updated"] = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
            except Exception:
                coin["last_updated"] = None

    return render(request, 'tradingapp/market.html', {'cryptos': cryptos})



@login_required
def coin_details(request):
    holdings = []
    btc_equivalent = 0
    has_btc = False
    btc_price = 0

    if request.user.is_authenticated:
        holdings = CryptoHolding.objects.filter(user=request.user)

        for coin in holdings:
            if coin.symbol.upper() == 'BTC':
                has_btc = True
                btc_price = get_coin_price_usdc('BTC') or 0
                btc_equivalent = coin.amount * btc_price
                break

    # En caso de que no tenga BTC, igual obtenemos el precio para mostrarlo en la tarjeta
    if not btc_price:
        btc_price = get_coin_price_usdc('BTC') or 0

    context = {
        'holdings': holdings,
        'btc_equivalent': btc_equivalent,
        'has_btc': has_btc,
        'btc_price': round(btc_price, 2),
    }

    print("BTC EQUIVALENT:", btc_equivalent)
    return render(request, 'tradingapp/coin-details.html', context)



@login_required
def buy_crypto(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'}, status=403)

    data = json.loads(request.body)
    symbol = data.get('symbol')
    amount = Decimal(data.get('amount'))
    price = Decimal(data.get('price'))

    total_cost = amount * price

    balance, _ = VirtualBalance.objects.get_or_create(user=request.user)

    if balance.usdc_balance < total_cost:
        return JsonResponse({'error': 'Fondos insuficientes'}, status=400)

    # Restar del balance
    balance.usdc_balance -= total_cost
    balance.save()

    # Añadir o actualizar criptomoneda en el portafolio
    holding, created = CryptoHolding.objects.get_or_create(user=request.user, symbol=symbol.upper())
    holding.amount += amount
    holding.save()

    return JsonResponse({'success': True, 'new_balance': float(balance.usdc_balance)})



@login_required
def future(request):
    context={
        "page_title":"Future Trading"
    }
    return render(request,'tradingapp/trading/future.html',context)


def page_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya está en uso.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Este correo ya está registrado.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, 'Registro exitoso. Ya puedes iniciar sesión.')
            return redirect('tradingapp:page-login')  # Asegúrate de tener esta URL configurada

    return render(request, 'tradingapp/pages/page-register.html')

def page_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            username = User.objects.get(email=email).username
            user = authenticate(request, username=username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            return redirect('tradingapp:index-2')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'tradingapp/pages/page-login.html')


def user_logout(request):
    logout(request)  # Elimina la sesión del servidor
    response = redirect('tradingapp:page-login')
    response.delete_cookie('sessionid')  # Esta línea es opcional pero ayuda a forzar borrado visual
    return response

def page_error_404(request, exception):
    return render(request, '404.html', status=404)
















