import sys
import os
import time
import streamlit as st
import numpy as np
import pandas as pd

# Local imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from wsclient.okx_ws import start_ws_thread, latest_data
from models.fee_model import calculate_fees
from models.slippage_model import estimate_slippage
from models.impact_model import estimate_market_impact
from models.maker_taker_model import predict_maker_taker
from utils.latency import record_latency, latency_records
from utils.history_buffer import MetricsBuffer

# Start WebSocket thread
start_ws_thread()

# Streamlit Config
st.set_page_config(page_title="GoQuant Real-Time Trade Simulator", layout="wide")
st.title("📈 GoQuant Real-Time Trade Simulator")

# State
buffer = MetricsBuffer(maxlen=100)

# Layout
col1, col2 = st.columns([1, 2])

# ----------------------------
# Left Panel: Inputs
# ----------------------------
with col1:
    st.header("⚙️ Input Parameters")
    exchange     = st.selectbox("Exchange", ["OKX"], index=0, disabled=True)
    spot_asset   = st.selectbox("Spot Asset", ["BTC-USDT", "ETH-USDT", "SOL-USDT"])
    order_type   = st.radio("Order Type", ["Market"], index=0, disabled=True)
    quantity_usd = st.number_input("Quantity (USD)", min_value=10.0, max_value=10000.0, value=100.0, step=10.0)
    volatility   = st.slider("Volatility (σ)", min_value=0.0, max_value=1.0, value=0.05, step=0.01)
    fee_tier     = st.selectbox("Fee Tier", ["Regular", "VIP 1", "VIP 2", "VIP 3"])
    is_maker     = st.radio("Order Role", ["Maker", "Taker"]) == "Maker"

# ----------------------------
# Right Panel: Outputs
# ----------------------------
with col2:
    st.header("📊 Output Metrics")

    if latest_data:
        start_time = time.time()

        # Process Order Book
        asks = latest_data.get("asks", [])
        bids = latest_data.get("bids", [])
        avg_ask = np.mean([float(a[0]) for a in asks]) if asks else 0
        avg_bid = np.mean([float(b[0]) for b in bids]) if bids else 0
        spread = abs(avg_ask - avg_bid)

        st.write(f"**Latest Bid Price:** {avg_bid:.2f} USDT")
        st.write(f"**Latest Ask Price:** {avg_ask:.2f} USDT")

        # Compute Trading Metrics
        slippage = estimate_slippage(quantity_usd, avg_ask, avg_bid)
        impact   = estimate_market_impact(quantity_usd, volatility)
        fees     = calculate_fees(quantity_usd, fee_tier, is_maker)
        net_cost = slippage + impact + fees

        # Predict Maker/Taker with trained model
        try:
            role, probs = predict_maker_taker(quantity_usd, volatility, spread)
            prob_maker = probs[1]
            st.metric("Predicted Role", role)
            st.progress(prob_maker if role == "Maker" else 1 - prob_maker)
        except Exception as e:
            role = "Unknown"
            st.error(f"⚠️ Maker/Taker prediction failed: {str(e)}")

        # Record Latency
        latency = record_latency(start_time)
        recent_latency = latency_records[-1] if latency_records else 0

        # Add to Buffer
        buffer.add(
            timestamp=latest_data.get("timestamp", time.strftime("%H:%M:%S")),
            slippage=slippage,
            impact=impact,
            fee=fees,
            net_cost=net_cost,
            latency=recent_latency,
            maker_taker_role=role
        )

        # Show Metrics
        st.metric("Expected Slippage (USD)", f"${slippage:.4f}")
        st.metric("Expected Fees (USD)", f"${fees:.4f}")
        st.metric("Market Impact (USD)", f"${impact:.4f}")
        st.metric("Net Cost (USD)", f"${net_cost:.4f}")
        st.metric("Internal Latency (ms)", f"{recent_latency * 1000:.2f}")

    else:
        st.warning("Waiting for real-time order book data...")

    # ----------------------------
    # Chart + Export
    # ----------------------------
    if buffer.timestamps:
        st.subheader("📈 Metrics Over Time")
        df = pd.DataFrame({
            "Timestamp": list(buffer.timestamps),
            "Slippage": list(buffer.slippages),
            "Impact": list(buffer.impacts),
            "Fees": list(buffer.fees),
            "Net Cost": list(buffer.net_costs),
            "Latency (ms)": [l * 1000 for l in buffer.latencies],
            "Order Role": list(buffer.maker_taker_roles),
        }).set_index("Timestamp")

        st.line_chart(df[["Slippage", "Impact", "Fees", "Net Cost", "Latency (ms)"]])

        # CSV Export
        csv = df.reset_index().to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Metrics as CSV",
            data=csv,
            file_name="metrics_history.csv",
            mime="text/csv"
        )

    st.caption("🔄 Metrics update in real-time from WebSocket stream.")