"""Test Layer 4 Step 1: Graph Validation + Normalization"""
import json
from app.ai.layer4_pipeline import run_layer4_step1, get_measurable_elements, get_elements_by_type

def test_layer4_step1():
    """Test Layer 4 Step 1 with sample data"""
    
    # Sample Layer 3 output (minimal structure)
    sample_layer3_output = {
        "elements": [
            {
                "id": "wall-1",
                "type": "Wall",
                "length": 4.2,
                "thickness": 0.23,
                "material": "Brick",
                "confidence": 0.88
            },
            {
                "id": "wall-2",
                "type": "Wall",
                "length": 3.5,
                "thickness": 0.23,
                "height": 3.0,
                "material": "Brick",
                "confidence": 0.92
            },
            {
                "id": "slab-1",
                "type": "Slab",
                "area": 15.5,
                "material": "Concrete",
                "confidence": 0.85
            },
            {
                "id": "column-1",
                "type": "Column",
                "width": 0.3,
                "depth": 0.3,
                "material": "RCC",
                "confidence": 0.78
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
        "relationships": [
            {"source": "door-1", "target": "wall-1", "type": "attached_to"},
            {"source": "window-1", "target": "wall-2", "type": "attached_to"}
        ],
        "summary": {
            "total_walls": 3,
            "total_slabs": 1,
            "total_columns": 1,
            "total_doors": 1,
            "total_windows": 1
        }
    }
    
    print("=" * 70)
    print("TESTING LAYER 4 - STEP 1: GRAPH VALIDATION + NORMALIZATION")
    print("=" * 70)
    
    # Run Layer 4 Step 1
    print("\n[1] Running validation, normalization, and preprocessing...")
    result = run_layer4_step1(sample_layer3_output, default_height=3.0)
    
    if not result["success"]:
        print(f"\n[X] Processing failed: {result.get('error')}")
        return
    
    print("[OK] Processing successful!")
    
    # Display statistics
    print("\n[2] Statistics:")
    stats = result["statistics"]
    print(f"  Total input elements: {stats['total_input']}")
    print(f"  Successfully processed: {stats['total_processed']}")
    print(f"  Errors: {stats['total_errors']}")
    print(f"  Measurable elements: {stats['measurable_elements']}")
    print(f"  High quality elements: {stats['high_quality_elements']}")
    print(f"  Requires review: {stats['requires_review']}")
    print(f"  Success rate: {stats['success_rate']:.1%}")
    
    # Display errors if any
    if result["errors"]:
        print("\n[3] Errors encountered:")
        for error in result["errors"]:
            print(f"  - {error['id']} ({error['type']}): {error['error']}")
    
    # Display processed elements
    print("\n[4] Processed Elements:")
    for elem in result["elements"]:
        print(f"\n  {elem['id']} ({elem['type']}):")
        print(f"    Confidence: {elem['confidence']:.2f}")
        print(f"    Quality Score: {elem.get('quality_score', 0):.2f}")
        print(f"    Measurable: {elem.get('is_measurable', False)}")
        print(f"    Measurement Basis: {elem.get('measurement_basis', 'N/A')}")
        print(f"    Requires Review: {elem.get('requires_review', False)}")
        print(f"    Has Defaults: {elem.get('has_defaults', False)}")
        
        # Show key dimensions
        if elem['type'] == 'Wall':
            print(f"    Dimensions: L={elem.get('length', 0):.2f}m, T={elem.get('thickness', 0):.3f}m, H={elem.get('height', 0):.2f}m")
            if elem.get('height_source') == 'default':
                print(f"    [!] Height assigned from default")
        elif elem['type'] == 'Slab':
            print(f"    Area: {elem.get('area', 0):.2f}m², Thickness: {elem.get('thickness', 0):.3f}m")
            if elem.get('thickness_source') == 'default':
                print(f"    [!] Thickness assigned from default")
        elif elem['type'] == 'Column':
            print(f"    Area: {elem.get('area', 0):.3f}m², Height: {elem.get('height', 0):.2f}m")
            if elem.get('area_source') == 'computed':
                print(f"    [i] Area computed from width x depth")
        elif elem['type'] in ['Door', 'Window']:
            print(f"    Dimensions: W={elem.get('width', 0):.2f}m × H={elem.get('height', 0):.2f}m")
            if elem.get('width_source') == 'default' or elem.get('height_source') == 'default':
                print(f"    [!] Dimensions assigned from defaults")
    
    # Get measurable elements only
    print("\n[5] Measurable Elements Only:")
    measurable = get_measurable_elements(result)
    print(f"  Total: {len(measurable)}")
    for elem in measurable:
        print(f"  - {elem['id']} ({elem['type']}): confidence={elem['confidence']:.2f}, quality={elem['quality_score']:.2f}")
    
    # Get elements by type
    print("\n[6] Elements by Type:")
    for elem_type in ["Wall", "Slab", "Column", "Door", "Window"]:
        elements = get_elements_by_type(result, elem_type)
        print(f"  {elem_type}s: {len(elements)}")
    
    # Save output
    print("\n[7] Saving output to layer4_step1_output.json...")
    with open("layer4_step1_output.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print("\n" + "=" * 70)
    print("[OK] LAYER 4 STEP 1 TEST COMPLETE")
    print("=" * 70)
    print("\nOutput saved to: layer4_step1_output.json")
    print("\nNext: Layer 4 Step 2 - Volume Computation")

if __name__ == "__main__":
    test_layer4_step1()
