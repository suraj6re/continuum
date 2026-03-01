import pandas as pd

REQUIRED_COLUMNS = [
    "supplier_id",
    "supplier_name",
    "material",
    "grade",
    "unit",
    "rate",
    "location",
    "distance_km",
    "lead_time_days",
    "availability"
]

def validate_schema(df):
    """Validate that all required columns are present"""
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

def load_suppliers(path="data/suppliers.csv"):
    """Load and normalize supplier data"""
    df = pd.read_csv(path)
    
    # Validate schema
    validate_schema(df)
    
    # Normalize text fields
    df["material"] = df["material"].str.lower().str.strip()
    df["grade"] = df["grade"].fillna("").str.lower().str.strip()
    df["unit"] = df["unit"].str.lower().str.strip()
    df["availability"] = df["availability"].str.lower().str.strip()
    df["location"] = df["location"].str.lower().str.strip()
    
    return df
