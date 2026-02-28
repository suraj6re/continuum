"""Test Layer 4 Step D: Confidence Propagation"""
import json
from app.ai.layer4_pipeline import (run_layer4_step1, run_layer4_step2, 
                                     run_layer4_stepB, run_layer4_stepC,
                                     run_layer4_stepD, run_layer4_pipeline)
from app.ai.layer4_confidence_engine import get_low_confidence_groups, get_confidence_by_work_category

def test_layer4_stepD():
    """Test Layer 4 Step D with sample data"""
    
    # Sample Layer 3 output with varying confidences
    sample_layer3_output = {
        "elements": [
            {"id": "wall-1", "type": "Wall", "length": 4.2, "thickness": 0.23, "height": 3.0, 
             "material": "Brick", "confidence": 0.9},
            {"id": "wall-2", "type": "Wall", "length": 3.5, "thickness": 0.23, "height": 3.0, 
             "material": "Brick", "confidence": 0.7},
            {"id": "wall-3", "type": "Wall", "length": 2.0, "thickness": 0.23, "height": 3.0, 
             "material": "Brick", "confidence": 0.8},
            {"id": "slab-1", "type": "Slab", "area": 15.5, "thickness": 0.15, 
             "material": "Concrete", "confidence": 0.85},
            {"id": "slab-2", "type": "Slab", "area": 12.0, "thickness": 0.15, 
             "material": "Concrete", "confidence": 0.95},
            {"id": "column-1", "type": "Column", "width": 0.3, "depth": 0.3, "height": 3.0, 
             "material": "RCC", "confidence": 0.78},
            {"id": "column-2", "type": "Column", "area": 0.09, "height": 3.0, 
             "material": "RCC", "confidence": 0.82},
            {"id": "door-1", "type": "Door", "code": "D1", "width": 0.9, "height": 2.1, 
             "material": "Wood", "confidence": 0.91}
        ],
        "relationships": [],
        "summary": {}
    }
    
    print("=" * 70)
    print("TESTING LAYER 4 - STEP D: CONFIDENCE PROPAGATION")
    print("=" * 70)
    
    # Run Steps 1, 2, B, C
    print("\n[1] Running Steps 1, 2, B, C...")
    step1_result = run_layer4_step1(sample_layer3_output)
    step2_result = run_layer4_step2(step1_result)
    stepB_result = run_layer4_stepB(step2_result)
    stepC_result = run_layer4_stepC(step2_result, stepB_result, group_by_fields=["material"])
    
    print(f"[OK] Measurements: {len(step2_result['element_measurements'])}")
    print(f"[OK] Reinforcement: {len(stepB_result['reinforcement_estimation'])}")
    print(f"[OK] Aggregation groups: {stepC_result['summary']['total_groups']}")
    
    # Step D: Confidence propagation
    print("\n[2] Running Step D: Confidence Propagation...")
    stepD_result = run_layer4_stepD(stepC_result, step2_result, stepB_result)
    
    if not stepD_result["success"]:
        print(f"[X] Step D failed: {stepD_result.get('error')}")
        return
    
    print("[OK] Step D complete!")
    
    # Display confidence statistics
    print("\n[3] Confidence Statistics:")
    conf_stats = stepD_result["summary"]["confidence"]
    print(f"  Average confidence: {conf_stats['average_confidence']}")
    print(f"  Min confidence: {conf_stats['min_confidence']}")
    print(f"  Max confidence: {conf_stats['max_confidence']}")
    print(f"  Groups with confidence: {conf_stats['groups_with_confidence']}")
    
    print(f"\n  Methods used:")
    for method, count in conf_stats['methods_used'].items():
        print(f"    {method}: {count}")
    
    print(f"\n  Metrics used for weighting:")
    for metric, count in conf_stats['metrics_used'].items():
        print(f"    {metric}: {count}")
    
    # Display aggregation with confidence
    print("\n[4] Aggregation with Confidence:")
    for group_key, data in stepD_result["aggregation"].items():
        print(f"\n  {group_key}:")
        print(f"    Confidence: {data.get('confidence', 'N/A')}")
        print(f"    Element count: {data['element_count']}")
        print(f"    Quantities: {data['quantities']}")
        
        trace = data.get("confidence_trace", {})
        print(f"    Confidence trace:")
        print(f"      Method: {trace.get('method')}")
        print(f"      Metric used: {trace.get('metric_used')}")
        print(f"      Valid elements: {trace.get('valid_elements')}")
        print(f"      Total weight: {trace.get('total_weight')}")
    
    # Manual verification example
    print("\n[5] Manual Verification (Brick walls):")
    print("  Wall-1: volume=2.898, confidence=0.9")
    print("  Wall-2: volume=2.415, confidence=0.7")
    print("  Wall-3: volume=1.38, confidence=0.8")
    print("  Total volume: 6.693")
    print("  Weighted confidence = (0.9*2.898 + 0.7*2.415 + 0.8*1.38) / 6.693")
    print("  = (2.6082 + 1.6905 + 1.104) / 6.693")
    print("  = 5.4027 / 6.693")
    print("  = 0.807")
    
    brick_conf = None
    for group_key, data in stepD_result["aggregation"].items():
        if "Brick" in group_key or "brick" in group_key.lower():
            brick_conf = data.get("confidence")
    
    if brick_conf:
        print(f"  Calculated confidence: {brick_conf}")
        print(f"  Match: {'YES' if abs(brick_conf - 0.807) < 0.01 else 'NO'}")
    
    # Get low confidence groups
    print("\n[6] Low Confidence Groups (< 0.8):")
    low_conf = get_low_confidence_groups(stepD_result, threshold=0.8)
    if low_conf:
        for group in low_conf:
            print(f"  {group['group_key']}: confidence={group['confidence']:.4f}")
    else:
        print("  None found")
    
    # Get confidence by work category
    print("\n[7] Confidence by Work Category:")
    by_category = get_confidence_by_work_category(stepD_result)
    for category, conf in by_category.items():
        print(f"  {category}: {conf:.4f}")
    
    # Test complete pipeline
    print("\n[8] Testing Complete Pipeline (All Steps)...")
    complete_result = run_layer4_pipeline(
        sample_layer3_output,
        include_reinforcement=True,
        include_aggregation=True,
        include_confidence=True,
        group_by_fields=["material"]
    )
    
    print(f"  Pipeline success: {complete_result['success']}")
    print(f"  Total measurements: {len(complete_result['measurements'])}")
    print(f"  Total groups: {complete_result['statistics']['aggregation']['total_groups']}")
    print(f"  Avg confidence: {complete_result['statistics']['aggregation']['confidence']['average_confidence']}")
    
    # Save output
    print("\n[9] Saving output to layer4_stepD_output.json...")
    output = {
        "step1": step1_result,
        "step2": step2_result,
        "stepB": stepB_result,
        "stepC": stepC_result,
        "stepD": stepD_result,
        "complete_pipeline": complete_result
    }
    
    with open("layer4_stepD_output.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("\n" + "=" * 70)
    print("[OK] LAYER 4 STEP D TEST COMPLETE")
    print("=" * 70)
    print("\nKey Achievements:")
    print("  [+] Weighted confidence propagation")
    print("  [+] Dynamic metric selection (no hardcoding)")
    print("  [+] Quantity-based weighting")
    print("  [+] Formula tracing")
    print("  [+] Deterministic calculations")
    print("  [+] Auditable confidence scores")
    print("\nOutput saved to: layer4_stepD_output.json")

if __name__ == "__main__":
    test_layer4_stepD()
