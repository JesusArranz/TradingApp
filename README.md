# 🧠 Trading Platform Project - Jesús Arranz Navas

This is a Django-based web application that simulates a cryptocurrency trading platform. The system allows users to register, log in, check real-time prices (CoinMarketCap and CoinGecko), buy/sell Bitcoin using virtual USDC funds, and view their current portfolio.

---

## 🚀 Key Features

- 🔐 **User authentication** (email and Google login)  
- 💰 **Deposit virtual USDC funds**  
- 📈 **Real-time market data and candlestick charts**  
- 🪙 **Simulated BTC buy/sell with fee**  
- 🧾 **Live portfolio balance updates**  
- ✅ **Unit tests included to verify core features**

---

## 🛠️ Technologies Used

- Django 5.0  
- HTML5 + CSS3 (custom integrated theme)  
- CoinMarketCap API  
- CoinGecko API  
- SQLite3  
- Pytest / Django TestCase

---

## 📦 Setup and Run

1. **Clone the repository**

2. **Create and activate a virtual environment**
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   
4. **Install dependencies**
   pip install -r requirements.txt

5. **Run the server**
   python manage.py runserver

