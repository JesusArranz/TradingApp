from .models import VirtualBalance

def global_wallet_balance(request):
    if request.user.is_authenticated:
        balance_obj, _ = VirtualBalance.objects.get_or_create(user=request.user)
        return {'sidebar_balance': round(balance_obj.usdc_balance, 2)}
    return {'sidebar_balance': 0.00}
