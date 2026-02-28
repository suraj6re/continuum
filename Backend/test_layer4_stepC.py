"""Test Layer 4 Step C: Material-Based Aggregation"""
import json
from app.ai.layer4_pipeline import (run_layer4_step1, run_layer4_step2, 
                                     run_layer4_stepB, run_layer4_stepC, 
                                     run_layer4_pipeline)
from app.ai.layer4_aggregation_engine import get_aggregation_by_work_category, get_total_by_metric

def test_layer4_stepC():
    """Test Layer 4 Step C with sample data"""
    
    # Sample Layer 3 output
    sample_layer3_output = {
        "elements": [
            {"id": "slab-1", "type": "Slab", "area": 15.5, "thickness": 0.15, 
             "material": "Concrete", "confidence": 0.85},
            {"id": "slab-2", "type": "Slab", "area": 12.0, "thickness": 0.15, 
             "material": "Concrete", "confidence": 0.82},
            {"id": "column-1", "type": "Column", "width": 0.3, "depth": 0.3, "height": 3.0, 
             "material": "RCC", "confidence": 0.78},
            {"id": "column-2", "type": "Column", "area": 0.09, "height": 3.0, 
             "material": "RCC", "confidence": 0.82},
            {"id": "wall-1", "type": "Wall", "length": 4.2, "thickness": 0.23, "height": 3.0, 
             "material": "Brick", "confidence": 0.88},
            {"id": "wall-2", "type": "Wall", "length": 3.5, "thickness": 0.23, "height": 3.0, 
             "material": "Brick", "confidence": 0.92},
            {"id": "wall-3", "type": "Wall", "length": 5.0, "thickness": 0.23, "height": 3.0, 
             "material": "RCC", "confidence": 0.90},
            {"id": "door-1", "type": "Door", "code": "D1", "width": 0.9, "height": 2.1, 
             "material": "Wood", "confidence": 0.91}
        ],
        "relationships": [],
        "summary": {}
    }
    
    print("=" * 70)
    print("TESTING LAYER 4 - STEP C: MATERIAL-BASED AGGREGATION")
    print("=" * 70)
    
    # Run Steps 1, 2, B
    print("\n[1] Running Steps 1, 2, B...")
    step1_result = run_layer4_step1(sample_layer3_output)
    step2_result = run_layer4_step2(step1_result)
    stepB_result = run_layer4_stepB(step2_result)
    print(f"[OK] Measurements: {len(step2_result['element_measurements'])}")
    print(f"[OK] Reinforcement: {len(stepB_result['reinforcement_estimation'])}")
    
    # Step C: Aggregate by material (default)
    print("\n[2] Running Step C: Aggregation by Material...")
    stepC_result = run_layer4_stepC(step2_result, stepB_result)
    
    if not stepC_result["success"]:
        print(f"[X] Step C failed: {stepC_result.get('error')}")
        return
    
    print("[OK] Step C complete!")
    
    # Display summary
    print("\n[3] Aggregation Summary:")
    summary = stepC_result["summary"]
    print(f"  Total groups: {summary['total_groups']}")
    print(f"  Total elements: {summary['total_elements']}")
    print(f"  Grouping by: {summary['grouping_dimensions']}")
    print(f"  Work categories: {', '.join(summary['work_categories'])}")
    
    print(f"\n  Total Quantities:")
    for metric, value in summary['total_quantities'].items():
        unit = "m3" if "volume" in metric else ("m2" if "area" in metric else ("kg" if "steel" in metric else ""))
        print(f"    {metric}: {value} {unit}")
    
    # Display aggregation by material
    print("\n[4] Aggregation by Material:")
    for group_key, data in stepC_result["aggregation"].items():
        print(f"\n  {group_key}:")
        print(f"    Work Category: {data['work_category']}")
        print(f"    Element Count: {data['element_count']}")
        print(f"    Quantities:")
        for metric, value in data['quantities'].items():
            unit = "m3" if "volume" in metric else ("m2" if "area" in metric else ("kg" if "steel" in metric else ""))
            print(f"      {metric}: {value} {unit}")
    
    # Test aggregation by work category
    print("\n[5] Re-aggregation by Work Category:")
    by_category = get_aggregation_by_work_category(stepC_result)
    for category, quantities in by_category.items():
        print(f"\n  {category}:")
        for metric, value in quantities.items():
            unit = "m3" if "volume" in metric else ("m2" if "area" in metric else ("kg" if "steel" in metric else ""))
            print(f"    {metric}: {value} {unit}")
    
    # Test multi-dimensional grouping
    print("\n[6] Testing Multi-Dimensional Grouping (Material + Type)...")
    stepC_multi = run_layer4_stepC(step2_result, stepB_result, 
                                    group_by_fields=["material", "type"])
    
    print(f"  Groups created: {stepC_multi['summary']['total_groups']}")
    print(f"  Group keys:")
    for group_key in stepC_multi["aggregation"].keys():
        print(f"    - {group_key}")
    
    # Test complete pipeline
    print("\n[7] Testing Complete Pipeline (All Steps)...")
    complete_result = run_layer4_pipeline(
        sample_layer3_output,
        include_reinforcement=True,
        include_aggregation=True,
        group_by_fields=["material"]
    )
    
    print(f"  Pipeline success: {complete_result['success']}")
    print(f"  Total measurements: {len(complete_result['measurements'])}")
    print(f"  Total reinforcement: {len(complete_result['reinforcement'])}")
    print(f"  Total groups: {complete_result['statistics']['aggregation']['total_groups']}")
    
    # Display final aggregation
    print(f"\n  Final Aggregation:")
    for group_key, data in complete_result["aggregation"].items():
        print(f"    {group_key}: {data['quantities']}")
    
    # Get specific metrics
    print("\n[8] Querying Specific Metrics...")
    total_volume = get_total_by_metric(stepC_result, "volume")
    total_steel = get_total_by_metric(stepC_result, "steel_kg")
    print(f"  Total concrete volume: {total_volume} m3")
    print(f"  Total steel: {total_steel} kg")
    
    # Save output
    print("\n[9] Saving output to layer4_stepC_output.json...")
    output = {
        "step1": step1_result,
        "step2": step2_result,
        "stepB": stepB_result,
        "stepC_by_material": stepC_result,
        "stepC_multi_dimension": stepC_multi,
        "complete_pipeline": complete_result
    }
    
    with open("layer4_stepC_output.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("\n" + "=" * 70)
    print("[OK] LAYER 4 STEP C TEST COMPLETE")
    print("=" * 70)
    print("\nKey Achievements:")
    print("  [+] Dynamic grouping (no hardcoded fields)")
    print("  [+] Configurable work categories")
    print("  [+] Multi-dimensional aggregation")
    print("  [+] Material + reinforcement combined")
    print("  [+] Extensible architecture")
    print("  [+] BOQ-ready output")
    print("\nOutput saved to: layer4_stepC_output.json")

if __name__ == "__main__":
    test_layer4_stepC()
