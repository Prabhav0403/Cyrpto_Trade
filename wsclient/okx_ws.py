import websocket
import json
import threading
import time
from collections import deque
import traceback

from utils.latency import record_latency

# Shared data structures
latest_data = {}
recent_asks = deque(maxlen=100)
recent_bids = deque(maxlen=100)
lock = threading.Lock()

# OKX WebSocket public endpoint
OKX_SPOT_WS_URL = "wss://ws.okx.com:8443/ws/v5/public"

def on_open(ws):
    print("🔗 WebSocket connection opened")
    # Subscribe to the BTC-USDT order book (books channel)
    subscribe_message = {
        "op": "subscribe",
        "args": [{
            "channel": "books",
            "instId": "BTC-USDT"
        }]
    }
    ws.send(json.dumps(subscribe_message))

def on_message(ws, message):
    global latest_data
    start_time = time.time()
    try:
        data = json.loads(message)
        # Ignore subscription confirmation
        if "event" in data and data["event"] == "subscribe":
            print(f"✅ Subscribed to {data['arg']['channel']}")
            return
        # Handle order book data
        if "arg" in data and data["arg"]["channel"] == "books":
            book_data = data["data"][0]
            timestamp = book_data["ts"]
            asks = [[float(p[0]), float(p[1])] for p in book_data["asks"]]
            bids = [[float(p[0]), float(p[1])] for p in book_data["bids"]]
            with lock:
                recent_asks.append(asks)
                recent_bids.append(bids)
                latest_data = {
                    "timestamp": timestamp,
                    "asks": asks,
                    "bids": bids,
                    "timestamp_unix": time.time()
                }
    except Exception:
        print("❌ Error in on_message:\n", traceback.format_exc())
        return
    latency = time.time() - start_time
    record_latency(latency)
    print(f"✅ Processing latency: {latency:.4f} seconds")
    print(f"📈 Latest data: {latest_data}")

def on_error(ws, error):
    print("❌ WebSocket error:", error)

def on_close(ws, close_status_code, close_msg):
    print(f"🔌 WebSocket closed: {close_status_code} - {close_msg}")

def run_ws():
    backoff = 1
    while True:
        try:
            ws = websocket.WebSocketApp(
                OKX_SPOT_WS_URL,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            ws.run_forever(ping_interval=20, ping_timeout=10)
        except Exception:
            print("❌ Exception in WebSocket thread:\n", traceback.format_exc())
        print(f"🔁 Reconnecting in {backoff} seconds...")
        time.sleep(backoff)
        backoff = min(backoff * 2, 60)

def start_ws_thread():
    thread = threading.Thread(target=run_ws, daemon=True)
    thread.start()

def get_latest_data():
    with lock:
        return latest_data.copy()
