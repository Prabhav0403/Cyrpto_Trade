def estimate_slippage(quantity_usd, avg_ask, avg_bid, market_depth=10, slippage_factor=0.0005):
    """
    Estimate the slippage for a market order based on order book spread and trade quantity.
    
    Parameters:
    - quantity_usd: Quantity of the asset in USD (size of the trade).
    - avg_ask: Average ask price.
    - avg_bid: Average bid price.
    - market_depth: Number of order book levels to consider for slippage estimation (default is 10).
    - slippage_factor: Adjustment factor to modify the slippage based on market conditions.
    
    Returns:
    - slippage: Estimated slippage in USD.
    """
    
    # Calculate the spread between the best bid and ask
    spread = abs(avg_ask - avg_bid)
    
    # Estimate how much liquidity is available based on market depth
    liquidity_factor = min(market_depth / (quantity_usd / 1000), 1)  # Liquidity decreases with larger trades
    
    # Heuristic adjustment based on quantity and spread
    slippage = slippage_factor * liquidity_factor * spread * (quantity_usd / 1000)
    
    return slippage
