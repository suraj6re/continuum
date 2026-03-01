# UI Stepper Changes - Remove Material & Dimension Parsing

## Summary
Removed "Material & Dimension Parsing" step from the UI stepper and shifted all subsequent steps one position earlier.

## Changes Made

### 1. Frontend/src/pages/Upload.js

**Before:**
```javascript
const steps = ['Upload', 'Hybrid Normalization', 'Legend Intelligence', 'Element Extraction', 'Material & Dimension Parsing', 'Element Graph Model', 'Deterministic QTO', 'Validation & Confidence', ...];
```

**After:**
```javascript
const steps = ['Upload', 'Hybrid Normalization', 'Legend Intelligence', 'Element Extraction', 'Element Graph Model', 'Deterministic QTO', 'Validation & Confidence', ...];
```

**Step Click Handler Updated:**
- `'Element Graph Model'` now shows Layer 4 data (was Layer 5)
- `'Deterministic QTO'` now shows Layer 5 data (was not mapped)

### 2. Frontend/src/components/Stepper.js

**Step Mapping Updated:**
```javascript
const stepMapping = {
  'Upload': 'upload',
  'Hybrid Normalization': 'normalize',
  'Legend Intelligence': 'extract',
  'Element Extraction': 'parse',
  'Element Graph Model': 'validate',      // Now maps to Layer 4
  'Deterministic QTO': 'qto'              // Now maps to Layer 5
};
```

## New Step Order

1. Upload
2. Hybrid Normalization (Layer 1)
3. Legend Intelligence (Layer 2)
4. Element Extraction (Layer 3)
5. ~~Material & Dimension Parsing~~ (REMOVED)
6. Element Graph Model (Layer 4) ← Moved from position 6 to 5
7. Deterministic QTO (Layer 5) ← Moved from position 7 to 6
8. Validation & Confidence ← Moved from position 8 to 7
9. Semantic Cost Alignment ← Moved from position 9 to 8
10. Cost & Risk Engine ← Moved from position 10 to 9
11. Budget Optimization ← Moved from position 11 to 10
12. Supplier & Procurement ← Moved from position 12 to 11
13. Explainable Scheduling ← Moved from position 13 to 12
14. Human Review ← Moved from position 14 to 13
15. Dashboard & Compliance ← Moved from position 15 to 14

## Backend Impact
✅ **NO BACKEND CHANGES** - All backend processing remains the same. Only UI display was modified.

## Testing
- Upload a DWG file
- Verify stepper shows 14 steps (not 15)
- Verify "Material & Dimension Parsing" is not displayed
- Click on "Element Graph Model" → Should show Layer 4 output
- Click on "Deterministic QTO" → Should show Layer 5 output

## Files Modified
- `Frontend/src/pages/Upload.js`
- `Frontend/src/components/Stepper.js`
