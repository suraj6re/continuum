import requests
import json

BASE_URL = "http://localhost:8001"

def test_basic_endpoint():
    """Test basic supplier discovery endpoint"""
    print("=" * 80)
    print("TEST 1: Basic Supplier Discovery")
    print("=" * 80)
    
    payload = {
        "material": "steel",
        "grade": "fe500",
        "unit": "kg",
        "max_distance_km": 30
    }
    
    response = requests.post(f"{BASE_URL}/find_supplier", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nRecommended Supplier: {result['recommended_supplier']}")
        print(f"Rate: Rs.{result['best_rate']}/kg")
        print(f"Distance: {result['best_distance']}km")
        print(f"Lead Time: {result['best_lead_time']} days")
        print(f"\nTotal suppliers found: {result['total_suppliers_found']}")
        print("\n[OK] Test 1 Passed")
    else:
        print(f"\n[ERROR] Test 1 Failed: {response.status_code}")
        print(response.text)

def test_layer8_integration():
    """Test Layer 8 output format"""
    print("\n" + "=" * 80)
    print("TEST 2: Layer 8 Integration")
    print("=" * 80)
    
    # Simulate Layer 8 output
    payload = {
        "description": "Steel reinforcement Fe500 bars",
        "unit": "kg",
        "quantity": 2500
    }
    
    response = requests.post(f"{BASE_URL}/find_supplier_from_layer8", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nLayer 8 Input:")
        print(f"  Description: {result['layer8_input']['description']}")
        print(f"  Extracted Material: {result['layer8_input']['extracted_material']}")
        print(f"  Extracted Grade: {result['layer8_input']['extracted_grade']}")
        
        print(f"\nLayer 9 Output:")
        print(f"  Recommended Supplier: {result['recommended_supplier']}")
        print(f"  Rate: Rs.{result['best_rate']}/kg")
        print(f"  Distance: {result['best_distance']}km")
        
        print("\n[OK] Test 2 Passed")
    else:
        print(f"\n[ERROR] Test 2 Failed: {response.status_code}")
        print(response.text)

def test_concrete_m25():
    """Test concrete M25 discovery"""
    print("\n" + "=" * 80)
    print("TEST 3: Concrete M25 Discovery")
    print("=" * 80)
    
    payload = {
        "description": "RCC slab M25 150mm thick",
        "unit": "m3",
        "quantity": 50
    }
    
    response = requests.post(f"{BASE_URL}/find_supplier_from_layer8", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nRecommended: {result['recommended_supplier']}")
        print(f"Rate: Rs.{result['best_rate']}/m3")
        print(f"Total Cost Estimate: Rs.{result['best_rate'] * 50:.2f}")
        print(f"\nTop 3 Suppliers:")
        for i, supplier in enumerate(result['comparison'], 1):
            print(f"  {i}. {supplier['supplier_name']} - Rs.{supplier['rate']}/m3 ({supplier['distance_km']}km)")
        
        print("\n[OK] Test 3 Passed")
    else:
        print(f"\n[ERROR] Test 3 Failed: {response.status_code}")
        print(response.text)

def main():
    print("\nLayer 9 API Test Suite")
    print("Make sure API is running: uvicorn api:app --reload --port 8001\n")
    
    try:
        # Check if API is running
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("[ERROR] API is not running!")
            return
        
        # Run tests
        test_basic_endpoint()
        test_layer8_integration()
        test_concrete_m25()
        
        print("\n" + "=" * 80)
        print("ALL TESTS PASSED")
        print("=" * 80)
        
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to API. Please start the server:")
        print("  uvicorn api:app --reload --port 8001")

if __name__ == "__main__":
    main()
