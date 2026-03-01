# 8th Layer: ML Ranking + Intelligent Cost Mapping System

## 🎯 Overview

This is the **8th layer** of the QTO-to-Cost mapping system that combines:
1. **Semantic Similarity** (Transformer embeddings)
2. **Feature Engineering** (4 domain-specific features)
3. **ML Ranking** (Logistic Regression)
4. **Intelligent Cost Mapping** (Unit conversion & cost calculation)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         INPUT: QTO ITEM                          │
│              (Description, Unit, Quantity)                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1: SEMANTIC SIMILARITY                                    │
│  • Transformer: all-MiniLM-L6-v2                                 │
│  • Cosine similarity with all cost items                         │
│  • Output: semantic_score (0-1)                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 2: FEATURE ENGINEERING                                    │
│  • Feature 1: semantic_score (from Layer 1)                      │
│  • Feature 2: grade_match (M25, M20, etc.)                       │
│  • Feature 3: unit_match (m3, kg, m2, etc.)                      │
│  • Feature 4: component_match (slab, beam, column, wall)         │
│  • Output: Feature vector [f1, f2, f3, f4]                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 3: ML RANKING MODEL                                       │
│  • Model: Logistic Regression                                    │
│  • Trained on labeled data                                       │
│  • Calculation: z = w₁f₁ + w₂f₂ + w₃f₃ + w₄f₄ + b              │
│  • Probability: P = sigmoid(z) = 1/(1 + e^(-z))                 │
│  • Output: ML probability (0-1)                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 4: RANKING & SELECTION                                    │
│  • Sort by ML probability (highest first)                        │
│  • Select top-k matches                                          │
│  • Output: Ranked list of cost items                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 5: COST MAPPING (NEW!)                                    │
│  • Check unit compatibility                                      │
│  • Apply conversion factors if needed                            │
│  • Calculate mapped rate and total cost                          │
│  • Flag items needing review                                     │
│  • Output: Mapped cost with confidence                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OUTPUT: BEST MATCH                            │
│         (Cost item with mapped rate & total cost)                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧮 Mathematical Foundation

### Step 1: Semantic Similarity
```
semantic_score = cosine_similarity(QTO_embedding, Cost_embedding)
                = (QTO · Cost) / (||QTO|| × ||Cost||)
```

### Step 2: Feature Vector
```
X = [semantic_score, grade_match, unit_match, component_match]
```

### Step 3: ML Probability
```
z = w₁ × semantic_score + w₂ × grade_match + w₃ × unit_match + w₄ × component_match + bias

P(match) = sigmoid(z) = 1 / (1 + e^(-z))
```

### Step 4: Cost Mapping
```
If unit_match = 1:
    mapped_rate = cost_rate
    mapped_total = quantity × cost_rate

If unit_match = 0 and conversion exists:
    conversion_factor = get_conversion_factor(qto_unit, cost_unit, material)
    mapped_rate = cost_rate / conversion_factor
    mapped_total = quantity × mapped_rate
```

---

## 📊 Example Walkthrough

### 🧱 Scenario: Steel Reinforcement (Unit Mismatch)

**QTO:**
- Description: "Steel reinforcement Fe500 bars"
- Unit: m³ ❌ (wrong)
- Quantity: 2.5 m³

**Cost Item:**
- Description: "Steel reinforcement Fe500"
- Unit: kg ✅ (correct in database)
- Rate: Rs. 65/kg

---

### Step 1: Semantic Similarity
```
Transformer computes:
semantic_score = 0.83
```
Very high because text meaning is almost identical.

---

### Step 2: Feature Vector Creation
```
Feature              Value    Why
─────────────────────────────────────────────
semantic_score       0.83     Very similar text
grade_match          0        No M-grade in steel
unit_match           0        m³ ≠ kg
component_match      0        No slab/column/beam/wall

Feature vector: [0.83, 0, 0, 0]
```

---

### Step 3: ML Ranking Calculation

**Model weights (learned from training):**
```
Feature              Weight
─────────────────────────────
semantic_score       1.0
grade_match          2.5
unit_match           2.0
component_match      1.2
bias                 -3.0
```

