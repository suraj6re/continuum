"""
Test DWG file upload
"""

import requests
import json
from pathlib import Path

# API endpoint
API_URL = "http://localhost:8000/api/upload/drawing"

# DWG file path
DWG_FILE = Path("../imputs/1.dwg")

if not DWG_FILE.exists():
    print(f"❌ DWG file not found: {DWG_FILE}")
    print("Please ensure the file exists at: imputs/1.dwg")
    exit(1)

print("=" * 60)
print("Testing DWG File Upload")
print("=" * 60)
print(f"File: {DWG_FILE}")
print(f"Size: {DWG_FILE.stat().st_size / 1024:.2f} KB")
print()

# Upload file
print("Uploading...")
with open(DWG_FILE, 'rb') as f:
    files = {'file': ('1.dwg', f, 'application/octet-stream')}
    response = requests.post(API_URL, files=files)

print(f"Status Code: {response.status_code}")
print()

if response.status_code == 200:
    result = response.json()
    print("✅ Upload Successful!")
    print()
    print("Response:")
    print(json.dumps(result, indent=2))
    
    # Get drawing ID
    drawing_id = result['data']['id']
    print()
    print("=" * 60)
    print(f"Drawing ID: {drawing_id}")
    print()
    print("Check status:")
    print(f"  curl http://localhost:8000/api/upload/drawing/{drawing_id}")
    print()
    print("Get Layer 2 results:")
    print(f"  curl http://localhost:8000/api/upload/drawing/{drawing_id}/layer2")
    print("=" * 60)
else:
    print("❌ Upload Failed!")
    print(response.text)
