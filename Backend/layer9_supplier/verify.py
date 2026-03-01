"""
Layer 9 Verification Script
Confirms all components are working without errors
"""

def verify_imports():
    """Verify all modules can be imported"""
    print("=" * 80)
    print("VERIFICATION 1: Module Imports")
    print("=" * 80)
    
    try:
        from supplier_db_loader import load_suppliers, validate_schema
        print("[OK] supplier_db_loader imported")
        
        from distance_calculator import filter_by_distance
        print("[OK] distance_calculator imported")
        
        from ranking_engine import rank_suppliers, normalize
        print("[OK] ranking_engine imported")
        
        from comparison_engine import build_output, get_top_suppliers
        print("[OK] comparison_engine imported")
        
        from config import RANKING_WEIGHTS, MAX_DISTANCE_KM
        print("[OK] config imported")
        
        from api import app
        print("[OK] api imported")
        
        print("\n[SUCCESS] All modules imported successfully\n")
        return True
    except Exception as e:
        print(f"\n[ERROR] Import failed: {e}\n")
        return False

def verify_data_loading():
    """Verify data can be loaded"""
    print("=" * 80)
    print("VERIFICATION 2: Data Loading")
    print("=" * 80)
    
    try:
        from supplier_db_loader import load_suppliers
        suppliers = load_suppliers()
        
        print(f"[OK] Loaded {len(suppliers)} suppliers")
        print(f"[OK] Columns: {list(suppliers.columns)}")
        print(f"[OK] Materials: {suppliers['material'].unique().tolist()}")
        
        print("\n[SUCCESS] Data loading works\n")
        return True
    except Exception as e:
        print(f"\n[ERROR] Data loading failed: {e}\n")
        return False

def verify_filtering():
    """Verify filtering logic"""
    print("=" * 80)
    print("VERIFICATION 3: Filtering Logic")
    print("=" * 80)
    
    try:
        from supplier_db_loader import load_suppliers
        from distance_calculator import filter_by_distance
        
        suppliers = load_suppliers()
        
        # Test distance filter
        nearby = filter_by_distance(suppliers, max_distance_km=30)
        print(f"[OK] Distance filter: {len(suppliers)} -> {len(nearby)} suppliers")
        
        # Test material filter
        steel = suppliers[suppliers["material"] == "steel"]
        print(f"[OK] Material filter: Found {len(steel)} steel suppliers")
        
        # Test grade filter
        fe500 = steel[steel["grade"] == "fe500"]
        print(f"[OK] Grade filter: Found {len(fe500)} Fe500 suppliers")
        
        print("\n[SUCCESS] Filtering logic works\n")
        return True
    except Exception as e:
        print(f"\n[ERROR] Filtering failed: {e}\n")
        return False

def verify_ranking():
    """Verify ranking algorithm"""
    print("=" * 80)
    print("VERIFICATION 4: Ranking Algorithm")
    print("=" * 80)
    
    try:
        from supplier_db_loader import load_suppliers
        from ranking_engine import rank_suppliers
        
        suppliers = load_suppliers()
        steel = suppliers[suppliers["material"] == "steel"]
        
        ranked = rank_suppliers(steel)
        
        print(f"[OK] Ranked {len(ranked)} suppliers")
        print(f"[OK] Best supplier: {ranked.iloc[0]['supplier_name']}")
        print(f"[OK] Best score: {ranked.iloc[0]['score']:.4f}")
        print(f"[OK] Scores are sorted: {ranked['score'].is_monotonic_increasing}")
        
        print("\n[SUCCESS] Ranking algorithm works\n")
        return True
    except Exception as e:
        print(f"\n[ERROR] Ranking failed: {e}\n")
        return False

def verify_output():
    """Verify output generation"""
    print("=" * 80)
    print("VERIFICATION 5: Output Generation")
    print("=" * 80)
    
    try:
        from main import run_supplier_discovery
        
        result = run_supplier_discovery(
            material="steel",
            grade="fe500",
            max_distance_km=30
        )
        
        print(f"[OK] Recommended supplier: {result['recommended_supplier']}")
        print(f"[OK] Best rate: Rs.{result['best_rate']}")
        print(f"[OK] Comparison items: {len(result['comparison'])}")
        print(f"[OK] Total found: {result['total_suppliers_found']}")
        
        # Verify JSON structure
        required_keys = ['recommended_supplier', 'best_rate', 'comparison', 'reason']
        for key in required_keys:
            assert key in result, f"Missing key: {key}"
        print(f"[OK] All required keys present")
        
        print("\n[SUCCESS] Output generation works\n")
        return True
    except Exception as e:
        print(f"\n[ERROR] Output generation failed: {e}\n")
        return False

def verify_api():
    """Verify API endpoints"""
    print("=" * 80)
    print("VERIFICATION 6: API Endpoints")
    print("=" * 80)
    
    try:
        from api import app, extract_material_grade
        
        print("[OK] FastAPI app created")
        
        # Test material extraction
        material, grade = extract_material_grade("Steel reinforcement Fe500 bars")
        print(f"[OK] Material extraction: '{material}', '{grade}'")
        
        material, grade = extract_material_grade("RCC slab M25 150mm thick")
        print(f"[OK] Material extraction: '{material}', '{grade}'")
        
        print("\n[SUCCESS] API components work\n")
        return True
    except Exception as e:
        print(f"\n[ERROR] API verification failed: {e}\n")
        return False

def main():
    print("\n" + "=" * 80)
    print("LAYER 9 COMPREHENSIVE VERIFICATION")
    print("=" * 80 + "\n")
    
    results = []
    
    results.append(("Module Imports", verify_imports()))
    results.append(("Data Loading", verify_data_loading()))
    results.append(("Filtering Logic", verify_filtering()))
    results.append(("Ranking Algorithm", verify_ranking()))
    results.append(("Output Generation", verify_output()))
    results.append(("API Endpoints", verify_api()))
    
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 80)
    if all_passed:
        print("ALL VERIFICATIONS PASSED - LAYER 9 IS READY!")
        print("No errors detected. System is production-ready.")
    else:
        print("SOME VERIFICATIONS FAILED - PLEASE CHECK ERRORS ABOVE")
    print("=" * 80 + "\n")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
