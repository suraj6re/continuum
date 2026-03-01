from supplier_db_loader import load_suppliers
from distance_calculator import filter_by_distance
from ranking_engine import rank_suppliers
from comparison_engine import build_output
import json

def run_supplier_discovery(material, grade="", unit="", max_distance_km=30):
    """
    Main orchestrator for Layer 9 supplier discovery
    
    Args:
        material: Material type (e.g., 'steel', 'concrete')
        grade: Material grade (e.g., 'fe500', 'm25')
        unit: Unit of measurement (e.g., 'kg', 'm3')
        max_distance_km: Maximum distance filter
    
    Returns:
        Structured JSON with recommended supplier and comparison
    """
    # Step 1: Load supplier database
    suppliers = load_suppliers()
    
    # Step 2: Filter by material
    filtered = suppliers[suppliers["material"] == material.lower()]
    
    # Filter by grade if provided
    if grade:
        filtered = filtered[filtered["grade"] == grade.lower()]
    
    # Filter by unit if provided
    if unit:
        filtered = filtered[filtered["unit"] == unit.lower()]
    
    # Step 3: Filter by distance
    filtered = filter_by_distance(filtered, max_distance_km)
    
    # Step 4: Rank suppliers
    ranked = rank_suppliers(filtered)
    
    # Step 5: Build structured output
    result = build_output(ranked, top_n=3)
    
    return result

def test_step1():
    """Test Step 1: Database loading"""
    print("=" * 80)
    print("STEP 1: Supplier Database Setup")
    print("=" * 80)
    
    suppliers = load_suppliers()
    print(f"\nTotal suppliers loaded: {len(suppliers)}")
    print("\nFirst 5 suppliers:")
    print(suppliers.head())
    print("\n[OK] Step 1 Complete")

def test_step2():
    """Test Step 2: Distance filtering"""
    print("\n" + "=" * 80)
    print("STEP 2: Distance Logic")
    print("=" * 80)
    
    suppliers = load_suppliers()
    nearby = filter_by_distance(suppliers, max_distance_km=30)
    print(f"\nSuppliers within 30km: {len(nearby)}")
    print(nearby[["supplier_name", "distance_km", "location"]].head())
    print("\n[OK] Step 2 Complete")

def test_step3():
    """Test Step 3: Ranking logic"""
    print("\n" + "=" * 80)
    print("STEP 3: Ranking Logic")
    print("=" * 80)
    
    suppliers = load_suppliers()
    steel = suppliers[suppliers["material"] == "steel"]
    ranked = rank_suppliers(steel)
    print("\nTop 3 ranked steel suppliers:")
    print(ranked[["supplier_name", "rate", "distance_km", "lead_time_days", "score"]].head(3))
    print("\n[OK] Step 3 Complete")

def test_step4():
    """Test Step 4: Structured output"""
    print("\n" + "=" * 80)
    print("STEP 4: Structured Output")
    print("=" * 80)
    
    result = run_supplier_discovery(material="steel", grade="fe500", max_distance_km=30)
    print("\nStructured JSON Output:")
    print(json.dumps(result, indent=2))
    print("\n[OK] Step 4 Complete")

def test_full_flow():
    """Test complete Layer 9 flow"""
    print("\n" + "=" * 80)
    print("COMPLETE LAYER 9 FLOW TEST")
    print("=" * 80)
    
    # Test Case 1: Steel Fe500
    print("\n[Test Case 1] Steel Fe500")
    result1 = run_supplier_discovery(material="steel", grade="fe500", max_distance_km=30)
    print(f"Recommended: {result1['recommended_supplier']}")
    print(f"Rate: Rs.{result1['best_rate']}/kg")
    print(f"Distance: {result1['best_distance']}km")
    print(f"Total suppliers found: {result1['total_suppliers_found']}")
    
    # Test Case 2: Concrete M25
    print("\n[Test Case 2] Concrete M25")
    result2 = run_supplier_discovery(material="concrete", grade="m25", max_distance_km=50)
    print(f"Recommended: {result2['recommended_supplier']}")
    print(f"Rate: Rs.{result2['best_rate']}/m3")
    print(f"Distance: {result2['best_distance']}km")
    print(f"Total suppliers found: {result2['total_suppliers_found']}")
    
    print("\n" + "=" * 80)
    print("ALL STEPS COMPLETE - LAYER 9 READY")
    print("=" * 80)

def main():
    # Run all tests
    test_step1()
    test_step2()
    test_step3()
    test_step4()
    test_full_flow()

if __name__ == "__main__":
    main()
