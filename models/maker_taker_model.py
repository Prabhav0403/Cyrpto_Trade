import threading

_model_lock = threading.Lock()

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import joblib
import os

# Paths for saving/loading model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "maker_taker_model.pkl")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "scaler.pkl")

# Initialize
model = None
scaler = None


def train_maker_taker_model(features, labels):
    """
    Train the Logistic Regression model to classify Maker/Taker behavior.
    
    :param features: List or array of features [quantity_usd, volatility, spread]
    :param labels: List or array of labels [0 (Taker), 1 (Maker)]
    """
    global model, scaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)
    
    model = LogisticRegression()
    model.fit(X_scaled, labels)
    
    # Save to disk
    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print("✅ Maker/Taker model and scaler saved successfully.")

def load_model():
    """Thread-safe model and scaler loader."""
    global model, scaler
    with _model_lock:
        if model is not None and scaler is not None:
            return  # Already loaded

        if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
            model = joblib.load(MODEL_PATH)
            scaler = joblib.load(SCALER_PATH)
        else:
            raise FileNotFoundError("Model or scaler file not found. Please train the model first.")

def predict_maker_taker(quantity_usd, volatility, spread):
    if model is None or scaler is None:
        load_model()

    features = np.array([[quantity_usd, volatility, spread]])
    scaled = scaler.transform(features)
    probs = model.predict_proba(scaled)[0]
    label = "Maker" if probs[1] > 0.5 else "Taker"
    return label, probs
