# CNN Fallback Module

Backup layout region classifier for when heuristic detection confidence is low.

## Overview

This module provides a lightweight CNN-based classifier that activates only when heuristic layout detection confidence < 0.65. It classifies cropped drawing regions into 4 categories:

- `legend` - Symbol legends with shapes and labels
- `schedule` - Tables and schedules with grid structure
- `title_block` - Dense metadata blocks with borders
- `drawing_region` - Actual drawing content with lines and dimensions

## Module Structure

```
cnn_fallback/
├── __init__.py                          # Module exports
├── README.md                            # This file
├── VALIDATION_GUIDE.md                  # Validation audit guide
├── synthetic_legend_generator.py        # Legend image generator
├── synthetic_schedule_generator.py      # Schedule/table generator
├── synthetic_titleblock_generator.py    # Title block generator
├── synthetic_drawing_generator.py       # Drawing region generator
├── dataset_builder.py                   # Dataset organization & splitting
├── cnn_trainer.py                       # Training script (MobileNetV2)
├── cnn_evaluator.py                     # Evaluation & metrics
├── cnn_inference.py                     # Inference module for Layer 2
├── validation_suite.py                  # Comprehensive validation audit
├── run_validation.py                    # Validation runner script
└── integration_example.py               # Integration examples
```

## Quick Start

### 1. Generate Dataset

```python
from app.ai.cnn_fallback import DatasetBuilder

builder = DatasetBuilder(base_dir='cnn_dataset')
builder.build_dataset(synthetic_per_class=500)
```

### 2. Train Model

```python
from app.ai.cnn_fallback import CNNTrainer

trainer = CNNTrainer(dataset_dir='cnn_dataset')
history = trainer.train(epochs=15, batch_size=32, lr=1e-4)
```

### 3. Evaluate Model

```python
from app.ai.cnn_fallback import CNNEvaluator

evaluator = CNNEvaluator(
    model_path='models/best_model.pth',
    dataset_dir='cnn_dataset'
)
results = evaluator.evaluate(split='test')
```

### 4. Run Full Validation Audit

```bash
cd Backend
python app/ai/cnn_fallback/run_validation.py
```

This runs comprehensive validation including:
- Mixed validation evaluation
- Confusion analysis with misclassified samples
- Confidence calibration study
- Robustness stress testing
- Real-world dry run simulation
- Final audit report generation

### 5. Add Real Samples (Optional)

```python
# Add real cropped samples
builder.add_real_samples('legend', 'path/to/real/legends')
builder.add_real_samples('schedule', 'path/to/real/schedules')

# Rebuild splits to include real data
builder.rebuild_splits()
```

## Model Architecture

- **Backbone**: MobileNetV2 (pretrained on ImageNet)
- **Fine-tuning**: Last 3 blocks unfrozen
- **Classifier**: Dropout(0.3) + Linear(4 classes)
- **Input**: 224×224×3 RGB images
- **Output**: 4-class softmax probabilities

## Training Configuration

- **Loss**: CrossEntropyLoss
- **Optimizer**: Adam (lr=1e-4)
- **Scheduler**: ReduceLROnPlateau
- **Epochs**: 10-15
- **Batch Size**: 32
- **Target Accuracy**: ≥85%

## Integration with Layer 2

### Option 1: Full Integration with Heuristic Fallback

```python
from app.ai.cnn_fallback import CNNFallbackIntegration

# Initialize
cnn_fallback = CNNFallbackIntegration(
    model_path='models/best_model.pth',
    heuristic_threshold=0.65,  # CNN activates when heuristic < 0.65
    cnn_threshold=0.75         # CNN must be >= 0.75 to accept
)

# In your Layer 2 pipeline
for region in detected_regions:
    # Crop region
    cropped = image[y1:y2, x1:x2]
    
    # Prepare heuristic result
    heuristic_result = {
        "class": region['detected_class'],
        "confidence": region['confidence']
    }
    
    # Classify with fallback
    result = cnn_fallback.classify_region(
        cropped_image=cropped,
        heuristic_result=heuristic_result
    )
    
    # Use result
    final_class = result['class']
    final_confidence = result['final_confidence']
    source = result['source']  # "heuristic", "cnn", or "uncertain"
```

### Option 2: Standalone CNN (No Heuristic)

```python
from app.ai.cnn_fallback import CNNLayoutClassifier

# Initialize
classifier = CNNLayoutClassifier(
    model_path='models/best_model.pth',
    confidence_threshold=0.75
)

# Predict single image
result = classifier.predict(cropped_image)
print(f"Class: {result['class']}, Confidence: {result['confidence']}")

# Batch prediction
results = classifier.predict_batch([img1, img2, img3])
```

### Option 3: Quick Prediction

```python
from app.ai.cnn_fallback import quick_predict

result = quick_predict(cropped_image, model_path='models/best_model.pth')
```

## Confidence Fusion

Final confidence combines heuristic and CNN scores:

```python
final_confidence = 0.7 × heuristic_score + 0.3 × cnn_score
```

## Dataset Structure

```
cnn_dataset/
├── train/
│   ├── legend/
│   ├── schedule/
│   ├── title_block/
│   └── drawing_region/
├── val/
├── test/
├── raw/          # Generated synthetic data
├── real/         # Manually added real samples
└── metadata.json
```

## Output Files

After training and evaluation:

```
models/
├── best_model.pth              # Best checkpoint
├── final_model.pth             # Final checkpoint
├── training_history.json       # Loss/accuracy curves
├── evaluation_test.json        # Test metrics
├── confusion_matrix.png        # Visualization
└── threshold_analysis.json     # Confidence thresholds
```

## Requirements

- PyTorch
- torchvision
- Pillow
- numpy
- scikit-learn
- matplotlib
- seaborn
- tqdm
- scipy

## Notes

- CNN is backup only, not primary logic
- Heuristics have priority when confident
- Model is lightweight and fast (MobileNetV2)
- Synthetic data provides baseline, real data improves accuracy
- Target: ≥85% validation accuracy
