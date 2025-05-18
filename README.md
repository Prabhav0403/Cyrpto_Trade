 
# 📈 GoQuant Real-Time Trade Simulator

A high-performance, real-time cryptocurrency trade simulator built for GoQuant’s recruitment assignment. The application ingests full L2 orderbook data from OKX via WebSocket, processes it in real-time, and provides predictive insights on transaction costs including **slippage**, **fees**, and **market impact**.

Developed in Python with **Streamlit** for an interactive dashboard, the project also integrates statistical models such as **Almgren-Chriss**, **regression**, and **logistic classification** to simulate market behavior under different trade conditions.

---

## 🎯 Objective

Build a low-latency trade simulator that can:
- Connect to a WebSocket feed
- Process incoming orderbook ticks in real-time
- Predict the **cost of trading** using statistical models
- Visualize key metrics dynamically in a dashboard

---

## 🏗️ Project Structure

goquant_sim/
├── app.py # Main Streamlit app
├── models/ # Modeling logic
│ ├── fee_model.py
│ ├── slippage_model.py
│ ├── impact_model.py
│ └── maker_taker_model.py
├── utils/ # Utilities
│ ├── latency.py
│ └── history_buffer.py
├── wsclient/ # WebSocket client logic
│ └── okx_ws.py
├── ui/ # UI abstraction (optional)
│ └── dashboard.py
├── tests/ # Unit tests (placeholder)
├── requirements.txt # Dependencies
├── README.md # This file
└── main.py # Optional alt entry point


---

## 🧰 Setup Instructions

### ✅ Requirements
- Python 3.8+
- pip
- Internet access (for WebSocket connection)

### 🔧 Installation

```bash
# Clone the repo
git clone https://github.com/yourname/goquant_sim.git
cd goquant_sim

# Create a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

##  Run the App
streamlit run app.py

⚙️ Input Parameters
Parameter	Description
Exchange	Fixed to OKX
Spot Asset	Selectable: BTC-USDT, ETH-USDT, etc.
Order Type	Market (fixed for now)
Quantity (USD)	Size of the trade
Volatility	Slider to simulate market behavior
Fee Tier	Exchange fee tier (Regular, VIP)
Order Role	Maker or Taker

📊 Output Metrics
Metric	Description
Expected Slippage (USD)	Based on bid-ask spread and regression
Expected Fees (USD)	Rule-based fee model by tier and role
Market Impact (USD)	Based on Almgren-Chriss theoretical model
Net Cost (USD)	Combined cost of slippage, fees, and impact
Maker/Taker Role	Logistic regression prediction
Internal Latency (ms)	Time per processing loop
Metrics Over Time	Real-time line chart and downloadable CSV

🔬 Model Overview
✅ Slippage Model
Method: Quantile/Linear Regression

Input: Order size, spread

Output: Estimated USD slippage

✅ Market Impact Model
Method: Almgren-Chriss (simplified)

Input: Volatility, order size

Output: USD impact cost

✅ Fee Model
Method: Tiered static fee rules (based on OKX docs)

Input: Fee tier, maker/taker

Output: USD fees

✅ Maker/Taker Prediction
Method: Logistic Regression

Input: Spread, order size

Output: Role classification (Maker/Taker)

🌐 WebSocket Integration
Connected to:

bash
Copy
Edit
wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP
Sample Response:
json
Copy
Edit
{
  "timestamp": "2025-05-04T10:39:13Z",
  "exchange": "OKX",
  "symbol": "BTC-USDT-SWAP",
  "asks": [["95445.5", "9.06"]],
  "bids": [["95445.4", "1104.23"]]
}
The app processes each incoming tick and updates outputs live.

📈 Performance & Optimization
✅ Latency Metrics Tracked
Orderbook tick → Model output latency

WebSocket → UI update time

Metrics buffer refresh rate

🛠 Optimization Techniques
Multithreaded WebSocket ingestion

Buffered data storage with deque

Efficient numerical ops via NumPy

Selective model execution