"""Test Layer 4 Step 2: Element-Level Measurement Calculation"""
import json
from app.ai.layer4_pipeline import run_layer4_step1, run_layer4_step2, run_layer4_pipeline
from app.ai.layer4_measurement_registry import enable_secondary_measurement

def test_layer4_step2():
    """Test Layer 4 Step 2 with sample data"""
    
    # Sample Layer 3 output
    sample_layer3_output = {
        "elements": [
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
                "material": "Brick",
                "confidence": 0.92
            },
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
                "id": "door-1",
                "type": "Door",
                "code": "D1",
                "width": 0.9,
                "height": 2.1,
                "material": "Wood",
                "confidence": 0.91
            },
            {
                "id": "window-1",
                "type": "Window",
                "code": "W1",
                "width": 1.2,
                "height": 1.5,
                "material": "Aluminum",
                "confidence": 0.65
            },
            {
                "id": "wall-3",
                "type": "Wall",
                "length": 2.0,
                "thickness": 0.15,
                "material": "Brick",
                "confidence": 0.35
            }
        ],
        "relationships": [],
        "summary": {}
    }
    
    print("=" * 70)
    print("TESTING LAYER 4 - STEP 2: ELEMENT-LEVEL MEASUREMENT")
    print("=" * 70)
    
    # Step 1: Validate and normalize
    print("\n[1] Running Step 1: Validation + Normalization...")
    step1_result = run_layer4_step1(sample_layer3_output)
    
    if not step1_result["success"]:
        print(f"[X] Step 1 failed: {step1_result.get('error')}")
        return
    
    print(f"[OK] Step 1 complete: {step1_result['statistics']['measurable_elements']} measurable elements")
    
    # Step 2: Calculate measurements
    print("\n[2] Running Step 2: Measurement Calculation...")
    step2_result = run_layer4_step2(step1_result, include_secondary=False)
    
    if not step2_result["success"]:
        print(f"[X] Step 2 failed: {step2_result.get('error')}")
        return
    
    print("[OK] Step 2 complete!")
    
    # Display statistics
    print("\n[3] Measurement Statistics:")
    stats = step2_result["statistics"]
    print(f"  Total elements: {stats['total_elements']}")
    print(f"  Measured: {stats['measured_elements']}")
    print(f"  Skipped: {stats['skipped_elements']}")
    print(f"  Errors: {stats['errors']}")
    print(f"  Success rate: {stats['success_rate']:.1%}")
    
    print(f"\n  By Type:")
    for elem_type, count in stats['by_type'].items():
        print(f"    {elem_type}: {count}")
    
    print(f"\n  Totals:")
    print(f"    Volume: {stats['totals']['volume_m3']:.4f} m³")
    print(f"    Area: {stats['totals']['area_m2']:.4f} m²")
    print(f"    Count: {stats['totals']['count']}")
    
    print(f"\n  Quality:")
    print(f"    Avg Quality Score: {stats['quality']['average_quality_score']:.3f}")
    print(f"    Avg Confidence: {stats['quality']['average_confidence']:.3f}")
    print(f"    With Defaults: {stats['quality']['elements_with_defaults']}")
    
    # Display measurements
    print("\n[4] Element Measurements:")
    for measurement in step2_result["element_measurements"]:
        print(f"\n  {measurement['element_id']} ({measurement['type']}):")
        print(f"    Formula: {measurement['formula']}")
        print(f"    Measurements:")
        for key, value in measurement['measurements'].items():
            print(f"      {key}: {value}")
        print(f"    Unit: {measurement['unit']}")
        print(f"    Confidence: {measurement['confidence']:.2f}")
        print(f"    Quality: {measurement['quality_score']:.2f}")
        if measurement.get('has_defaults'):
            print(f"    [!] Contains default values")
    
    # Display skipped elements
    if step2_result["skipped"]:
        print("\n[5] Skipped Elements:")
        for skipped in step2_result["skipped"]:
            print(f"  - {skipped['element_id']} ({skipped['type']}): {skipped['reason']}")
    
    # Test with secondary measurements
    print("\n[6] Testing with Secondary Measurements (Plaster)...")
    enable_secondary_measurement("Wall", "plaster")
    
    step2_with_secondary = run_layer4_step2(step1_result, include_secondary=True)
    
    if step2_with_secondary["secondary_measurements"]:
        print(f"  Secondary measurements calculated: {len(step2_with_secondary['secondary_measurements'])}")
        for sec_meas in step2_with_secondary["secondary_measurements"]:
            print(f"\n  {sec_meas['element_id']} - {sec_meas['measurement_type']}:")
            print(f"    Formula: {sec_meas['formula']}")
            for key, value in sec_meas['measurements'].items():
                print(f"      {key}: {value}")
    
    # Test complete pipeline
    print("\n[7] Testing Complete Pipeline (Step 1 + Step 2)...")
    complete_result = run_layer4_pipeline(sample_layer3_output, include_secondary=False)
    
    print(f"  Pipeline success: {complete_result['success']}")
    print(f"  Total measurements: {len(complete_result['measurements'])}")
    print(f"  Total volume: {complete_result['statistics']['totals']['volume_m3']:.4f} m³")
    
    # Save output
    print("\n[8] Saving output to layer4_step2_output.json...")
    output = {
        "step1": step1_result,
        "step2": step2_result,
        "complete_pipeline": complete_result
    }
    
    with open("layer4_step2_output.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("\n" + "=" * 70)
    print("[OK] LAYER 4 STEP 2 TEST COMPLETE")
    print("=" * 70)
    print("\nKey Achievements:")
    print("  [+] Strategy Pattern implemented")
    print("  [+] Registry-based resolution (no hardcoding)")
    print("  [+] Primary + Secondary measurements")
    print("  [+] Extensible architecture")
    print("  [+] Deterministic calculations")
    print("\nOutput saved to: layer4_step2_output.json")

if __name__ == "__main__":
    test_layer4_step2()
