import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import time
import streamlit as st
import numpy as np
import pandas as pd
from wsclient.okx_ws import start_ws_thread, get_latest_data
from models.fee_model import calculate_fees
from models.slippage_model import estimate_slippage
from models.impact_model import estimate_market_impact
from models.maker_taker_model import predict_maker_taker, load_model
from utils.latency import record_latency, latency_records
from utils.history_buffer import MetricsBuffer

# Load models
load_model()

# Start WebSocket in the background (once per session)
if "ws_started" not in st.session_state:
    start_ws_thread()
    st.session_state.ws_started = True

# Streamlit UI setup
st.set_page_config(page_title="GoQuant Real-Time Trade Simulator", layout="wide")
st.title("📈 GoQuant Real-Time Trade Simulator")

# History buffer
buffer = MetricsBuffer(maxlen=100)

UI_TO_INTERNAL_TIER = {
    "Regular": "Tier 1",
    "VIP 1": "VIP 1",
    "VIP 2": "VIP 2",
    "VIP 3": "VIP 3"
}

# Input Layout
col1, col2 = st.columns([1, 2])
with col1:
    st.header("⚙️ Input Parameters")
    exchange = st.selectbox("Exchange", ["OKX"], index=0, disabled=True)
    spot_asset = st.selectbox("Spot Asset", ["BTC-USDT", "ETH-USDT", "SOL-USDT"])
    quantity_usd = st.number_input("Quantity (USD)", min_value=10.0, max_value=10000.0, value=100.0, step=10.0)
    volatility = st.slider("Volatility (σ)", min_value=0.0, max_value=1.0, value=0.05, step=0.01)
    fee_tier = st.selectbox("Fee Tier", ["Regular", "VIP 1", "VIP 2", "VIP 3"])
    is_maker = st.radio("Order Role", ["Maker", "Taker"]) == "Maker"

# Output Panel
with col2:
    st.header("📊 Output Metrics")

    latest_data = get_latest_data()

    if latest_data and "asks" in latest_data and "bids" in latest_data:
        asks = latest_data["asks"]
        bids = latest_data["bids"]

        avg_ask = np.mean([float(a[0]) for a in asks]) if asks else 0
        avg_bid = np.mean([float(b[0]) for b in bids]) if bids else 0
        spread = abs(avg_ask - avg_bid)

        # Timestamp freshness
        data_age = time.time() - latest_data.get("timestamp_unix", time.time())
        if data_age > 5:
            st.warning(f"⚠️ Data is {data_age:.1f}s old. Waiting for fresh updates...")

        st.write(f"**Latest Bid Price:** {avg_bid:.2f} USDT")
        st.write(f"**Latest Ask Price:** {avg_ask:.2f} USDT")

        # Calculations
        slippage = estimate_slippage(quantity_usd, avg_ask, avg_bid)
        impact = estimate_market_impact(quantity_usd, volatility)
        fees = calculate_fees(quantity_usd, UI_TO_INTERNAL_TIER[fee_tier], is_maker=is_maker, is_vip=fee_tier.startswith("VIP"))
        net_cost = slippage + impact + fees
        maker_taker_role, _ = predict_maker_taker(quantity_usd, volatility, spread)

        # Record latency
        processing_start = time.time()
        record_latency(processing_start)
        recent_latency = latency_records[-1] if latency_records else 0

        # Buffer update
        buffer.add(
            timestamp=latest_data.get("timestamp", time.strftime("%H:%M:%S")),
            slippage=slippage,
            impact=impact,
            fee=fees,
            net_cost=net_cost,
            latency=recent_latency,
            maker_taker_role=maker_taker_role
        )

        # Display Metrics
        st.metric("Expected Slippage (USD)", f"${slippage:.4f}")
        st.metric("Expected Fees (USD)", f"${fees:.4f}")
        st.metric("Market Impact (USD)", f"${impact:.4f}")
        st.metric("Net Cost (USD)", f"${net_cost:.4f}")
        st.metric("Order Role", maker_taker_role)
        st.metric("Internal Latency (ms)", f"{recent_latency * 1000:.2f}")

    else:
        st.warning("Waiting for real-time data from WebSocket...")

    # Plot history if available
    if buffer.timestamps:
        st.subheader("📈 Metrics Over Time")

        df = pd.DataFrame({
            "Timestamp": list(buffer.timestamps),
            "Slippage": list(buffer.slippages),
            "Impact": list(buffer.impacts),
            "Fees": list(buffer.fees),
            "Net Cost": list(buffer.net_costs),
            "Latency (ms)": [l * 1000 for l in buffer.latencies],
            "Order Role": list(buffer.maker_taker_roles)}).set_index("Timestamp")

        st.line_chart(df[["Slippage", "Impact", "Fees", "Net Cost", "Latency (ms)"]])

        # CSV Download
        st.download_button(
            label="📥 Download Metrics as CSV",
            data=df.reset_index().to_csv(index=False).encode("utf-8"),
            file_name="metrics_history.csv",
            mime="text/csv"
        )

    st.caption("🔄 Live updates powered by WebSocket feed.")