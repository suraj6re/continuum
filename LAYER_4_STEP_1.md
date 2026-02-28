# Layer 4 Step 1: Graph Validation + Normalization

## 📋 Overview

Layer 4 Step 1 prepares Layer 3 output for Quantity Takeoff (QTO) by:
1. **Validating** structural integrity
2. **Normalizing** units and filling defaults
3. **Preprocessing** for QTO eligibility

## 🎯 Purpose

Before computing quantities, we must ensure:
- ✅ Required properties exist
- ✅ Units are standardized (meters)
- ✅ Missing heights/dimensions are inferred
- ✅ Elements are eligible for measurement
- ✅ Confidence is propagated

## 📥 Input Contract

Layer 4 **ONLY** reads Layer 3 output JSON. No raw CAD access.

```json
{
  "elements": [
    {
      "id": "W1",
      "type": "Wall",
      "length": 4.2,
      "thickness": 0.23,
      "material": "Brick",
      "confidence": 0.88
    }
  ],
  "relationships": [...]
}
```

## 📤 Output Contract

```json
{
  "success": true,
  "elements": [
    {
      "id": "W1",
      "type": "Wall",
      "length": 4.2,
      "thickness": 0.23,
      "height": 3.0,
      "material": "Brick",
      "confidence": 0.88,
      "is_measurable": true,
      "measurement_basis": "geometry_high_confidence",
      "quality_score": 0.88,
      "requires_review": false,
      "has_defaults": true,
      "height_source": "default"
    }
  ],
  "relationships": [...],
  "errors": [],
  "statistics": {
    "total_input": 7,
    "total_processed": 6,
    "total_errors": 1,
    "measurable_elements": 5,
    "high_quality_elements": 4,
    "requires_review": 2,
    "success_rate": 0.857
  }
}
```

## 🏗️ Architecture

```
Layer 4 Step 1
│
├── layer4_validator.py      (Structural integrity checks)
├── layer4_normalizer.py     (Unit standardization + defaults)
├── layer4_preprocessor.py   (QTO eligibility marking)
└── layer4_pipeline.py       (Orchestrator)
```

## 🔍 Component Details

### A) Validator (`layer4_validator.py`)

**Purpose**: Validate structural integrity of input graph

**Required Fields Per Type**:
| Type   | Required Fields        |
|--------|------------------------|
| Wall   | length, thickness      |
| Slab   | area                   |
| Column | area OR (width + depth)|
| Door   | width, height          |
| Window | width, height          |

**Functions**:
- `validate_node(node)` → (is_valid, error_message)
- `validate_graph(graph)` → validation_report

### B) Normalizer (`layer4_normalizer.py`)

**Purpose**: Standardize units & fill missing defaults

**Default Values**:
```python
DEFAULT_WALL_HEIGHT = 3.0       # meters
DEFAULT_COLUMN_HEIGHT = 3.0     # meters
DEFAULT_SLAB_THICKNESS = 0.15   # meters
DEFAULT_DOOR_WIDTH = 0.9        # meters
DEFAULT_DOOR_HEIGHT = 2.1       # meters
DEFAULT_WINDOW_WIDTH = 1.2      # meters
DEFAULT_WINDOW_HEIGHT = 1.5     # meters
```

**Functions**:
- `normalize_units(node)` → Converts all numeric fields to float
- `assign_default_height(node)` → Fills missing heights
- `assign_missing_dimensions(node)` → Fills missing door/window dimensions
- `normalize_material(node)` → Standardizes material names
- `normalize_node(node)` → Applies all normalizations

**Tracking**: Adds `*_source` fields to track origin:
- `height_source: "default"` → Height was assigned
- `area_source: "computed"` → Area computed from width × depth
- `material_source: "default"` → Material was defaulted

### C) Preprocessor (`layer4_preprocessor.py`)

**Purpose**: Mark elements for QTO eligibility

**Confidence Thresholds**:
- `MIN_CONFIDENCE_THRESHOLD = 0.4` → Below this = not measurable
- `GOOD_CONFIDENCE_THRESHOLD = 0.7` → Above this = high quality

