import requests
import pandas as pd
import time

url = "https://api.binance.us/api/v3/depth"

session = requests.Session()

params = {
    "symbol" : "BTCUSDT",
    "limit" : 1
}

all_rows = []

current_stamp = int(time.time() * 1000)
time_length = 180 # minutes

while int(time.time() * 1000) < current_stamp + (time_length * 60 * 1000): # first number = minutes
    response = session.get(url, params=params) # session.get
    data = response.json()
    
    # Extract the data into a dictionary
    row = {
        'update_id': data['lastUpdateId'],
        'best_bid_price': float(data['bids'][0][0]),
        'best_bid_qty': float(data['bids'][0][1]),
        'best_ask_price': float(data['asks'][0][0]),
        'best_ask_qty': float(data['asks'][0][1]),
        'timestamp': int(time.time() * 1000)
    }
    
    # Append the dictionary to your list
    all_rows.append(row)

master_df = pd.DataFrame(all_rows)
master_df = master_df.drop_duplicates(subset=['update_id'], keep='first')
master_df = master_df.reset_index(drop=True)
master_df = master_df.set_index("update_id")

print(master_df)

master_df.to_csv("aggregated_data.csv")
    
'''bid_level = pd.DataFrame(data["bids"], columns=["best_bid_price", "best_bid_qty"], dtype=float)
print(bid_level)

ask_level = pd.DataFrame(data["asks"], columns=["best_ask_price", "best_ask_qty"], dtype=float)
ask_level["side"] = "ask"'''

#print(pd.concat([bid_level, ask_level]).sort_values("price", ascending=False).to_string())