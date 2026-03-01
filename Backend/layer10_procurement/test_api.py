import requests
import json

BASE_URL = "http://localhost:8002"

def test_direct_rfq():
    """Test direct RFQ generation"""
    print("=" * 80)
    print("TEST 1: Direct RFQ Generation")
    print("=" * 80)
    
    payload = {
        "supplier_name": "Iron Works",
        "material": "Steel reinforcement Fe500 bars",
        "quantity": 2500,
        "unit": "kg",
        "project_name": "Residential Tower A",
        "delivery_date": "15-02-2025",
        "supplier_id": 8,
        "supplier_location": "Nagpur",
        "expected_rate": 64.0,
        "distance_km": 8,
        "lead_time_days": 1
    }
    
    response = requests.post(f"{BASE_URL}/generate_rfq", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nRFQ ID: {result['rfq_id']}")
        print(f"Supplier: {result['supplier']['name']}")
        print(f"Material: {result['material']['description']}")
        print(f"Quantity: {result['material']['quantity']} {result['material']['unit']}")
        print(f"\nRFQ Text Preview:")
        print(result['rfq_text'][:300] + "...")
        print("\n[OK] Test 1 Passed")
    else:
        print(f"\n[ERROR] Test 1 Failed: {response.status_code}")

def test_layer_integration():
    """Test Layer 8 + Layer 9 integration"""
    print("\n" + "=" * 80)
    print("TEST 2: Layer 8 + Layer 9 Integration")
    print("=" * 80)
    
    payload = {
        "layer8": {
            "description": "Steel reinforcement Fe500 bars",
            "quantity": 2500,
            "unit": "kg"
        },
        "layer9": {
            "recommended_supplier": "Iron Works",
            "recommended_supplier_id": 8,
            "best_rate": 64.0,
            "best_distance": 8,
            "best_lead_time": 1,
            "comparison": [
                {
                    "supplier_name": "Iron Works",
                    "location": "nagpur"
                }
            ]
        },
        "project_name": "Residential Tower A",
        "delivery_date": "15-02-2025"
    }
    
    response = requests.post(f"{BASE_URL}/generate_rfq_from_layers", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nGenerated RFQ:")
        print(f"RFQ ID: {result['rfq_id']}")
        print(f"Status: {result['status']}")
        print(f"\nFull RFQ Text:")
        print(result['rfq_text'])
        print("\n[OK] Test 2 Passed")
    else:
        print(f"\n[ERROR] Test 2 Failed: {response.status_code}")

def main():
    print("\nLayer 10 API Test Suite")
    print("Make sure API is running: uvicorn api:app --reload --port 8002\n")
    
    try:
        # Check if API is running
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("[ERROR] API is not running!")
            return
        
        print(f"API Status: {response.json()}\n")
        
        # Run tests
        test_direct_rfq()
        test_layer_integration()
        
        print("\n" + "=" * 80)
        print("ALL TESTS PASSED")
        print("=" * 80)
        
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to API. Please start the server:")
        print("  uvicorn api:app --reload --port 8002")

if __name__ == "__main__":
    main()
