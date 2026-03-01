import sys
sys.path.append('Backend')

import cv2
import numpy as np
from app.ai.raster_pipeline import preprocess_scanned_blueprint, run_raster_pipeline
import json

print("Direct Layer 1 Preprocessing Test (No Server Required)")
print("="*60)

# Create test image
test_img = np.ones((1000, 800, 3), dtype=np.uint8) * 255
cv2.line(test_img, (100, 100), (700, 100), (0, 0, 0), 3)
cv2.line(test_img, (100, 100), (100, 800), (0, 0, 0), 3)
cv2.rectangle(test_img, (200, 200), (600, 600), (0, 0, 0), 2)
cv2.circle(test_img, (400, 400), 100, (0, 0, 0), 2)
cv2.putText(test_img, "SCALE 1:100", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

test_path = "test_blueprint.jpg"
cv2.imwrite(test_img, test_path)
print(f"✓ Created test image: {test_path}\n")

# Test 1: Layer 1 Preprocessing Only
print("TEST 1: Layer 1 Preprocessing")
print("-" * 60)
try:
    result = preprocess_scanned_blueprint(test_path)
    print("✓ Preprocessing successful!")
    print(f"  - Clean image shape: {result['clean_image'].shape}")
    print(f"  - Binary image shape: {result['binary_image'].shape}")
    print(f"  - Deskew angle: {result['deskew_angle']:.2f}°")
    print(f"  - Scale factor: {result['scale_factor']}")
    
    # Save outputs
    cv2.imwrite("output_clean.jpg", result['clean_image'])
    cv2.imwrite("output_binary.jpg", result['binary_image'])
    print("  - Saved: output_clean.jpg, output_binary.jpg")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Full Raster Pipeline
print("\n\nTEST 2: Full Raster Pipeline (Layer 1 + Geometry)")
print("-" * 60)
try:
    result = run_raster_pipeline(test_path)
    print("✓ Full pipeline successful!")
    print(f"  - Pipeline type: {result['pipeline_type']}")
    print(f"  - Lines detected: {len(result['geometry']['lines'])}")
    print(f"  - Contours detected: {len(result['geometry']['contours'])}")
    print(f"  - Image dimensions: {result['geometry']['image_dimensions']}")
    print(f"  - Deskew angle: {result['scale']['deskew_angle']:.2f}°")
    
    # Show sample lines
    if result['geometry']['lines']:
        print("\n  Sample lines (first 3):")
        for i, line in enumerate(result['geometry']['lines'][:3]):
            print(f"    Line {i+1}: {line['start']} → {line['end']} (length: {line['length']:.1f}px)")
    
    # Show sample contours
    if result['geometry']['contours']:
        print("\n  Sample contours (first 3):")
        for i, contour in enumerate(result['geometry']['contours'][:3]):
            print(f"    Contour {i+1}: area={contour['area']:.0f}, vertices={contour['vertices']}")
    
    # Save full result as JSON
    # Remove numpy arrays for JSON serialization
    json_result = {
        'pipeline_type': result['pipeline_type'],
        'geometry': result['geometry'],
        'scale': result['scale'],
        'parsed_text': result['parsed_text']
    }
    with open('output_result.json', 'w') as f:
        json.dump(json_result, f, indent=2)
    print("\n  - Saved: output_result.json")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Custom Configuration
print("\n\nTEST 3: Custom Configuration")
print("-" * 60)
try:
    custom_config = {
        'bilateral_d': 5,
        'adaptive_block_size': 15,
        'enable_deskew': False
    }
    result = preprocess_scanned_blueprint(test_path, config=custom_config)
    print("✓ Custom config works!")
    print(f"  - Deskew disabled: angle = {result['deskew_angle']:.2f}°")
except Exception as e:
    print(f"✗ Error: {e}")

import os
os.remove(test_path)
print("\n" + "="*60)
print("✓ All tests complete!")
print("\nGenerated files:")
print("  - output_clean.jpg (denoised grayscale)")
print("  - output_binary.jpg (thresholded binary)")
print("  - output_result.json (full pipeline output)")
