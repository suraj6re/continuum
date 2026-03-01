def get_top_suppliers(df, top_n=3):
    """Get top N suppliers from ranked dataframe"""
    return df.head(top_n)

def build_output(df, top_n=3):
    """
    Build structured JSON output with recommended supplier and comparison
    """
    if len(df) == 0:
        return {
            "recommended_supplier": None,
            "comparison": [],
            "reason": "No suppliers found matching criteria"
        }
    
    # Get best supplier (lowest score)
    best = df.iloc[0]
    
    # Build comparison list
    comparison = []
    for _, row in df.head(top_n).iterrows():
        comparison.append({
            "supplier_id": int(row["supplier_id"]),
            "supplier_name": row["supplier_name"],
            "material": row["material"],
            "grade": row["grade"] if row["grade"] else "N/A",
            "unit": row["unit"],
            "rate": float(row["rate"]),
            "distance_km": int(row["distance_km"]),
            "lead_time_days": int(row["lead_time_days"]),
            "availability": row["availability"],
            "location": row["location"],
            "score": round(float(row["score"]), 4)
        })
    
    return {
        "recommended_supplier": best["supplier_name"],
        "recommended_supplier_id": int(best["supplier_id"]),
        "best_rate": float(best["rate"]),
        "best_distance": int(best["distance_km"]),
        "best_lead_time": int(best["lead_time_days"]),
        "comparison": comparison,
        "total_suppliers_found": len(df),
        "reason": "Lowest weighted score based on cost (60%), distance (30%), and lead time (10%)"
    }