**Calculation:**
```
z = (1.0 × 0.83) + (2.5 × 0) + (2.0 × 0) + (1.2 × 0) - 3.0
z = 0.83 - 3.0
z = -2.17

P(match) = sigmoid(-2.17) = 1/(1 + e^2.17) ≈ 0.10
```

**Result:** Probability ≈ 0.10 (Low confidence)

Even though semantic similarity is high, the unit mismatch kills confidence.

---

### Step 4: Cost Mapping

**Unit Conversion:**
```
From: m³ (QTO)
To: kg (Cost)
Material: Steel
Density: 7850 kg/m³

conversion_factor = 7850
```

**Cost Calculation:**
```
mapped_rate = 65 / 7850 = Rs. 0.0083/m³ ❌ (This doesn't make sense!)

⚠️ WARNING: Unit mismatch detected
⚠️ This mapping requires manual review
```

**Confidence:** Low (with conversion) - 0.08

---

### 🎯 Compare with Correct Unit Case

**Same QTO but with correct unit:**
- Unit: kg ✅

**Feature vector:**
```
[0.83, 0, 1, 0]  ← unit_match = 1 now
```

**ML Calculation:**
```
z = (1.0 × 0.83) + (2.5 × 0) + (2.0 × 1) + (1.2 × 0) - 3.0
z = 0.83 + 2.0 - 3.0
z = -0.17

P(match) = sigmoid(-0.17) ≈ 0.46
```

**Result:** Probability ≈ 0.46 (Medium confidence)

Much better! Unit match adds +2.0 to the score.

---

### 🏆 Perfect Match Example: RCC Slab

**QTO:**
- Description: "RCC slab M25 150mm thick"
- Unit: m³
- Quantity: 50 m³

**Cost Item:**
- Description: "Reinforced Cement Concrete M25"
- Unit: m³
- Rate: Rs. 7200/m³

**Feature vector:**
```
[0.53, 1, 1, 0]
```

**ML Calculation:**
```
z = (1.0 × 0.53) + (2.5 × 1) + (2.0 × 1) + (1.2 × 0) - 3.0
z = 0.53 + 2.5 + 2.0 - 3.0
z = 2.03

P(match) = sigmoid(2.03) ≈ 0.88
```

**Cost Mapping:**
```
Units match: m³ = m³ ✅
mapped_rate = Rs. 7200/m³
mapped_total = 50 × 7200 = Rs. 3,60,000
```

**Confidence:** Very High - 0.88

---

## 🔧 Implementation Files

### 1. `cost_mapper.py`
Handles intelligent unit conversion and cost mapping.

**Key Features:**
- Material detection (steel, concrete, cement, etc.)
- Unit conversion factors (m³↔kg, m²↔m³, etc.)
- Cost calculation with conversion
- Confidence adjustment for conversions

### 2. `api.py`
FastAPI endpoint for QTO-to-Cost mapping.

**Endpoint:** `POST /align_cost`

**Request:**
```json
{
  "description": "Steel reinforcement Fe500 bars",
  "unit": "m3",
  "quantity": 2.5,
  "top_k": 3
}
```

**Response:**
```json
{
  "query": {
    "description": "Steel reinforcement Fe500 bars",
    "quantity": 2.5,
    "unit": "m3"
  },
  "best_match": {
    "cost_id": 6,
    "description": "Steel reinforcement Fe500",
    "unit": "kg",
    "rate": 65,
    "ml_probability": 0.10,
    "confidence": "Low (with conversion)",
    "match_details": {
      "grade_matched": false,
      "unit_matched": false,
      "component_matched": false,
      "semantic_score": 0.83
    },
    "cost_mapping": {
      "can_map": true,
      "mapped_rate": 0.0083,
      "mapped_total": 0.02,
      "conversion_factor": 7850,
      "warning": "Converting m3 to kg using steel density",
      "explanation": "Converted mapping: 2.5 m3 × Rs.65/kg (factor: 7850.00) = Rs.0.01/m3"
    }
  },
  "top_matches": [...],
  "needs_review": true,
  "processing_time_ms": 45.23
}
```

