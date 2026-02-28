"""
Integration Example: CNN Fallback with Layer 2 Pipeline
Shows how to integrate CNN classifier with existing heuristic layout detection
"""

import numpy as np
from PIL import Image
from app.ai.cnn_fallback import CNNFallbackIntegration


def example_layer2_integration():
    """
    Example showing how to integrate CNN fallback into Layer 2 pipeline
    """
    
    # Initialize CNN fallback integration
    cnn_fallback = CNNFallbackIntegration(
        model_path='models/best_model.pth',
        heuristic_threshold=0.65,  # CNN activates when heuristic < 0.65
        cnn_threshold=0.75         # CNN must be >= 0.75 to accept
    )
    
    # Simulated Layer 2 pipeline
    print("=" * 60)
    print("Layer 2 Pipeline with CNN Fallback")
    print("=" * 60)
    
    # Example regions detected by heuristic
    detected_regions = [
        {
            "bbox": [100, 100, 300, 300],
            "heuristic_class": "legend",
            "heuristic_confidence": 0.85,  # High confidence
            "image_crop": np.random.randint(0, 255, (200, 200), dtype=np.uint8)
        },
        {
            "bbox": [400, 100, 600, 300],
            "heuristic_class": "schedule",
            "heuristic_confidence": 0.55,  # Low confidence - CNN will activate
            "image_crop": np.random.randint(0, 255, (200, 200), dtype=np.uint8)
        },
        {
            "bbox": [100, 400, 300, 600],
            "heuristic_class": "title_block",
            "heuristic_confidence": 0.40,  # Very low - CNN will activate
            "image_crop": np.random.randint(0, 255, (200, 200), dtype=np.uint8)
        }
    ]
    
    # Process each region
    final_results = []
    
    for i, region in enumerate(detected_regions):
        print(f"\nRegion {i + 1}:")
        print(f"  Heuristic: {region['heuristic_class']} "
              f"(confidence: {region['heuristic_confidence']:.2f})")
        
        # Prepare heuristic result
        heuristic_result = {
            "class": region['heuristic_class'],
            "confidence": region['heuristic_confidence']
        }
        
        # Classify with CNN fallback
        result = cnn_fallback.classify_region(
            cropped_image=region['image_crop'],
            heuristic_result=heuristic_result
        )
        
        print(f"  Final: {result['class']} (source: {result['source']})")
        print(f"  Final confidence: {result['final_confidence']:.2f}")
        print(f"  CNN used: {result['cnn_used']}")
        
        # Add to final results
        final_results.append({
            "bbox": region['bbox'],
            "class": result['class'],
            "confidence": result['final_confidence'],
            "source": result['source']
        })
    
    print("\n" + "=" * 60)
    print("Final Classification Results:")
    print("=" * 60)
    
    for i, result in enumerate(final_results):
        print(f"Region {i + 1}: {result['class']} "
              f"(confidence: {result['confidence']:.2f}, source: {result['source']})")
    
    return final_results


def example_standalone_cnn():
    """
    Example using CNN classifier standalone (without heuristic)
    """
    from app.ai.cnn_fallback import CNNLayoutClassifier
    
    print("\n" + "=" * 60)
    print("Standalone CNN Classification")
    print("=" * 60)
    
    # Initialize classifier
    classifier = CNNLayoutClassifier(
        model_path='models/best_model.pth',
        confidence_threshold=0.75
    )
    
    # Load or create test image
    test_image = np.random.randint(0, 255, (224, 224), dtype=np.uint8)
    
    # Predict
    result = classifier.predict(test_image)
    
    print(f"\nPredicted Class: {result['class']}")
    print(f"Confidence: {result['confidence']:.4f}")
    print(f"Accepted: {result['accepted']}")
    print("\nAll Probabilities:")
    for cls, prob in result['all_probs'].items():
        print(f"  {cls}: {prob:.4f}")


def example_batch_prediction():
    """
    Example using batch prediction for multiple regions
    """
    from app.ai.cnn_fallback import CNNLayoutClassifier
    
    print("\n" + "=" * 60)
    print("Batch Prediction Example")
    print("=" * 60)
    
    # Initialize classifier
    classifier = CNNLayoutClassifier(
        model_path='models/best_model.pth',
        confidence_threshold=0.75
    )
    
    # Create batch of test images
    batch_images = [
        np.random.randint(0, 255, (224, 224), dtype=np.uint8)
        for _ in range(5)
    ]
    
    # Batch predict
    results = classifier.predict_batch(batch_images)
    
    print(f"\nProcessed {len(results)} images:")
    for i, result in enumerate(results):
        print(f"  Image {i + 1}: {result['class']} "
              f"(confidence: {result['confidence']:.4f}, "
              f"accepted: {result['accepted']})")


def example_real_integration_pseudocode():
    """
    Pseudocode showing real integration with Layer 2 pipeline
    """
    code = '''
# In your Layer 2 pipeline (e.g., layer2_boundary.py or pipeline.py)

from app.ai.cnn_fallback import CNNFallbackIntegration

class Layer2Pipeline:
    def __init__(self):
        # Initialize CNN fallback
        self.cnn_fallback = CNNFallbackIntegration(
            model_path='models/best_model.pth',
            heuristic_threshold=0.65,
            cnn_threshold=0.75
        )
    
    def detect_layout_regions(self, image):
        """Detect layout regions with CNN fallback"""
        
        # Step 1: Run heuristic detection
        heuristic_regions = self.heuristic_layout_detection(image)
        
        # Step 2: Process each region
        final_regions = []
        
        for region in heuristic_regions:
            # Crop region from image
            x1, y1, x2, y2 = region['bbox']
            cropped = image[y1:y2, x1:x2]
            
            # Prepare heuristic result
            heuristic_result = {
                "class": region['detected_class'],
                "confidence": region['confidence']
            }
            
            # Classify with CNN fallback
            result = self.cnn_fallback.classify_region(
                cropped_image=cropped,
                heuristic_result=heuristic_result
            )
            
            # Update region with final classification
            region['final_class'] = result['class']
            region['final_confidence'] = result['final_confidence']
            region['classification_source'] = result['source']
            
            final_regions.append(region)
        
        return final_regions
    
    def heuristic_layout_detection(self, image):
        """Your existing heuristic detection logic"""
        # ... existing code ...
        pass
'''
    
    print("\n" + "=" * 60)
    print("Real Integration Pseudocode")
    print("=" * 60)
    print(code)


if __name__ == "__main__":
    # Run examples
    print("CNN Fallback Integration Examples\n")
    
    # Example 1: Full integration with heuristic
    example_layer2_integration()
    
    # Example 2: Standalone CNN
    example_standalone_cnn()
    
    # Example 3: Batch prediction
    example_batch_prediction()
    
    # Example 4: Real integration pseudocode
    example_real_integration_pseudocode()
    
    print("\n" + "=" * 60)
    print("✓ Examples complete!")
    print("=" * 60)
