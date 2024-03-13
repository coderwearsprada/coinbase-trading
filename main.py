# 2024 GNU License
# Framework for getting coinbase market data and make trade decisions

from coinbase.websocket import WSClient
import dateutil
from dotenv import load_dotenv
import json
import os
from queue import Queue
import pandas as pd

ticker_to_subscribe = ['BTC-USD', 'ETH_USD']

max_data_points = 100 # so dataframe does not explode in size
# Queue for asynchronously storing ticker price and other info
data_queue = Queue()

# Market Data: Spot price, last 24 hour high, last 24 hour low, percent of change in the last 24 hours
market_data = pd.DataFrame(columns=['Spot', 'High', 'Low', 'ChangePct'], index=pd.DatetimeIndex([]))  # Initialize an empty DataFrame

# Function to handle WebSocket messages
def handle_message(msg):
    msg = json.loads(msg)
    if 'events' in msg and msg['events'] and 'tickers' in msg['events'][0]:
        ticker = msg['events'][0]['tickers'][0]
        if 'price' in ticker and 'timestamp' in msg:
            data_queue.put((msg['timestamp'], ticker['product_id'], ticker['price'], ticker['high_24_h'], ticker['low_24_h'], ticker['price_percent_chg_24_h']))  # Put data in the queue

# deplete the incoming websocket market data queue and store in a dataframe
def get_data():
    global market_data
    timestamps = []
    prices = []
    high_24 = []
    low_24 = []
    changes = []
    products = []
    while not data_queue.empty():
        timestamp, product, price, high, low, change = data_queue.get()  # Get data from the queue
        timestamps.append(pd.to_datetime(dateutil.parser.parse(timestamp).timestamp(), unit='s'))
        products.append(product)
        prices.append(float(price))
        high_24.append(float(high))
        low_24.append(float(low))
        changes.append(float(change))

    if timestamps and prices:
        temp = pd.DataFrame(
        {
            'Ticker': products,
            'Spot': prices,
            'High': high_24,
            'Low': low_24,
            'ChangePct': changes
        }, index=timestamps)
        print(temp)
        return temp
    else:
        return market_data

def main():
    global market_data

    # Load Coinbase API credentials from environment
    # put your API key and secret in a .env file
    load_dotenv()
    api_key = os.getenv('API_KEY')
    secret_key = os.getenv('SECRET_KEY')

    # Initialize WebSocket client
    ws_client = WSClient(api_key=api_key, api_secret=secret_key, on_message=handle_message)

    # Open WebSocket connection and subscribe to ticker channels
    ws_client.open()
    # Subscribe to data stream of designated product market data
    for ticker in ticker_to_subscribe:
        ws_client.subscribe(product_ids=[ticker], channels=["ticker"])

    # Process market data
    while market_data.empty:
        market_data = get_data()
    try:
        while True:
                new_data = get_data()
                if new_data is not None:
                    data = pd.concat([market_data, new_data])

                    if len(data) > max_data_points:
                        data = data.iloc[-max_data_points:]  # Keep only the last max_data_points rows        
    except KeyboardInterrupt:
        print("Terminating with Keyboard.")
    finally:
        # Close WebSocket
        ws_client.close()    

if __name__ == "__main__":
    main()