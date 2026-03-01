def filter_by_distance(df, max_distance_km=30):
    """Filter suppliers within specified distance"""
    return df[df["distance_km"] <= max_distance_km].copy()
