# coinbase-trading 
A simple framework for trading crypto with coinbase. This repo helps you to do the following

For Coinbase Advanced User - this repo uses official coinbase-advance-py package
* Authenticate into API with your coinbase API key/secret
* Manage accounts/wallets
* Subscribe to WSS feed, including product information updates and/or user events
* Templates for using the information to make trading decisions. YOu should choose what works for yo to extend
    * Template 1: Time triggered trading decision making
    * Template 2: Market data triggered trading decision making
* Libraries for calling Coinbase APIs to place trades and track order status
* Keep a transient order book and a ledger with average cost basis for each ticker traded. This information helps on making trading decisions while program is running
    * For reliable calculation of cost basis over time, please consider adding a database (not implemented here)

---

## API credential
First create your own trading API credential on Coinbase. Copy the API key and Secret key. Store these two keys in .env file in a format of: \n

'''
API_KEY = $YOUR_API_KEY_ON_COINBASE \n
SECRET_KEY = $YOUR_SECRET_KEY_ON_COINBASE \n
'''

## Subscribe to market data with predefined tickert set
In main.py, ticker_to_subscribe defines the set of ticker you want to subscribe market data to. Enumerate all tickers you want to subscribe

This framework currently prints out ticker, spot price, 24 hours high and low, as well as percentage of change in the last 24 hours. 

## Trading Strategies Templates

More to Come