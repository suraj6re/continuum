# CNN Fallback Validation Guide

## Overview

This validation suite performs a comprehensive safety and robustness audit of the CNN fallback system before production deployment. It focuses on validation, calibration, and risk assessment - not just accuracy metrics.

## What Gets Validated

### 1. Mixed Validation Evaluation (Task 1)
- Overall accuracy on validation set
- Per-class precision, recall, F1-score
- Confusion matrix visualization
- Confidence distribution per class

**Output:**
- `validation/validation_report.json`
- `validation/confusion_matrix.png`
- `validation/confidence_histograms.png`

### 2. Confusion Analysis (Task 2)
- Identifies most common misclassification patterns
- Analyzes legend vs schedule confusion
- Analyzes title_block vs schedule confusion
- Saves misclassified samples for manual review

**Output:**
- `validation/misclassified/` folder with images
- Filename format: `trueClass_predictedClass_confidence.png`

### 3. Confidence Calibration Study (Task 3)
- Confidence distribution for correct vs incorrect predictions
- Average confidence statistics
- Threshold analysis (0.5 to 0.9)
- Recommends safe override and escalation thresholds

**Output:**
- `validation/confidence_calibration.png`
- Threshold recommendations in report

### 4. Robustness Stress Test (Task 4)
- Tests model under distortions:
  - Skew (±5°)
  - Blur
  - Contrast reduction
  - Random erasing (5-10% area)
- Identifies which class degrades most
- Detects synthetic data overfitting

**Output:**
- Accuracy drop per distortion type
- Most vulnerable class identification

### 5. Real-World Dry Run Simulation (Task 5)
- Simulates full Layer 2 pipeline with fallback logic
- Tests heuristic + CNN integration
- Measures:
  - CNN override rate
  - Escalation rate
  - Incorrect override rate
- Verifies CNN doesn't dominate decisions

**Output:**
- Decision distribution statistics
- Safety warnings if CNN overrides too aggressively

### 6. Final Audit Report (Task 6)
- Comprehensive markdown report
- Risk assessment
- Threshold recommendations
- Final recommendation:
  - **SAFE FOR PRODUCTION**
  - **SAFE WITH CONDITIONS**
  - **NEEDS REFINEMENT**

**Output:**
- `validation/CNN_AUDIT_REPORT.md`

## Running Validation

### Quick Start

```bash
cd Backend
python app/ai/cnn_fallback/run_validation.py
```

### Prerequisites

1. Trained model at `models/best_model.pth`
2. Dataset at `cnn_dataset/` with train/val/test splits
3. Required packages: torch, torchvision, sklearn, matplotlib, seaborn, scipy

### Expected Runtime

- Small dataset (500 samples/class): ~5-10 minutes
- Large dataset (1000+ samples/class): ~15-30 minutes

## Interpreting Results

### Key Metrics to Check

1. **Mixed Validation Accuracy**
   - Target: ≥85%
   - Acceptable: ≥80%
   - Needs work: <80%

2. **CNN Override Rate**
   - Good: 15-35%
   - Warning: >50% (CNN dominates)
   - Warning: <10% (CNN rarely activates)

3. **Incorrect Override Rate**
   - Good: <15%
   - Acceptable: 15-25%
   - Concerning: >25%

4. **Robustness (Max Accuracy Drop)**
   - Good: <15%
   - Acceptable: 15-20%
   - Concerning: >20%

### Safety Thresholds

The validation suite recommends two thresholds:

1. **Safe Override Threshold**
   - Minimum CNN confidence to accept prediction
   - Typically 0.75-0.85
   - Higher = more conservative

2. **Safe Escalation Threshold**
   - Below this, flag as uncertain
   - Typically 0.50-0.65
   - Used when both heuristic and CNN are uncertain

## Common Issues and Solutions

### Issue: Low Validation Accuracy (<80%)

**Causes:**
- Insufficient training data
- Synthetic data doesn't match real patterns
- Model underfitting

**Solutions:**
1. Add 50+ real samples per class
2. Improve synthetic data generation
3. Train for more epochs
4. Increase model capacity

### Issue: High Confusion Between Classes

**Causes:**
- Visual similarity (e.g., legend vs schedule)
- Synthetic bias
- Insufficient class separation

**Solutions:**
1. Add more diverse training samples
2. Improve synthetic generation to emphasize differences
3. Consider ensemble methods
4. Add class-specific features

### Issue: Poor Robustness to Distortions

**Causes:**
- Overfitting to synthetic data
- Insufficient augmentation during training
- Model too sensitive

**Solutions:**
1. Add more augmentation during training
2. Include distorted samples in training set
3. Use dropout and regularization
4. Test on real scanned drawings

### Issue: CNN Dominates Decisions (>50% override rate)

**Causes:**
- CNN threshold too low
- Heuristic threshold too high
- CNN overconfident

**Solutions:**
1. Increase CNN threshold (e.g., 0.75 → 0.85)
2. Lower heuristic threshold (e.g., 0.65 → 0.60)
3. Recalibrate confidence scores
4. Add temperature scaling

### Issue: High Incorrect Override Rate (>25%)

**Causes:**
- CNN not reliable enough
- Poor confidence calibration
- Model needs improvement

**Solutions:**
1. Increase CNN threshold
2. Retrain with better data
3. Implement confidence calibration
4. Add manual review for low-confidence cases

## Validation Checklist

Before deploying to production:

- [ ] Validation accuracy ≥85%
- [ ] All per-class accuracies ≥75%
- [ ] CNN override rate 15-35%
- [ ] Incorrect override rate <15%
- [ ] Max robustness drop <20%
- [ ] Confidence calibration looks good (correct >> incorrect)
- [ ] Reviewed misclassified samples
- [ ] Tested on real drawings (if available)
- [ ] Final recommendation is "SAFE FOR PRODUCTION" or "SAFE WITH CONDITIONS"

## Next Steps After Validation

### If SAFE FOR PRODUCTION:
1. Deploy with recommended thresholds
2. Set up monitoring and logging
3. Collect production data for continuous improvement
4. Schedule periodic re-validation

### If SAFE WITH CONDITIONS:
1. Deploy to staging environment first
2. Implement strict monitoring
3. Manual review of escalated cases
4. Gradual rollout with A/B testing
5. Collect edge cases for retraining

### If NEEDS REFINEMENT:
1. Collect more real training samples (50+ per class)
2. Improve synthetic data generation
3. Retrain model with augmented dataset
4. Re-run validation audit
5. Consider architecture changes or ensemble methods

## Continuous Validation

After deployment:

1. **Monitor in Production**
   - Track CNN activation rate
   - Log confidence distributions
   - Collect edge cases

2. **Periodic Re-validation**
   - Run validation suite monthly
   - Compare metrics over time
   - Detect model drift

3. **Active Learning**
   - Identify low-confidence cases
   - Add to training set
   - Retrain and re-validate

4. **A/B Testing**
   - Test new models against current
   - Compare validation metrics
   - Gradual rollout of improvements

## Support

For issues or questions:
1. Check `CNN_AUDIT_REPORT.md` for detailed analysis
2. Review misclassified samples in `misclassified/` folder
3. Examine confidence calibration plots
4. Verify dataset quality and balance

---

**Validation Suite Version:** 1.0.0  
**Last Updated:** March 1, 2026
