# models/fee_model.py

# Define the fee tiers for different fee levels on the exchange
FEE_TIERS = {
    "Tier 1": {"maker": 0.0008, "taker": 0.0010},
    "Tier 2": {"maker": 0.0006, "taker": 0.0008},
    "Tier 3": {"maker": 0.0005, "taker": 0.0007},
    "VIP 1": {"maker": 0.0004, "taker": 0.0006},
    "VIP 2": {"maker": 0.0003, "taker": 0.0005},
    "VIP 3": {"maker": 0.0002, "taker": 0.0004},
}

def calculate_fees(quantity_usd, fee_tier, is_maker=False, is_vip=False):
    """
    Calculate the trading fees based on the fee tier, whether the user is a maker or taker,
    and the USD amount for the trade.
    
    Parameters:
    - quantity_usd: The trade amount in USD.
    - fee_tier: The user's fee tier ("Tier 1", "VIP 1", etc.).
    - is_maker: Boolean indicating whether the user is a maker or taker.
    - is_vip: Boolean indicating whether the user is a VIP trader (for specific fee discounts).
    
    Returns:
    - The calculated fee in USD.
    """
    # Select the fee tier based on the user's selection (defaults to Tier 1 if invalid tier)
    tier_fees = FEE_TIERS.get(fee_tier, FEE_TIERS["Tier 1"])

    # If VIP status is enabled, apply a VIP discount (example: 10% off VIP fee)
    if is_vip:
        vip_discount_factor = 0.90  # Apply a 10% discount for VIP traders
        tier_fees["maker"] *= vip_discount_factor
        tier_fees["taker"] *= vip_discount_factor

    # Choose the appropriate fee rate based on whether the user is a maker or taker
    fee_rate = tier_fees["maker"] if is_maker else tier_fees["taker"]

    # Calculate the fee in USD based on the trade size and the fee rate
    fee = quantity_usd * fee_rate

    return fee

