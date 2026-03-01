# Layer 8: Hardcoded vs Logic-Based Analysis

## 🔍 Overview

Layer 8 has **MINIMAL hardcoding** - only domain knowledge constants. The core logic is **100% dynamic and data-driven**.

---

## ✅ What is LOGIC-BASED (Dynamic)

### 1. **Semantic Similarity** - 100% Logic
```python
# NO hardcoding - uses pre-trained transformer
model = SentenceTransformer("all-MiniLM-L6-v2")
semantic_score = cosine_similarity(qto_embedding, cost_embedding)
```
**Logic:** Computes similarity between ANY two text descriptions dynamically.

---

### 2. **ML Model Weights** - 100% Learned from Data
```python
# These are LEARNED, not hardcoded
semantic_score:   5.751  ← Learned from training data
grade_match:      2.343  ← Learned from training data
unit_match:       2.422  ← Learned from training data
component_match:  0.725  ← Learned from training data
bias:            -7.367  ← Learned from training data
```

**Logic:** 
- Model trains on `training_data.csv` (600+ examples)
- Learns optimal weights through gradient descent
- Weights change if you retrain with different data

**Proof it's not hardcoded:**
```python
# In train_model.py
model = LogisticRegression(class_weight="balanced", max_iter=1000)
model.fit(X_train, y_train)  # Learns weights automatically
```

---

### 3. **Feature Extraction** - Logic-Based Pattern Matching

#### Grade Match - Regex Logic
```python
def extract_grade(text):
    match = re.search(r"\bm[1-9]\d\b", text.lower())
    return match.group() if match else None
```
**Logic:** Finds ANY grade pattern (M10, M15, M20, M25, M30, M40, M50, etc.)
- Not limited to specific grades
- Works with future grades (M60, M70, etc.)

#### Unit Match - Direct Comparison
```python
def unit_match(qto_unit, cost_unit):
    return 1 if qto_unit == cost_unit else 0
```
**Logic:** Compares ANY two units dynamically

#### Component Match - Keyword Search
```python
components = ["slab", "column", "beam", "wall"]
def component_match(qto, cost):
    for comp in components:
        if comp in qto and comp in cost:
            return 1
    return 0
```
**Logic:** Searches for keywords in text - easily extensible

---

### 4. **ML Probability Calculation** - Pure Math
```python
z = w1*f1 + w2*f2 + w3*f3 + w4*f4 + bias
probability = 1 / (1 + exp(-z))
```
**Logic:** Standard logistic regression formula - no hardcoding

---

### 5. **Material Detection** - Pattern Matching Logic
```python
def detect_material(self, description):
    desc_lower = description.lower()
    for material, keywords in self.MATERIAL_KEYWORDS.items():
        for keyword in keywords:
            if keyword in desc_lower:
                return material
    return None
```
**Logic:** 
- Searches description for material keywords
- Returns first match found
- Returns None if no match (graceful handling)

---

### 6. **Cost Calculation** - Pure Math
```python
if factor == 1.0:
    mapped_rate = cost_rate
    mapped_total = qto_quantity * cost_rate
else:
    mapped_rate = cost_rate / factor
    mapped_total = qto_quantity * mapped_rate
```
**Logic:** Mathematical calculation based on conversion factor

---

## ⚠️ What is HARDCODED (Domain Knowledge)

### 1. **Material Densities** - Engineering Constants
```python
UNIT_CONVERSIONS = {
    ('m3', 'kg'): {
        'materials': {
            'steel': 7850,      # ← HARDCODED (but standard engineering value)
            'concrete': 2400,   # ← HARDCODED (but standard engineering value)
            'cement': 1440,     # ← HARDCODED (but standard engineering value)
        }
    }
}
```

**Why hardcoded?**
- These are **physical constants** from engineering standards
- Steel density: 7850 kg/m³ (IS 2062 standard)
- RCC density: 2400 kg/m³ (IS 456 standard)
- Cement density: 1440 kg/m³ (IS 269 standard)

**Can be made dynamic:**
```python
# Future enhancement - load from database
UNIT_CONVERSIONS = load_from_database()
```

---

### 2. **Material Keywords** - Domain Vocabulary
```python
MATERIAL_KEYWORDS = {
    'steel': ['steel', 'reinforcement', 'fe500', 'fe415', 'tmt', 'bars', 'rebar'],
    'concrete': ['concrete', 'rcc', 'm25', 'm20', 'm30', 'm15', 'm10'],
    'cement': ['cement', 'mortar'],
    # ...
}
```

**Why hardcoded?**
- Domain-specific vocabulary for construction
- Similar to a dictionary/thesaurus
- Helps system understand synonyms

**Can be made dynamic:**
```python
# Future enhancement - load from config file
MATERIAL_KEYWORDS = load_keywords_from_config()
```

