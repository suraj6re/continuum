"""Test Layer 4 Step B: Reinforcement Estimation"""
import json
from app.ai.layer4_pipeline import run_layer4_step1, run_layer4_step2, run_layer4_stepB, run_layer4_pipeline
from app.ai.layer4_reinforcement_config import load_project_config

def test_layer4_stepB():
    """Test Layer 4 Step B with sample data"""
    
    # Sample Layer 3 output
    sample_layer3_output = {
        "elements": [
            {
                "id": "slab-1",
                "type": "Slab",
                "area": 15.5,
                "thickness": 0.15,
                "material": "Concrete",
                "confidence": 0.85
            },
            {
                "id": "column-1",
                "type": "Column",
                "width": 0.3,
                "depth": 0.3,
                "height": 3.0,
                "material": "RCC",
                "confidence": 0.78
            },
            {
                "id": "column-2",
                "type": "Column",
                "area": 0.09,
                "height": 3.0,
                "material": "RCC",
                "confidence": 0.82
            },
            {
                "id": "wall-1",
                "type": "Wall",
                "length": 4.2,
                "thickness": 0.23,
                "height": 3.0,
                "material": "Brick",
                "confidence": 0.88
            },
            {
                "id": "wall-2",
                "type": "Wall",
                "length": 3.5,
                "thickness": 0.23,
                "height": 3.0,
                "material": "RCC",
                "confidence": 0.92
            },
            {
                "id": "door-1",
                "type": "Door",
                "code": "D1",
                "width": 0.9,
                "height": 2.1,
                "material": "Wood",
                "confidence": 0.91
            }
        ],
        "relationships": [],
        "summary": {}
    }
    
    print("=" * 70)
    print("TESTING LAYER 4 - STEP B: REINFORCEMENT ESTIMATION")
    print("=" * 70)
    
    # Step 1: Validate and normalize
    print("\n[1] Running Step 1: Validation + Normalization...")
    step1_result = run_layer4_step1(sample_layer3_output)
    print(f"[OK] Step 1 complete")
    
    # Step 2: Calculate measurements
    print("\n[2] Running Step 2: Measurement Calculation...")
    step2_result = run_layer4_step2(step1_result)
    print(f"[OK] Step 2 complete: {len(step2_result['element_measurements'])} measurements")
    
    # Step B: Reinforcement estimation (default ratios)
    print("\n[3] Running Step B: Reinforcement Estimation (Default Ratios)...")
    stepB_result = run_layer4_stepB(step2_result)
    
    if not stepB_result["success"]:
        print(f"[X] Step B failed: {stepB_result.get('error')}")
        return
    
    print("[OK] Step B complete!")
    
    # Display statistics
    print("\n[4] Reinforcement Statistics:")
    stats = stepB_result["statistics"]
    print(f"  Total elements: {stats['total_elements']}")
    print(f"  Estimated: {stats['estimated_elements']}")
    print(f"  Skipped: {stats['skipped_elements']}")
    print(f"  Success rate: {stats['success_rate']:.1%}")
    print(f"  Total steel: {stats['total_steel_kg']:.2f} kg")
    
    print(f"\n  Steel by Type:")
    for elem_type, steel_kg in stats['steel_by_type'].items():
        print(f"    {elem_type}: {steel_kg:.2f} kg")
    
    print(f"\n  Quality:")
    print(f"    Avg Quality Score: {stats['quality']['average_quality_score']:.3f}")
    print(f"    Avg Confidence: {stats['quality']['average_confidence']:.3f}")
    
    print(f"\n  Ratio Sources:")
    for source, count in stats['ratio_sources'].items():
        print(f"    {source}: {count}")
    
    # Display reinforcement estimations
    print("\n[5] Reinforcement Estimations:")
    for estimation in stepB_result["reinforcement_estimation"]:
        print(f"\n  {estimation['element_id']} ({estimation['type']}):")
        print(f"    Steel: {estimation['reinforcement']['steel_kg']} kg")
        print(f"    Ratio: {estimation['reinforcement']['ratio_used']} kg/m3")
        print(f"    Formula: {estimation['formula_trace']['formula']}")
        print(f"    Calculation: {estimation['formula_trace']['calculation']}")
        print(f"    Method: {estimation['formula_trace']['method']}")
        print(f"    Ratio Source: {estimation['formula_trace']['ratio_source']}")
    
    # Display skipped elements
    if stepB_result["skipped"]:
        print("\n[6] Skipped Elements:")
        for skipped in stepB_result["skipped"]:
            print(f"  - {skipped['element_id']} ({skipped['type']}): {skipped['reason']}")
    
    # Test with project-specific config
    print("\n[7] Testing with Project-Specific Config...")
    project_config = load_project_config({
        "Slab": {"steel_ratio": 90, "description": "High-rise building slab"},
        "Column": 140,  # Simple format
        "Wall": {"steel_ratio": 70}
    })
    
    stepB_custom = run_layer4_stepB(step2_result, project_config)
    
    print(f"  Custom config applied:")
    print(f"  Total steel: {stepB_custom['statistics']['total_steel_kg']:.2f} kg")
    print(f"  Difference: {stepB_custom['statistics']['total_steel_kg'] - stats['total_steel_kg']:.2f} kg")
    
    print(f"\n  Custom ratios used:")
    for estimation in stepB_custom["reinforcement_estimation"]:
        if estimation['formula_trace']['ratio_source'] == 'project_config':
            print(f"    {estimation['element_id']}: {estimation['reinforcement']['ratio_used']} kg/m3 (custom)")
    
    # Test complete pipeline
    print("\n[8] Testing Complete Pipeline (Step 1 + 2 + B)...")
    complete_result = run_layer4_pipeline(
        sample_layer3_output,
        include_reinforcement=True,
        reinforcement_config=project_config
    )
    
    print(f"  Pipeline success: {complete_result['success']}")
    print(f"  Total measurements: {len(complete_result['measurements'])}")
    print(f"  Total reinforcement: {len(complete_result['reinforcement'])}")
    print(f"  Total steel: {complete_result['statistics']['reinforcement']['total_steel_kg']:.2f} kg")
    
    # Save output
    print("\n[9] Saving output to layer4_stepB_output.json...")
    output = {
        "step1": step1_result,
        "step2": step2_result,
        "stepB_default": stepB_result,
        "stepB_custom": stepB_custom,
        "complete_pipeline": complete_result
    }
    
    with open("layer4_stepB_output.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("\n" + "=" * 70)
    print("[OK] LAYER 4 STEP B TEST COMPLETE")
    print("=" * 70)
    print("\nKey Achievements:")
    print("  [+] Ratio-based estimation (no bar parsing)")
    print("  [+] Configurable ratios (not hardcoded)")
    print("  [+] Project-level overrides supported")
    print("  [+] Formula trace recorded")
    print("  [+] Deterministic calculations")
    print("  [+] Industry-acceptable method")
    print("\nOutput saved to: layer4_stepB_output.json")

if __name__ == "__main__":
    test_layer4_stepB()
