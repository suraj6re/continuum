import requests
import cv2
import numpy as np
import json

print("Layer 1 Preprocessing API Test")
print("="*50)

# Create test image
test_img = np.ones((1000, 800, 3), dtype=np.uint8) * 255
cv2.line(test_img, (100, 100), (700, 100), (0, 0, 0), 3)
cv2.line(test_img, (100, 100), (100, 800), (0, 0, 0), 3)
cv2.rectangle(test_img, (200, 200), (600, 600), (0, 0, 0), 2)
cv2.circle(test_img, (400, 400), 100, (0, 0, 0), 2)
cv2.putText(test_img, "1:100", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

test_path = "test_blueprint.jpg"
cv2.imwrite(test_path, test_img)
print(f"✓ Created test image: {test_path}\n")

# Upload to API
url = "http://localhost:8000/api/upload/drawing"
files = {'file': open(test_path, 'rb')}

print("Uploading to API...")
try:
    response = requests.post(url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        print("✓ Upload successful!\n")
        print(json.dumps(result, indent=2))
        
        # Get drawing ID
        drawing_id = result['data']['id']
        print(f"\n✓ Drawing ID: {drawing_id}")
        print(f"✓ Status: {result['data']['status']}")
        print(f"✓ Pipeline: {result['data']['pipeline_type']}")
        
        # Fetch full details
        print("\nFetching full drawing details...")
        detail_response = requests.get(f"http://localhost:8000/api/upload/drawing/{drawing_id}")
        if detail_response.status_code == 200:
            details = detail_response.json()
            print("✓ Full details retrieved")
            print(f"  - Lines detected: {len(details['data'].get('geometry', {}).get('lines', []))}")
            print(f"  - Contours detected: {len(details['data'].get('geometry', {}).get('contours', []))}")
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("✗ Cannot connect to API. Make sure server is running:")
    print("  cd Backend")
    print("  uvicorn main:app --reload")
except Exception as e:
    print(f"✗ Error: {e}")

import os
os.remove(test_path)
print("\n✓ Test complete!")
