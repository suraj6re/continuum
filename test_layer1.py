import sys
sys.path.append('Backend')

import cv2
import numpy as np
from app.ai.raster_pipeline import preprocess_scanned_blueprint

print("Testing Layer 1 Preprocessing Pipeline\n" + "="*50)

# Create test image
test_img = np.ones((1000, 800, 3), dtype=np.uint8) * 255
cv2.line(test_img, (100, 100), (700, 100), (0, 0, 0), 3)
cv2.line(test_img, (100, 100), (100, 800), (0, 0, 0), 3)
cv2.rectangle(test_img, (200, 200), (600, 600), (0, 0, 0), 2)
cv2.circle(test_img, (400, 400), 100, (0, 0, 0), 2)

test_path = "test_blueprint.jpg"
cv2.imwrite(test_path, test_img)

try:
    result = preprocess_scanned_blueprint(test_path)
    
    print("✓ Pipeline executed successfully!\n")
    print(f"Output keys: {list(result.keys())}")
    print(f"Clean image shape: {result['clean_image'].shape}")
    print(f"Binary image shape: {result['binary_image'].shape}")
    print(f"Deskew angle: {result['deskew_angle']:.2f}°")
    print(f"Scale factor: {result['scale_factor']}")
    
    # Save outputs
    cv2.imwrite("output_clean.jpg", result['clean_image'])
    cv2.imwrite("output_binary.jpg", result['binary_image'])
    print("\n✓ Output images saved: output_clean.jpg, output_binary.jpg")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

import os
os.remove(test_path)
print("\n✓ Test complete!")
