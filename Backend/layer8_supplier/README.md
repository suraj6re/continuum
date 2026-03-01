# Layer 9 - Supplier Matching System

## Complete Implementation ✅

### Overview
Layer 9 intelligently matches materials from Layer 8 to the best suppliers based on cost, distance, and lead time.

### Folder Structure
```
layer9_supplier/
├── data/
│   └── suppliers.csv          # Supplier database (15 suppliers)
├── supplier_db_loader.py      # Data loader with validation
├── distance_calculator.py     # Distance filtering logic
├── ranking_engine.py          # Weighted ranking algorithm
├── comparison_engine.py       # Structured output builder
├── config.py                  # Configurable parameters
├── main.py                    # Complete test suite
└── README.md                  # This file
```

### Complete Flow

```
Layer 8 Output → Layer 9 Input
{
  "material": "steel",
  "grade": "fe500",
  "quantity": 2500,
  "unit": "kg"
}

↓ Step 1: Load Supplier Database
↓ Step 2: Filter by Distance (≤30km)
↓ Step 3: Rank by Weighted Score
↓ Step 4: Build Structured Output

Layer 9 Output
{
  "recommended_supplier": "Iron Works",
  "best_rate": 64.0,
  "comparison": [...],
  "reason": "Lowest weighted score..."
}
```

## Step-by-Step Implementation

### ✅ Step 1: Supplier Database Setup

**File:** `supplier_db_loader.py`

**Features:**
- Loads 15 suppliers from CSV
- Validates schema (10 required columns)
- Normalizes text fields (lowercase, trim)
- Handles missing grades

**Schema:**
| Column | Type | Description |
|--------|------|-------------|
| supplier_id | int | Unique identifier |
| supplier_name | string | Supplier name |
| material | string | Material type |
| grade | string | Material grade |
| unit | string | Unit of measurement |
| rate | float | Rate per unit (Rs.) |
| location | string | Supplier location |
| distance_km | int | Distance from site |
| lead_time_days | int | Delivery lead time |
| availability | string | Stock status |

### ✅ Step 2: Distance Logic

**File:** `distance_calculator.py`

**Logic:**
```python
filter_by_distance(df, max_distance_km=30)
```

- Uses precomputed `distance_km` from CSV
- Configurable max distance parameter
- No external APIs required
- Stable for demos

**Example:**
- Total suppliers: 15
- Within 30km: 9 suppliers

### ✅ Step 3: Ranking Logic

**File:** `ranking_engine.py`

**Algorithm:**

1. **Normalize** each factor to 0-1 scale:
   ```python
   norm_value = (value - min) / (max - min)
   ```

2. **Calculate weighted score**:
   ```python
   score = 0.6 × norm_cost + 0.3 × norm_distance + 0.1 × norm_lead
   ```

3. **Sort ascending** (lowest score = best)

**Weights (Configurable in `config.py`):**
- Cost: 60% - Most important factor
- Distance: 30% - Logistics impact
- Lead Time: 10% - Planning consideration

**Why This Works:**
- Transparent scoring
- Explainable to stakeholders
- Easy to adjust priorities
- No hardcoded values

### ✅ Step 4: Structured Output

**File:** `comparison_engine.py`

**Output Format:**
```json
{
  "recommended_supplier": "Iron Works",
  "recommended_supplier_id": 8,
  "best_rate": 64.0,
  "best_distance": 8,
  "best_lead_time": 1,
  "comparison": [
    {
      "supplier_id": 8,
      "supplier_name": "Iron Works",
      "material": "steel",
      "grade": "fe500",
      "unit": "kg",
      "rate": 64.0,
      "distance_km": 8,
      "lead_time_days": 1,
      "availability": "in stock",
      "location": "nagpur",
      "score": 0.0
    },
    {...}
  ],
  "total_suppliers_found": 2,
  "reason": "Lowest weighted score based on cost (60%), distance (30%), and lead time (10%)"
}
```

## Usage

### Basic Usage