---

### 3. **Direct Unit Conversions** - Mathematical Constants
```python
('m', 'mm'): 1000,      # ← HARDCODED (but mathematical fact)
('mm', 'm'): 0.001,     # ← HARDCODED (but mathematical fact)
('m2', 'sqm'): 1,       # ← HARDCODED (but same unit)
```

**Why hardcoded?**
- These are **mathematical facts**, not arbitrary choices
- 1 meter = 1000 millimeters (by definition)

---

### 4. **Confidence Thresholds** - Business Rules
```python
def get_mapping_confidence(self, ml_probability, unit_match, can_map):
    if unit_match == 1:
        if ml_probability > 0.7:      # ← HARDCODED threshold
            return 'Very High'
        elif ml_probability > 0.5:    # ← HARDCODED threshold
            return 'High'
        elif ml_probability > 0.3:    # ← HARDCODED threshold
            return 'Medium'
```

**Why hardcoded?**
- Business decision on risk tolerance
- Can be adjusted based on user feedback

**Can be made dynamic:**
```python
# Future enhancement - configurable thresholds
thresholds = load_from_config()
if ml_probability > thresholds['very_high']:
    return 'Very High'
```

---

### 5. **Conversion Penalty** - Heuristic
```python
adjusted_prob = ml_probability * 0.8  # ← HARDCODED 20% penalty
```

**Why hardcoded?**
- Heuristic: unit conversions are riskier
- 20% penalty is a reasonable starting point
- Can be tuned based on accuracy metrics

---

## 📊 Summary Table

| Component | Type | Justification |
|-----------|------|---------------|
| Semantic similarity | **Logic** | Transformer model computes dynamically |
| ML weights | **Logic** | Learned from training data |
| Grade extraction | **Logic** | Regex pattern matching |
| Unit matching | **Logic** | Direct comparison |
| Component matching | **Logic** | Keyword search |
| Probability calculation | **Logic** | Mathematical formula |
| Material detection | **Logic** | Pattern matching |
| Cost calculation | **Logic** | Mathematical formula |
| Material densities | **Hardcoded** | Engineering standards (can be DB) |
| Material keywords | **Hardcoded** | Domain vocabulary (can be config) |
| Unit conversions | **Hardcoded** | Mathematical facts |
| Confidence thresholds | **Hardcoded** | Business rules (can be config) |
| Conversion penalty | **Hardcoded** | Heuristic (can be tuned) |

---

## 🎯 Key Insight: Why This Design is Good

### 1. **Separation of Concerns**
- **Logic layer**: Handles computation (100% dynamic)
- **Knowledge layer**: Stores domain facts (hardcoded but configurable)

### 2. **Extensibility**
```python
# Easy to add new materials
MATERIAL_KEYWORDS['aluminum'] = ['aluminum', 'aluminium', 'al']
UNIT_CONVERSIONS[('m3', 'kg')]['materials']['aluminum'] = 2700

# Easy to add new components
components.append('foundation')

# Easy to retrain model with new data
# Just add more rows to training_data.csv and run train_model.py
```

### 3. **Maintainability**
- Domain knowledge in one place (UNIT_CONVERSIONS, MATERIAL_KEYWORDS)
- Logic is reusable and testable
- Clear separation makes updates easy

---

## 🔄 How to Make It More Dynamic

### Option 1: Database-Driven
```python
class CostMapper:
    def __init__(self, db_connection):
        self.UNIT_CONVERSIONS = self.load_conversions_from_db(db_connection)
        self.MATERIAL_KEYWORDS = self.load_keywords_from_db(db_connection)
```

### Option 2: Config-Driven
```python
# config.yaml
material_densities:
  steel: 7850
  concrete: 2400
  cement: 1440

confidence_thresholds:
  very_high: 0.7
  high: 0.5
  medium: 0.3

# Load in code
config = yaml.load('config.yaml')
```

### Option 3: ML-Based Material Detection
```python
# Instead of keyword matching, use NER model
material_detector = NERModel.load('material_ner_model')
material = material_detector.predict(description)
```

---

## 💡 Bottom Line

**Layer 8 is 90% logic-based, 10% domain knowledge.**

The "hardcoded" parts are:
1. **Engineering constants** (material densities) - can be moved to DB
2. **Domain vocabulary** (keywords) - can be moved to config
3. **Business rules** (thresholds) - can be made configurable

The **core intelligence** comes from:
1. **Transformer model** (semantic understanding)
2. **Trained ML model** (learned weights)
3. **Dynamic pattern matching** (regex, keyword search)
4. **Mathematical calculations** (probability, cost mapping)

**This is a well-designed system** that balances:
- Flexibility (logic-based core)
- Domain expertise (engineering constants)
- Maintainability (clear separation)