**Added Fields**:
- `is_measurable` (bool) → Can this element be measured?
- `measurement_basis` (string) → Why is it measurable?
  - `"geometry_high_confidence"` → confidence ≥ 0.7
  - `"geometry_medium_confidence"` → 0.4 ≤ confidence < 0.7
  - `"rejected_low_confidence"` → confidence < 0.4
- `quality_score` (float) → Overall quality (0-1)
  - Penalized by 20% if using defaults
- `requires_review` (bool) → confidence < 0.7
- `has_defaults` (bool) → Any dimension from defaults

**Functions**:
- `mark_measurable(node)` → Sets is_measurable flag
- `compute_quality_score(node)` → Computes quality score
- `add_metadata(node)` → Adds all preprocessing metadata
- `preprocess_node(node)` → Applies all preprocessing

### D) Pipeline (`layer4_pipeline.py`)

**Purpose**: Orchestrate all steps

**Main Function**:
```python
run_layer4_step1(layer3_output, default_height=3.0) → result
```

**Process Flow**:
1. Validate graph structure
2. For each element:
   - Validate required fields
   - Normalize units
   - Assign defaults
   - Preprocess for QTO
3. Collect errors
4. Compute statistics
5. Return processed graph

**Helper Functions**:
- `get_measurable_elements(result)` → Filter only measurable
- `get_elements_by_type(result, type)` → Filter by type

## 🧪 Testing

```bash
cd Backend
python test_layer4_step1.py
```

**Test Output**:
- Validates 7 sample elements
- Shows normalization (defaults assigned)
- Displays measurability flags
- Saves to `layer4_step1_output.json`

## 📊 Statistics Computed

```python
{
  "total_input": 7,              # Elements from Layer 3
  "total_processed": 6,          # Successfully processed
  "total_errors": 1,             # Validation failures
  "measurable_elements": 5,      # Eligible for QTO
  "high_quality_elements": 4,    # Confidence ≥ 0.7
  "requires_review": 2,          # Needs manual check
  "success_rate": 0.857          # 6/7 = 85.7%
}
```

## 🚨 Error Handling

**Validation Errors**:
- Missing required fields → Element rejected
- Unsupported type → Element rejected
- Invalid data types → Converted to 0.0

**Processing Errors**:
- Caught and logged
- Element skipped
- Processing continues

## 🎯 Why This Step Is Critical

**Without Step 1**:
- ❌ Later formulas will break (missing dimensions)
- ❌ Volumes may compute wrongly (inconsistent units)
- ❌ Doors without height will crash
- ❌ Low-confidence garbage enters QTO

**With Step 1**:
- ✅ Deterministic and stable
- ✅ All elements have required dimensions
- ✅ Units are consistent
- ✅ Quality is tracked
- ✅ Errors are isolated

## 🔄 Integration with Layer 3

Layer 3 outputs → Layer 4 Step 1 → Ready for QTO

```python
from app.ai.layer3_pipeline import run_layer3_pipeline
from app.ai.layer4_pipeline import run_layer4_step1

# Run Layer 3
layer3_output = run_layer3_pipeline(layer1_output, layer2_output)

# Run Layer 4 Step 1
layer4_step1_output = run_layer4_step1(layer3_output)

# Get measurable elements
measurable = get_measurable_elements(layer4_step1_output)

# Ready for Step 2: Volume Computation
```

## 📈 Next Steps

**Layer 4 Step 2**: Volume Computation
- Wall volume = length × thickness × height
- Slab volume = area × thickness
- Column volume = area × height
- Door/Window area = width × height

## ✅ Summary

| Component    | Purpose                    | Output                  |
|--------------|----------------------------|-------------------------|
| Validator    | Structural integrity       | Valid/Invalid + errors  |
| Normalizer   | Unit standardization       | Normalized dimensions   |
| Preprocessor | QTO eligibility            | Measurability flags     |
| Pipeline     | Controlled flow            | Clean graph + stats     |

**Result**: Clean, validated, normalized graph ready for quantity takeoff! 🎉
