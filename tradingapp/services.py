
import os
from decimal import Decimal

import requests

CMC_API_KEY = "d1af4a50-17ed-4a13-9109-b005a014763d"
CMC_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
CMC_QUOTE_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
CMC_INFO_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/info"


def get_candlestick_data(symbol="BTC", days=7):
    """Obtiene los datos OHLC (velas) de la criptomoneda desde CoinGecko."""
    url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart?vs_currency=usd&days={days}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Convertir los datos en formato OHLC
        candlestick_data = data['prices']
        transformed_data = [
            {
                'timestamp': int(item[0]),  # Timestamp en milisegundos
                'open': item[1],  # Precio de apertura
                'high': item[1],  # Precio más alto
                'low': item[1],   # Precio más bajo
                'close': item[1]  # Precio de cierre
            }
            for item in candlestick_data
        ]

        return transformed_data
    except Exception as e:
        print(f"[ERROR] CoinGecko Candlestick: {e}")
        return []


def get_top_cryptos(limit=50):
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": CMC_API_KEY
    }
    params = {
        "start": "1",
        "limit": str(limit),
        "convert": "USD"
    }

    try:
        response = requests.get(CMC_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("data", [])
    except requests.RequestException as e:
        print(f"[ERROR] CoinMarketCap API: {e}")
        return []

def get_specific_cryptos(symbols):
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": CMC_API_KEY
    }
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    params = {
        "symbol": ",".join(symbols),
        "convert": "USD"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json().get("data", {})
        return [data[s] for s in symbols if s in data]
    except requests.RequestException as e:
        print(f"[ERROR] CoinMarketCap API: {e}")
        return []

def get_candlestick_data(symbol="BTC", days=7):
    url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart?vs_currency=usd&days={days}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Convertir los datos en formato OHLC
        candlestick_data = data['prices']
        transformed_data = [
            {
                'timestamp': int(item[0]),  # Timestamp en milisegundos
                'open': item[1],  # Precio de apertura
                'high': item[1],  # Precio más alto
                'low': item[1],   # Precio más bajo
                'close': item[1]  # Precio de cierre
            }
            for item in candlestick_data
        ]

        return transformed_data
    except Exception as e:
        print(f"[ERROR] CoinGecko Candlestick: {e}")
        return []


def get_coinmarketcap_ohlcv(symbol="bitcoin", days=7, api_key=None):
    """
    Usa CoinGecko para obtener datos OHLC de forma gratuita.
    CoinGecko devuelve [timestamp, open, high, low, close]
    """
    url = f"https://api.coingecko.com/api/v3/coins/{symbol}/ohlc"
    params = {
        "vs_currency": "usd",
        "days": days
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        return {
            "quotes": [
                {
                    "timestamp": item[0],
                    "quote": {
                        "USD": {
                            "open": item[1],
                            "high": item[2],
                            "low": item[3],
                            "close": item[4]
                        }
                    }
                }
                for item in data
            ]
        }
    except Exception as e:
        print(f"[ERROR] CoinGecko OHLCV: {e}")
        return {"quotes": []}


def get_coin_price_usdc(symbol="BTC"):
    try:
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        parameters = {
            'symbol': symbol,
            'convert': 'USDC'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': CMC_API_KEY  # <- aquí usamos la constante directamente
        }

        response = requests.get(url, headers=headers, params=parameters)
        response.raise_for_status()
        data = response.json()

        return Decimal(str(data['data'][symbol]['quote']['USDC']['price']))

    except Exception as e:
        print(f"[ERROR] CoinMarketCap price fetch failed for {symbol}: {e}")
        return None


def get_coin_icon_url(symbol: str) -> str:
    """
    Devuelve la URL del icono (logo) de la criptomoneda indicada,
    usando el endpoint 'info' de CoinMarketCap.
    """
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": CMC_API_KEY  # <- igual aquí
    }
    params = {
        "symbol": symbol.upper()
    }
    try:
        resp = requests.get(CMC_INFO_URL, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json().get("data", {})
        info = data.get(symbol.upper(), {})
        return info.get("logo", "")
    except Exception as e:
        print(f"[ERROR] CoinMarketCap icon fetch failed for {symbol}: {e}")
        return ""