```python
from main import run_supplier_discovery

# Find best steel supplier
result = run_supplier_discovery(
    material="steel",
    grade="fe500",
    max_distance_km=30
)

print(result["recommended_supplier"])  # "Iron Works"
print(result["best_rate"])             # 64.0
```

### Run Complete Test Suite

```bash
cd Backend/layer9_supplier
python main.py
```

### Adjust Configuration

Edit `config.py` to change priorities:

```python
RANKING_WEIGHTS = {
    "cost": 0.5,      # Reduce cost importance
    "distance": 0.4,  # Increase distance importance
    "lead": 0.1
}

MAX_DISTANCE_KM = 50  # Expand search radius
```

## Test Results

### Test Case 1: Steel Fe500
- **Input:** material="steel", grade="fe500", max_distance=30km
- **Suppliers Found:** 2
- **Recommended:** Iron Works
- **Rate:** Rs.64/kg
- **Distance:** 8km
- **Lead Time:** 1 day

### Test Case 2: Concrete M25
- **Input:** material="concrete", grade="m25", max_distance=50km
- **Suppliers Found:** 3
- **Recommended:** Concrete Plus
- **Rate:** Rs.7150/m3
- **Distance:** 22km
- **Lead Time:** 2 days

## Architecture Highlights

### ✅ No Hardcoding
- All weights configurable in `config.py`
- Distance threshold adjustable
- Top N suppliers configurable
- Material/grade filters dynamic

### ✅ Pure Logic-Based
- Normalization algorithm for fair comparison
- Weighted scoring with mathematical formula
- Sorting by computed score
- No arbitrary decisions

### ✅ Modular Design
- Each step in separate file
- Easy to test individually
- Easy to modify/extend
- Clear separation of concerns

### ✅ Explainable AI
- Score calculation is transparent
- Weights are visible
- Reason provided in output
- Stakeholders can understand decisions

## Integration with Layer 8

Layer 8 provides:
```json
{
  "best_match": {
    "description": "Steel reinforcement Fe500",
    "unit": "kg",
    "rate": 65,
    "cost_mapping": {
      "mapped_total": 162500
    }
  }
}
```

Layer 9 extracts:
- Material: "steel" (from description)
- Grade: "fe500" (from description)
- Unit: "kg"

Then finds best supplier matching these criteria.

## What's NOT Included

❌ Auto-purchase functionality
❌ Quantity modification
❌ Payment integration
❌ Contract generation
❌ Real-time GPS tracking

Layer 9 is **comparison only** - provides recommendations, not transactions.

## Future Enhancements

1. **Availability Scoring:** Factor stock status into ranking
2. **Historical Performance:** Track supplier reliability
3. **Bulk Discounts:** Apply quantity-based pricing
4. **Multi-Material Orders:** Optimize for multiple materials
5. **Dynamic Pricing:** Real-time rate updates

## Configuration Options

### Ranking Weights
Adjust based on project priorities:

**Cost-Focused Project:**
```python
WEIGHTS = {"cost": 0.8, "distance": 0.15, "lead": 0.05}
```

**Urgent Project:**
```python
WEIGHTS = {"cost": 0.4, "distance": 0.3, "lead": 0.3}
```

**Local-First Project:**
```python
WEIGHTS = {"cost": 0.4, "distance": 0.5, "lead": 0.1}
```

## Summary

| Step | File | Purpose | Logic |
|------|------|---------|-------|
| 1 | supplier_db_loader.py | Load & validate data | Schema validation, normalization |
| 2 | distance_calculator.py | Filter by distance | Threshold comparison |
| 3 | ranking_engine.py | Rank suppliers | Normalization + weighted scoring |
| 4 | comparison_engine.py | Build output | JSON structuring |

**Total Lines of Code:** ~200 (excluding tests)
**Dependencies:** pandas, numpy
**Hardcoded Values:** 0
**Configurable Parameters:** 5+

---

**Status:** ✅ All Steps Complete
**Version:** 1.0
**Last Tested:** Successfully on Windows
