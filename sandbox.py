# 2024 GNU License
# Framework for getting coinbase market data and make trade decisions

# cbpro package works for Coinbase Pro and Sandbox
import cbpro
# General packages
from dotenv import load_dotenv
import os
import pandas as pd
from queue import Queue
import time

ticker_to_subscribe = ['BTC-USD', 'ETH-USD', 'SHIB-USD']

def sandbox_authenticate():
    load_dotenv()
    api_key = os.getenv('API_KEY')
    api_secret = os.getenv('SECRET_KEY')
    pass_phrase = os.getenv('PASS_PHRASE')

    api_url = "https://api-public.sandbox.pro.coinbase.com"
    auth_client = cbpro.AuthenticatedClient(api_key, api_secret, pass_phrase, api_url=api_url)

    return auth_client

def get_accounts(auth_client):
    accounts = auth_client.get_accounts()
    accounts_df = pd.DataFrame(accounts)
    print(accounts_df)

class cbWebsocketClient(cbpro.WebsocketClient):
    def on_open(self):
        self.url = "wss://ws-feed-public.sandbox.exchange.coinbase.com"
        self.products = ticker_to_subscribe
        self.channels = ["ticker"]
        self.message_count = 0
        print("Lets count the messages!")

    def on_message(self, msg):
        self.message_count += 1
        #print(msg)
        if 'price' in msg:
            price_data =(msg['time'], msg['product_id'], msg['price'], msg['high_24h'], msg['low_24h'])
            print(price_data)

    def on_close(self):
        print("-- Goodbye! --")


def main():
    global market_data
    global order_filled
    global limit_order_id
    global order_sequence

    try:
        print("sandboxing....")
        auth_client = sandbox_authenticate()
        get_accounts(auth_client)
        # Subscribe to data stream of designated product market data and user event
        wsClient = cbWebsocketClient()

        wsClient.start()
        while (wsClient.message_count < 10):
            print ("\nmessage_count =", "{} \n".format(wsClient.message_count))
            time.sleep(1)
    except KeyboardInterrupt:
        print("Terminating with Keyboard.")
    finally:
        # Close WebSocket
        wsClient.close()   
        print("end of sandboxing....")               

if __name__ == "__main__":
    main()