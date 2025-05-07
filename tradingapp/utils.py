from decimal import Decimal

from django.shortcuts import redirect
from django.urls import resolve

from .models import CryptoHolding, VirtualBalance
from .services import get_coin_price_usdc

def get_portfolio_summary(user):
    holdings = CryptoHolding.objects.filter(user=user)
    summary = []
    total_value = Decimal('0')

    for holding in holdings:
        symbol = holding.symbol.upper()
        amount = holding.amount
        price = get_coin_price_usdc(symbol) or Decimal('0')
        value = amount * price

        summary.append({
            'symbol': symbol,
            'amount': amount,
            'price': float(price),
            'value': float(value),
        })

        total_value += value

    return summary, float(total_value)



def get_total_wallet_balance(user):
    balance_obj, _ = VirtualBalance.objects.get_or_create(user=user)
    balance = balance_obj.usdc_balance

    holdings = CryptoHolding.objects.filter(user=user)
    total_crypto = Decimal('0')
    for h in holdings:
        price = get_coin_price_usdc(h.symbol) or Decimal('0')
        total_crypto += h.amount * price

    return balance + total_crypto



class RestrictAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Estas rutas no requieren autenticación
        allowed_names = ['page-login', 'page-register', 'page-error-404']
        path = request.path_info

        # Excluir recursos estáticos y medios
        if path.startswith('/static/') or path.startswith('/media/'):
            return self.get_response(request)

        try:
            match = resolve(path)
            url_name = match.url_name
        except:
            url_name = None

        # Solo si no es pública y no está autenticado, redirigir
        if hasattr(request, 'user'):
            if not request.user.is_authenticated and url_name not in allowed_names:
                return redirect('tradingapp:page-login')

        return self.get_response(request)