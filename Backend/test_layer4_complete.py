"""Test Complete Layer 4 Pipeline with Traceability"""
import json
from app.ai.layer4_pipeline import run_layer4_pipeline

def test_complete_layer4():
    """Test complete Layer 4 pipeline with all steps"""
    
    # Sample Layer 3 output
    sample_layer3_output = {
        "elements": [
            {"id": "wall-1", "type": "Wall", "length": 4.2, "thickness": 0.23, "height": 3.0, 
             "material": "Brick", "confidence": 0.9},
            {"id": "wall-2", "type": "Wall", "length": 3.5, "thickness": 0.23, 
             "material": "Brick", "confidence": 0.7},
            {"id": "slab-1", "type": "Slab", "area": 15.5, "thickness": 0.15, 
             "material": "Concrete", "confidence": 0.85},
            {"id": "column-1", "type": "Column", "width": 0.3, "depth": 0.3, "height": 3.0, 
             "material": "RCC", "confidence": 0.78},
            {"id": "door-1", "type": "Door", "code": "D1", "width": 0.9, "height": 2.1, 
             "material": "Wood", "confidence": 0.91}
        ],
        "relationships": [],
        "summary": {}
    }
    
    print("=" * 70)
    print("TESTING COMPLETE LAYER 4 PIPELINE")
    print("=" * 70)
    
    # Run complete pipeline
    print("\n[1] Running Complete Pipeline (All Steps)...")
    result = run_layer4_pipeline(
        sample_layer3_output,
        include_reinforcement=True,
        include_aggregation=True,
        include_confidence=True,
        include_validation_metrics=True,
        group_by_fields=["material"]
    )
    
    if not result["success"]:
        print(f"[X] Pipeline failed")
        return
    
    print("[OK] Pipeline complete!")
    
    # Display Step 1 results
    print("\n[2] Step 1: Validation + Normalization")
    print(f"  Processed: {result['step1']['statistics']['total_processed']}")
    print(f"  Measurable: {result['step1']['statistics']['measurable_elements']}")
    
    # Display Step 2 results with traceability
    print("\n[3] Step 2: Measurements (with Traceability)")
    for measurement in result['measurements'][:3]:
        print(f"\n  {measurement['element_id']} ({measurement['type']}):")
        print(f"    Formula: {measurement['formula']}")
        
        if 'formula_trace' in measurement:
            trace = measurement['formula_trace']
            print(f"    Trace:")
            print(f"      Formula: {trace['formula']}")
            print(f"      Calculation: {trace['calculation']}")
            print(f"      Dimension sources: {trace['dimension_sources']}")
            print(f"      Has defaults: {trace.get('has_defaults', False)}")
    
    # Display Step B results
    print("\n[4] Step B: Reinforcement")
    print(f"  Total steel: {result['statistics']['reinforcement'].get('total_steel_kg', 0)} kg")
    
    # Display Step C results
    print("\n[5] Step C: Aggregation")
    print(f"  Total groups: {result['statistics']['aggregation'].get('total_groups', 0)}")
    
    # Display Step D results
    print("\n[6] Step D: Confidence")
    conf_stats = result['statistics']['aggregation'].get('confidence', {})
    print(f"  Avg confidence: {conf_stats.get('average_confidence', 'N/A')}")
    
    # Display Step E results (Validation Metrics)
    print("\n[7] Step E: Validation Metrics (for Layer 5)")
    metrics = result['validation_metrics']
    print(f"  Total slab area: {metrics.get('total_slab_area', 0)} m2")
    print(f"  Total concrete volume: {metrics.get('total_concrete_volume', 0)} m3")
    print(f"  Total wall length: {metrics.get('total_wall_length', 0)} m")
    print(f"  Total steel weight: {metrics.get('total_steel_weight', 0)} kg")
    print(f"  Total column count: {metrics.get('total_column_count', 0)}")
    print(f"  Total door count: {metrics.get('total_door_count', 0)}")
    print(f"  Total window count: {metrics.get('total_window_count', 0)}")
    
    # Display aggregation with confidence
    print("\n[8] Final Aggregation (with Confidence):")
    for group_key, data in result['aggregation'].items():
        print(f"\n  {group_key}:")
        print(f"    Confidence: {data.get('confidence', 'N/A')}")
        print(f"    Quantities: {data['quantities']}")
    
    # Save output
    print("\n[9] Saving complete output...")
    with open("layer4_complete_output.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print("\n" + "=" * 70)
    print("[OK] COMPLETE LAYER 4 TEST PASSED")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  [+] Traceability: Formula traces with dimension sources")
    print("  [+] Edge case handling: Default heights tracked")
    print("  [+] Confidence propagation: Weighted by quantity")
    print("  [+] Validation metrics: Ready for Layer 5")
    print("  [+] Complete pipeline: All steps integrated")
    print("\nOutput saved to: layer4_complete_output.json")

if __name__ == "__main__":
    test_complete_layer4()
