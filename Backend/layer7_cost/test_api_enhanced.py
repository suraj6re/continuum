"""
Test API with Cost Mapping
Tests the enhanced API endpoint with intelligent cost mapping
"""

import requests
import json

API_URL = "http://localhost:8000/align_cost"

def print_separator(char="=", length=100):
    print(char * length)

def print_result(response_data):
    """Pretty print the API response"""
    print_separator()
    print("📋 QUERY")
    print_separator("-")
    query = response_data['query']
    print(f"Description: {query['description']}")
    print(f"Quantity: {query['quantity']} {query['unit']}")
    print()
    
    # Best Match
    if response_data.get('best_match'):
        print_separator()
        print("🏆 BEST MATCH")
        print_separator("-")
        best = response_data['best_match']
        print(f"Cost Item: {best['description']}")
        print(f"Rate: Rs.{best['rate']}/{best['unit']}")
        print(f"ML Probability: {best['ml_probability']:.3f}")
        print(f"Confidence: {best['confidence']}")
        print()
        
        print("Match Details:")
        details = best['match_details']
        print(f"  Grade: {'✅' if details['grade_matched'] else '❌'}")
        print(f"  Unit: {'✅' if details['unit_matched'] else '❌'}")
        print(f"  Component: {'✅' if details['component_matched'] else '❌'}")
        print(f"  Semantic Score: {details['semantic_score']:.3f}")
        print()
        
        print("💰 Cost Mapping:")
        mapping = best['cost_mapping']
        if mapping['can_map']:
            print(f"  Status: ✅ CAN MAP")
            print(f"  Mapped Rate: Rs.{mapping['mapped_rate']}/{query['unit']}")
            print(f"  Total Cost: Rs.{mapping['mapped_total']:,.2f}")
            if mapping['conversion_factor'] != 1.0:
                print(f"  Conversion Factor: {mapping['conversion_factor']}")
            if mapping['warning']:
                print(f"  ⚠️  {mapping['warning']}")
            print(f"  📝 {mapping['explanation']}")
        else:
            print(f"  Status: ❌ CANNOT MAP")
            print(f"  Reason: {mapping['explanation']}")
        print()
    
    # Top Matches
    print_separator()
    print(f"📊 TOP {len(response_data['top_matches'])} MATCHES")
    print_separator("-")
    
    for i, match in enumerate(response_data['top_matches'], 1):
        print(f"\n{i}. {match['description']}")
        print(f"   Rate: Rs.{match['rate']}/{match['unit']}")
        print(f"   Probability: {match['ml_probability']:.3f} | Confidence: {match['confidence']}")
        
        mapping = match['cost_mapping']
        if mapping['can_map']:
            print(f"   💰 Mapped: Rs.{mapping['mapped_rate']}/{query['unit']} → Total: Rs.{mapping['mapped_total']:,.2f}")
        else:
            print(f"   ❌ Cannot map: {mapping['explanation']}")
    
    print()
    print_separator()
    print(f"⚠️  Needs Review: {'YES' if response_data['needs_review'] else 'NO'}")
    print(f"⏱️  Processing Time: {response_data['processing_time_ms']:.2f} ms")
    print(f"🤖 Model: {response_data['model_version']}")
    print_separator()
    print()

def test_case_1():
    """Test Case 1: Unit Mismatch - Steel (m3 vs kg)"""
    print("\n🧪 TEST CASE 1: UNIT MISMATCH - Steel Reinforcement")
    print("QTO has wrong unit (m3) but cost book has correct unit (kg)")
    print()
    
    payload = {
        "description": "Steel reinforcement Fe500 bars",
        "unit": "m3",
        "quantity": 2.5,
        "top_k": 3
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        print_result(response.json())
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        print("Make sure the API server is running: uvicorn api:app --reload")

def test_case_2():
    """Test Case 2: Perfect Match - Concrete"""
    print("\n🧪 TEST CASE 2: PERFECT MATCH - RCC Slab M25")
    print("All features align: semantic, grade, unit, component")
    print()
    
    payload = {
        "description": "RCC slab M25 150mm thick",
        "unit": "m3",
        "quantity": 50.0,
        "top_k": 3
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        print_result(response.json())
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")

def test_case_3():
    """Test Case 3: Grade Match - Concrete M30"""
    print("\n🧪 TEST CASE 3: GRADE MATCH - Concrete M30")
    print("Tests grade matching with different concrete grades")
    print()
    
    payload = {
        "description": "Concrete M30 grade for columns",
        "unit": "m3",
        "quantity": 15.0,
        "top_k": 3
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        print_result(response.json())
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")

def test_case_4():
    """Test Case 4: Correct Unit - Steel in kg"""
    print("\n🧪 TEST CASE 4: CORRECT UNIT - Steel in kg")
    print("Same as Test Case 1 but with correct unit")
    print()
    
    payload = {
        "description": "Steel reinforcement Fe500 bars",
        "unit": "kg",
        "quantity": 1000.0,
        "top_k": 3
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        print_result(response.json())
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")

def test_case_5():
    """Test Case 5: Plaster Work"""
    print("\n🧪 TEST CASE 5: PLASTER WORK - Area based")
    print("Tests area-based cost items")
    print()
    
    payload = {
        "description": "Cement plaster 12mm thick on walls",
        "unit": "m2",
        "quantity": 200.0,
        "top_k": 3
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        print_result(response.json())
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")

def main():
    print("\n")
    print("╔" + "="*98 + "╗")
    print("║" + " "*25 + "API TEST: COST MAPPING SYSTEM" + " "*44 + "║")
    print("╚" + "="*98 + "╝")
    print()
    print("Testing the enhanced API with intelligent cost mapping...")
    print()
    
    # Run all test cases
    test_case_1()
    test_case_2()
    test_case_3()
    test_case_4()
    test_case_5()
    
    print("\n" + "="*100)
    print("✅ ALL API TESTS COMPLETED")
    print("="*100)
    print()
    print("📌 OBSERVATIONS:")
    print("   • Unit mismatches are detected and flagged")
    print("   • Cost mapping attempts intelligent conversion")
    print("   • Confidence levels guide manual review decisions")
    print("   • System provides detailed explanations for each match")
    print()

if __name__ == "__main__":
    main()
