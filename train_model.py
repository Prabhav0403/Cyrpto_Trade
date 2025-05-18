# train_model.py
import numpy as np
from models.maker_taker_model import train_maker_taker_model

# Generate dummy training data (replace with your real data)
num_samples = 1000
features = np.array([
    np.random.uniform(10, 10000, num_samples),  # quantity_usd
    np.random.uniform(0, 1, num_samples),       # volatility
    np.random.uniform(0.1, 5, num_samples)      # spread
]).T  # Shape: (1000, 3)

# Labels: 0=Taker, 1=Maker (dummy binary labels)
labels = np.random.randint(0, 2, num_samples)

# Train and save
train_maker_taker_model(features, labels)
