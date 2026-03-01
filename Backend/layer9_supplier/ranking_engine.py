import numpy as np

# Configurable weights (can be adjusted based on project priorities)
WEIGHTS = {
    "cost": 0.6,      # 60% weight on cost
    "distance": 0.3,  # 30% weight on distance
    "lead": 0.1       # 10% weight on lead time
}

def normalize(series):
    """Normalize values to 0-1 range"""
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return series * 0  # All same values = 0
    return (series - min_val) / (max_val - min_val)

def rank_suppliers(df, weights=None):
    """
    Rank suppliers based on weighted score
    Lower score = better supplier
    """
    if weights is None:
        weights = WEIGHTS
    
    df = df.copy()
    
    # Normalize each factor (0-1 scale)
    df["norm_cost"] = normalize(df["rate"])
    df["norm_distance"] = normalize(df["distance_km"])
    df["norm_lead"] = normalize(df["lead_time_days"])
    
    # Calculate weighted score (lower is better)
    df["score"] = (
        weights["cost"] * df["norm_cost"] +
        weights["distance"] * df["norm_distance"] +
        weights["lead"] * df["norm_lead"]
    )
    
    # Sort by score (ascending - lowest score first)
    return df.sort_values("score").reset_index(drop=True)
