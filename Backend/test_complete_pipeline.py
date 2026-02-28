"""Test Complete 3-Layer Pipeline"""
import json
from app.ai.pipeline import route_preprocessing
from app.ai.layer2_boundary import load_geometry_and_compute_extents
from app.ai.layer2_text_clustering import cluster_text_dbscan
from app.ai.layer2_title_block import identify_title_block
from app.ai.layer2_legend import detect_legend_region
from app.ai.layer2_schedule import detect_schedule_tables
from app.ai.layer2_region_tagging import tag_regions
from app.ai.layer2_output import build_layer2_output
from app.ai.layer3_pipeline import run_layer3_pipeline

if __name__ == '__main__':
    test_file = input("Enter DXF file path: ").strip()
    
    print("="*60)
    print("TESTING COMPLETE 3-LAYER PIPELINE")
    print("="*60)
    
    # Layer 1
    print("\n[Layer 1] Geometry Extraction...")
    layer1_output = route_preprocessing(test_file, 'DXF')
    print(f"✓ Entities: {layer1_output.get('entity_count', {})}")
    
    # Layer 2
    print("\n[Layer 2] Semantic Understanding...")
    text_entities = layer1_output.get('text', [])
    all_lines, extents = load_geometry_and_compute_extents(layer1_output)
    sheet_border = layer1_output.get('sheet_border')
    
    if len(text_entities) >= 4:
        labels, params = cluster_text_dbscan(text_entities)
        title_block = identify_title_block(text_entities, labels)
        legend_info = detect_legend_region(text_entities, labels, layer1_output)
        tables = detect_schedule_tables(layer1_output, text_entities)
        region_tags = tag_regions(text_entities, title_block, legend_info, tables, sheet_border)
        layer2_output = build_layer2_output(sheet_border, title_block, legend_info, 
                                            tables, region_tags, layer1_output)
    else:
        layer2_output = {'drawing_region': {'bbox': sheet_border}}
    
    print(f"✓ Title block: {'Found' if layer2_output.get('title_block_region') else 'Not found'}")
    print(f"✓ Scale: {layer2_output.get('scale_info', {}).get('ratio', 'Not found')}")
    
    # Layer 3
    print("\n[Layer 3] Structural Element Detection...")
    layer3_output = run_layer3_pipeline(layer1_output, layer2_output)
    
    if 'error' in layer3_output:
        print(f"✗ Error: {layer3_output['error']}")
    else:
        print(f"✓ Elements detected: {layer3_output['summary']['total_elements']}")
        print(f"  - Walls: {layer3_output['summary']['total_walls']}")
        print(f"  - Slabs: {layer3_output['summary']['total_slabs']}")
        print(f"  - Columns: {layer3_output['summary']['total_columns']}")
        print(f"  - Doors: {layer3_output['summary']['total_doors']}")
        print(f"  - Windows: {layer3_output['summary']['total_windows']}")
        print(f"✓ Relationships: {len(layer3_output['relationships'])}")
        print(f"✓ Avg confidence: {layer3_output['summary']['avg_confidence']}")
        print(f"✓ Flagged for review: {layer3_output['summary']['flagged_count']}")
        
        # Show sample elements
        print("\n[Sample Elements]")
        for elem in layer3_output['elements'][:3]:
            print(f"  {elem['type']} {elem['id']}: confidence={elem['confidence']}")
    
    # Save output
    print("\n[Saving Results]")
    with open('final_output.json', 'w') as f:
        json.dump(layer3_output, f, indent=2)
    
    print("✓ Saved to: final_output.json")
    print("\n" + "="*60)
    print("PIPELINE COMPLETE")
    print("="*60)
