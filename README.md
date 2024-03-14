# coinbase-trading
A simple framework for trading crypto with coinbase

## API credential
First create your own trading API credential on Coinbase. Copy the API key and Secret key. Store these two keys in .env file in a format of: \n

API_KEY = $YOUR_API_KEY_ON_COINBASE \n
SECRET_KEY = $YOUR_SECRET_KEY_ON_COINBASE \n

## Subscribe to market data with predefined tickert set
In main.py, ticker_to_subscribe defines the set of ticker you want to subscribe market data to. Enumerate all tickers you want to subscribe

This framework currently prints out ticker, spot price, 24 hours high and low, as well as percentage of change in the last 24 hours. 

## More to come on trading strategies and plugable components