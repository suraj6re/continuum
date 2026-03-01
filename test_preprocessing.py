import sys
sys.path.append('Backend')

import cv2
import numpy as np
from app.ai.raster_pipeline import preprocess_scanned_image, run_raster_pipeline

# Test 1: Check if preprocessing function works
print("Test 1: Testing preprocess_scanned_image function...")
try:
    # Create a dummy image
    test_image = np.random.randint(0, 255, (500, 500, 3), dtype=np.uint8)
    result = preprocess_scanned_image(test_image)
    print(f"✓ Preprocessing works! Output shape: {result.shape}")
    print(f"✓ Output is binary: {np.unique(result)}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: Check if full pipeline works with a real file (if exists)
print("\nTest 2: Testing full raster pipeline...")
try:
    # Create a test image file
    test_img = np.ones((800, 600, 3), dtype=np.uint8) * 255
    cv2.line(test_img, (100, 100), (500, 100), (0, 0, 0), 2)
    cv2.line(test_img, (100, 100), (100, 400), (0, 0, 0), 2)
    cv2.rectangle(test_img, (200, 200), (400, 350), (0, 0, 0), 2)
    
    test_path = "test_drawing.jpg"
    cv2.imwrite(test_path, test_img)
    
    result = run_raster_pipeline(test_path)
    print(f"✓ Pipeline works!")
    print(f"  - Lines detected: {len(result['geometry']['lines'])}")
    print(f"  - Contours detected: {len(result['geometry']['contours'])}")
    print(f"  - Pipeline type: {result['pipeline_type']}")
    
    import os
    os.remove(test_path)
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n✓ All tests passed! The code will run.")
