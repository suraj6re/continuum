"""
Validation Runner Script
Execute full CNN fallback validation audit
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.ai.cnn_fallback.validation_suite import ValidationSuite


def main():
    """Run validation audit"""
    
    # Configuration
    model_path = 'models/best_model.pth'
    dataset_dir = 'cnn_dataset'
    output_dir = 'cnn_fallback/validation'
    
    print("=" * 60)
    print("CNN Fallback Validation Audit")
    print("=" * 60)
    print(f"Model: {model_path}")
    print(f"Dataset: {dataset_dir}")
    print(f"Output: {output_dir}")
    print("=" * 60)
    
    # Check if model exists
    if not Path(model_path).exists():
        print(f"\n❌ Error: Model not found at {model_path}")
        print("Please train the model first using:")
        print("  python -m app.ai.cnn_fallback.cnn_trainer")
        return 1
    
    # Check if dataset exists
    if not Path(dataset_dir).exists():
        print(f"\n❌ Error: Dataset not found at {dataset_dir}")
        print("Please build the dataset first using:")
        print("  python -m app.ai.cnn_fallback.dataset_builder")
        return 1
    
    # Initialize validation suite
    suite = ValidationSuite(
        model_path=model_path,
        dataset_dir=dataset_dir,
        output_dir=output_dir
    )
    
    # Run full audit
    try:
        results = suite.run_full_audit()
        
        # Print summary
        print("\n" + "=" * 60)
        print("VALIDATION AUDIT SUMMARY")
        print("=" * 60)
        
        mixed = results['mixed_validation']
        confusion = results['confusion_analysis']
        calibration = results['calibration']
        dryrun = results['dryrun']
        
        print(f"\n📊 Mixed Validation Accuracy: {mixed['overall_accuracy']:.2f}%")
        
        if confusion['most_common_confusion']:
            print(f"🔀 Most Common Confusion: {confusion['most_common_confusion']['pair']}")
        
        print(f"🎯 Recommended CNN Threshold: {calibration['recommendations']['safe_override_threshold']:.2f}")
        print(f"⚡ CNN Override Rate: {dryrun['cnn_override_rate']:.2f}%")
        print(f"❌ Incorrect Override Rate: {dryrun['incorrect_override_rate']:.2f}%")
        
        # Safety assessment
        print("\n" + "=" * 60)
        if dryrun['cnn_override_rate'] > 50:
            print("⚠️  WARNING: CNN dominates decisions")
            safe = False
        elif dryrun['incorrect_override_rate'] > 25:
            print("⚠️  WARNING: High incorrect override rate")
            safe = False
        elif mixed['overall_accuracy'] < 80:
            print("⚠️  WARNING: Accuracy below target")
            safe = False
        else:
            print("✅ System appears safe for fallback deployment")
            safe = True
        
        print("=" * 60)
        
        print(f"\n📁 Full report: {output_dir}/CNN_AUDIT_REPORT.md")
        print(f"📁 Validation results: {output_dir}/validation_report.json")
        print(f"📁 Misclassified samples: {output_dir}/misclassified/")
        
        return 0 if safe else 1
        
    except Exception as e:
        print(f"\n❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
