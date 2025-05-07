from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from tradingapp.models import VirtualBalance, CryptoHolding


class TradingAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        VirtualBalance.objects.create(user=self.user, usdc_balance=10000)
        self.client.force_login(self.user)

    def test_buy_btc_with_sufficient_funds(self):
        response = self.client.post('/buy-btc/', {
            'amount_btc': '0.1',
            'price_usdc': '25000',
            'fee': '0',
            'total_usdc': '2500'
        }, follow=True)

        balance = VirtualBalance.objects.get(user=self.user)
        holding = CryptoHolding.objects.filter(user=self.user, symbol='BTC').first()

        self.assertIsNotNone(holding, "No se creó el holding de BTC")
        self.assertAlmostEqual(holding.amount, Decimal('0.1'))
        self.assertEqual(balance.usdc_balance, Decimal('7500'))

    def test_deposit_adds_funds(self):
        response = self.client.post('/deposit/', {
            'amount': 500,
            'seller_mobile': '123456789',
            'product_name': 'Test Product'
        })
        balance = VirtualBalance.objects.get(user=self.user)
        self.assertEqual(balance.usdc_balance, 10500)

    def test_candlestick_api_response(self):
        response = self.client.get('/api/candlestick/BTC/')
        self.assertIn(response.status_code, [200, 429])  # Aceptamos error de rate limit

    def test_buy_btc_with_insufficient_funds(self):
        response = self.client.post('/buy-btc/', {
            'amount_btc': '0.5',
            'price_usdc': '25000',
            'fee': '0',
            'total_usdc': '15000'
        }, follow=True)

        holding = CryptoHolding.objects.filter(user=self.user, symbol='BTC').first()
        self.assertIsNone(holding, "Se creó un holding pese a fondos insuficientes")

        balance = VirtualBalance.objects.get(user=self.user)
        self.assertEqual(balance.usdc_balance, Decimal('10000'))

    def test_sell_btc_success(self):
        CryptoHolding.objects.create(user=self.user, symbol='BTC', amount=Decimal('0.2'))

        response = self.client.post('/sell-btc/', {
            'amount_btc': '0.1',
            'price_usdc': '30000',
        }, follow=True)

        balance = VirtualBalance.objects.get(user=self.user)
        expected_usdc = Decimal('10000') + Decimal('0.1') * Decimal('30000') * Decimal('0.99')  # -1% fee
        self.assertAlmostEqual(balance.usdc_balance, expected_usdc, places=2)

        holding = CryptoHolding.objects.get(user=self.user, symbol='BTC')
        self.assertAlmostEqual(holding.amount, Decimal('0.1'), places=6)

    def test_coin_details_view_logged_in(self):
        response = self.client.get('/coin-details/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tradingapp/coin-details.html')

    def test_index_2_view_shows_balance(self):
        response = self.client.get('/index-2/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tradingapp/index-2.html')
        self.assertIn('balance_usdc', response.context)