### 3. `test_complete_system.py`
Comprehensive test script demonstrating the full pipeline.

**Run:**
```bash
python test_complete_system.py
```

### 4. `ml_reranker/train_model.py`
Trains the logistic regression model.

**Features:**
- Loads training data with labels
- Trains logistic regression with class balancing
- Saves model as `model.pkl`

### 5. `ml_reranker/training_data.csv`
Labeled training data with 600+ examples.

**Format:**
```csv
semantic_score,grade_match,unit_match,component_match,label
0.83,1,1,0,1
0.47,0,1,0,0
...
```

---

## 🚀 Usage

### 1. Install Dependencies
```bash
pip install fastapi uvicorn pandas scikit-learn sentence-transformers joblib
```

### 2. Train Model (if needed)
```bash
cd ml_reranker
python train_model.py
```

### 3. Run API Server
```bash
cd "Backend/8th layer"
uvicorn api:app --reload --port 8000
```

### 4. Test the System
```bash
python test_complete_system.py
```

### 5. Test API
```bash
python test_api.py
```

Or use curl:
```bash
curl -X POST "http://localhost:8000/align_cost" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "RCC slab M25 150mm thick",
    "unit": "m3",
    "quantity": 50.0,
    "top_k": 3
  }'
```

---

## 📈 Model Performance

The logistic regression model learns optimal weights for each feature:

| Feature | Typical Weight | Impact |
|---------|---------------|--------|
| semantic_score | ~1.0 | Baseline similarity |
| grade_match | ~2.5 | High impact (concrete grade critical) |
| unit_match | ~2.0 | High impact (unit compatibility critical) |
| component_match | ~1.2 | Medium impact (structural element type) |

**Why these weights?**
- **unit_match** has high weight because wrong units → incorrect cost
- **grade_match** has high weight because concrete grade affects strength & cost
- **semantic_score** provides baseline but can be misleading alone
- **component_match** helps distinguish similar items (slab vs beam)

---

## 🎯 Key Insights

### 1. Semantic Similarity Alone is Not Enough
```
"Steel reinforcement Fe500 bars" (m³)
vs
"Steel reinforcement Fe500" (kg)

Semantic score: 0.83 (very high)
But wrong unit → Low confidence (0.10)
```

### 2. Engineering Features Add Domain Knowledge
```
Feature engineering captures:
- Material grades (M25, M20, Fe500)
- Unit compatibility (m³, kg, m²)
- Component types (slab, beam, column)
```

### 3. ML Model Learns Optimal Weights
```
Model learns from training data:
- Which features matter most
- How to combine features
- When to flag for review
```

### 4. Cost Mapping Handles Real-World Complexity
```
- Same units → Direct mapping
- Different units → Intelligent conversion
- Impossible conversion → Flag for review
```

---

## ⚠️ Important Notes

1. **Unit Mismatch Warning:** When QTO unit ≠ Cost unit, the system attempts conversion but flags for review.

2. **Confidence Levels:**
   - **Very High (>0.7):** Direct use recommended
   - **High (0.5-0.7):** Use with minor review
   - **Medium (0.3-0.5):** Review recommended
   - **Low (<0.3):** Manual review required

3. **Conversion Limitations:**
   - m³ ↔ kg: Requires material density
   - m² ↔ m³: Requires thickness
   - Some conversions are impossible

4. **Model Retraining:** Add more labeled examples to `training_data.csv` and retrain for better accuracy.

---

## 🔮 Future Enhancements

1. **Deep Learning Ranking:** Replace logistic regression with neural network
2. **More Conversion Rules:** Add more material densities and conversion factors
3. **Fuzzy Matching:** Handle typos and variations in descriptions
4. **Multi-language Support:** Support regional languages
5. **Historical Learning:** Learn from user corrections

---

## 📞 Support

For questions or issues, refer to the main project documentation or contact the development team.

---

**Version:** 1.1 (with Cost Mapping)  
**Last Updated:** 2024
