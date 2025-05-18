# models/impact_model.py

def estimate_market_impact(quantity_usd, volatility, volume=1e6, lambda_param=0.01):
    """
    Simplified Almgren-Chriss discrete-time market impact model.
    
    This model estimates the market impact of a trade based on the trade size (USD equivalent),
    the volatility of the asset, the market's volume, and the risk aversion parameter (lambda).
    
    Parameters:
    - quantity_usd: The trade size in USD.
    - volatility: The volatility of the asset (σ).
    - volume: The market volume (default is 1e6, which represents $1 million in volume).
    - lambda_param: The risk aversion parameter (default is 0.01, higher values lead to larger impact).
    
    Returns:
    - The estimated market impact in USD.
    """
    
    # Almgren-Chriss impact model: 
    # impact = lambda * (quantity / volume)^2 * volatility * quantity
    impact = lambda_param * (quantity_usd / volume)**2 * volatility
    
    # Final market impact, in USD
    return impact * quantity_usd
