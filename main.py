# 2024 GNU License
# Framework for getting coinbase market data and make trade decisions

# Below two packages only work for Coinbase not Coinbase Pro or Sandbox
from coinbase.rest import RESTClient
from coinbase.websocket import WSClient

# cbpro package works for Coinbase Pro and Sandbox
#import cbpro
# General packages
import dateutil
from dotenv import load_dotenv
import json
import os
import pandas as pd
from queue import Queue

ticker_to_subscribe = ['BTC-USD', 'ETH-USD', 'SHIB-USD']

max_data_points = 100 # so dataframe does not explode in size
# Queue for asynchronously storing ticker price and other info
data_queue = Queue()

# Market Data: Spot price, last 24 hour high, last 24 hour low, percent of change in the last 24 hours
market_data = pd.DataFrame(columns=['Spot', 'High', 'Low', 'ChangePct'], index=pd.DatetimeIndex([]))

limit_order_id = ""
order_filled = False
order_sequence = 1

trades = pd.DataFrame(columns=['Product', 'Action', 'Quantity', 'USDValue'], index=pd.DatetimeIndex([]))
#portfolio = pd.DataFrame(columns=['Product', 'Position'], index='Product')

# Function to handle WebSocket messages

def handle_message(msg):
    global order_filled
    global limit_order_id

    msg = json.loads(msg)
    #print(msg)
    if 'channel' in msg and msg['channel'] == 'ticker' and 'events' in msg and msg['events'] and 'tickers' in msg['events'][0]:
        ticker = msg['events'][0]['tickers'][0]
        if 'price' in ticker and 'timestamp' in msg:
            data_queue.put((msg['timestamp'], ticker['product_id'], ticker['price'], ticker['high_24_h'], ticker['low_24_h'], ticker['price_percent_chg_24_h']))  # Put data in the queue
    if 'channel' in msg and msg['channel'] == 'user':
        orders = msg['events'][0]['orders']
        for order in orders:
            if order['order_id'] == limit_order_id and order['status'] == 'FILLED':
                order_filled = True


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
        new_md = pd.DataFrame(
        {
            'Ticker': products,
            'Spot': prices,
            'High': high_24,
            'Low': low_24,
            'ChangePct': changes
        }, index=timestamps)
        print(new_md)
        return new_md
    else:
        return market_data

def trade_limit(rest_client, ws_client):
    global order_filled
    global limit_order_id
    global order_sequence
    global order_filled

    product = rest_client.get_product("BTC-USD")
    price = float(product["price"])
    target_price = str(math.floor(price - (price*0.05)))
    limit_order = rest_client.limit_order_gtc_buy(
        client_order_id = str(order_sequence),
        product_id = "BTC_USD",
        base_size = "0.0002",
        limit_price = target_price
    )
    limit_order_id = limit_order["order_id"]
    while not order_filled:
        ws_client.sleep_with_exception_check(1)
    order_sequence += 1
    order_filled = False

def authenticate():
    # Load Coinbase API credentials from environment
    # put your API key and secret in a .env file
    load_dotenv()
    api_key = os.getenv('API_KEY')
    secret_key = os.getenv('SECRET_KEY')
    pass_phrase = os.getenv('PASS_PHRASE')

    # Initialize WebSocket client
    ws_client = WSClient(api_key=api_key, api_secret=secret_key, on_message=handle_message)

    # Initialize REST client
    rest_client = RESTClient(api_key=api_key, api_secret=secret_key, verbose=True)

    return ws_client, rest_client

def main():
    global market_data
    global order_filled
    global limit_order_id
    global order_sequence

    ws_client, rest_client = authenticate()

    # Open WebSocket connection and subscribe to ticker channels
    ws_client.open()
    # Subscribe to data stream of designated product market data
    print(ticker_to_subscribe)
    ws_client.subscribe(product_ids=ticker_to_subscribe, channels=["ticker", "user"])

    print(rest_client.get_accounts())
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
                # Now make a trading decision based on the latest market data                        
            #trade_limit(rest_client, ws_client)
                    
    except KeyboardInterrupt:
        print("Terminating with Keyboard.")
    finally:
        # Close WebSocket
        ws_client.close()    

if __name__ == "__main__":
    main()