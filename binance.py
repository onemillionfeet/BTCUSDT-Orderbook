import threading
import time
import pandas as pd
import json
import websocket
import os
from flask import Flask, send_file, render_template_string

app = Flask(__name__)

# --- CONFIGURATION ---
SYMBOL = "btcusdt"  # Websocket symbols must be lowercase
# Stream for the best bid/ask (bookTicker) - this is the fastest stream
WS_URL = f"wss://stream.binance.us:9443/ws/{SYMBOL}@bookTicker"
CSV_FILENAME = "aggregated_data.csv"

all_rows = []

def on_message(ws, message):
    """This function triggers every time Binance pushes a new price."""
    global all_rows
    data = json.loads(message)
    
    # Binance 'bookTicker' format:
    # u: order book updateId, b: best bid price, B: best bid qty, a: best ask price, A: best ask qty
    row = {
        'update_id': data['u'],
        'best_bid_price': float(data['b']),
        'best_bid_qty': float(data['B']),
        'best_ask_price': float(data['a']),
        'best_ask_qty': float(data['A']),
        'timestamp': int(time.time() * 1000)
    }
    
    all_rows.append(row)
    
    # Keep last 10,000 to save memory
    if len(all_rows) > 50_000:
        all_rows.pop(0)

def on_error(ws, error):
    print(f"WS Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("### Closed Connection - Reconnecting... ###")
    time.sleep(2)
    start_websocket() # Auto-reconnect

def start_websocket():
    ws = websocket.WebSocketApp(WS_URL,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    ws.run_forever()

# --- FLASK ROUTES ---

@app.route('/')
def index():
    return render_template_string("""
        <div style="font-family: sans-serif; text-align: center; margin-top: 50px;">
            <h1 style="color: #f3ba2f;">Binance Real-Time Stream</h1>
            <p style="font-size: 1.5em;">Rows Captured: <strong>{{ count }}</strong></p>
            <p>Speed: Up to 10 updates per second</p>
            <hr style="width: 50%; margin: 20px auto;">
            <a href="/download"><button style="padding: 15px 30px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer;">Download CSV</button></a>
        </div>
    """, count=len(all_rows))

@app.route('/download')
def download():
    if not all_rows: return "No data", 404
    pd.DataFrame(all_rows).to_csv(CSV_FILENAME, index=False)
    return send_file(CSV_FILENAME, as_attachment=True)

if __name__ == "__main__":
    # Run the websocket in the background
    threading.Thread(target=start_websocket, daemon=True).start()
    
    # Run Flask
    port = int(os.environ.get("PORT", 6969))
    app.run(host='0.0.0.0', port=port)
