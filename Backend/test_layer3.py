"""Test Layer 3 - Step 1"""
import json
from app.ai.pipeline import route_preprocessing
from app.ai.layer2_boundary import load_geometry_and_compute_extents
from app.ai.layer2_text_clustering import cluster_text_dbscan
from app.ai.layer2_title_block import identify_title_block
from app.ai.layer2_legend import detect_legend_region
from app.ai.layer2_schedule import detect_schedule_tables
from app.ai.layer2_region_tagging import tag_regions
from app.ai.layer2_output import build_layer2_output
from app.ai.layer3_filter import filter_to_drawing_region
from app.ai.layer3_walls import detect_walls
from app.ai.layer3_slabs import detect_slabs
from app.ai.layer3_columns import detect_columns
from app.ai.layer3_doors_windows import detect_doors_windows
from app.ai.layer3_dimensions import parse_dimensions
from app.ai.layer3_graph import build_relationship_graph
from app.ai.layer3_materials import assign_materials

if __name__ == '__main__':
    test_file = input("Enter DXF file path: ").strip()
    
    print("="*60)
    print("TESTING LAYER 3 - STEP 1")
    print("="*60)
    
    # Run Layer 1
    print("\n[1] Running Layer 1...")
    layer1_output = route_preprocessing(test_file, 'DXF')
    print(f"Entities: {layer1_output.get('entity_count', {})}")
    
    # Run Layer 2
    print("\n[2] Running Layer 2...")
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
    
    print(f"Layer 2 complete")
    
    # Run Layer 3 Step 1
    print("\n[3] Testing STEP 1: Filter to Drawing Region...")
    filtered_result = filter_to_drawing_region(layer1_output, layer2_output)
    
    if 'error' in filtered_result:
        print(f"Error: {filtered_result['error']}")
    else:
        print(f"Filtering complete:")
        print(f"  -> Total entities: {filtered_result['total_entities']}")
        print(f"  -> Drawing entities: {filtered_result['drawing_entities_count']}")
        print(f"  -> Filtered out: {filtered_result['filtered_out_count']}")
        print(f"  -> Retention rate: {filtered_result['statistics']['retention_rate']:.2%}")
        print(f"  -> Buffer size: {filtered_result['drawing_polygon']['buffer_size']:.4f}")
        print(f"  -> Entity types in drawing:")
        for etype, count in filtered_result['statistics']['entity_types'].items():
            print(f"     {etype}: {count}")
    
    # Run Layer 3 Step 2
    print("\n[4] Testing STEP 2: Wall Detection...")
    scale_info = layer2_output.get('scale_info')
    walls_result = detect_walls(filtered_result.get('entities', []), scale_info)
    
    print(f"Wall detection complete:")
    print(f"  -> Total walls: {walls_result['statistics']['total_walls']}")
    print(f"  -> Double-line walls: {walls_result['statistics']['double_line_count']}")
    print(f"  -> Polyline walls: {walls_result['statistics']['polyline_count']}")
    print(f"  -> Learned thickness: {walls_result['learned_thickness']:.4f}" if walls_result['learned_thickness'] else "  -> Learned thickness: None")
    print(f"  -> Candidate lines: {walls_result['statistics']['candidate_lines']}")
    
    if walls_result['double_line_walls']:
        print(f"  -> Sample walls:")
        for wall in walls_result['double_line_walls'][:3]:
            print(f"     Wall: length={wall['length']:.2f}, thickness={wall['thickness']:.3f}, layer={wall['layer']}")
    
    # Run Layer 3 Step 3
    print("\n[5] Testing STEP 3: Slab Detection...")
    slabs_result = detect_slabs(filtered_result.get('entities', []), 
                                walls_result.get('double_line_walls', []))
    
    print(f"Slab detection complete:")
    print(f"  -> Total slabs: {slabs_result['statistics']['total_slabs']}")
    print(f"  -> Candidates: {slabs_result['statistics']['candidates']}")
    if 'large_polygons' in slabs_result['statistics']:
        print(f"  -> Large polygons: {slabs_result['statistics']['large_polygons']}")
    
    if slabs_result['slabs']:
        print(f"  -> Detected slabs:")
        for slab in slabs_result['slabs']:
            print(f"     Slab: area={slab['area']:.2f}, walls_inside={slab['walls_inside']}, confidence={slab['confidence']}, layer={slab['layer']}")
    
    # Run Layer 3 Step 4
    print("\n[6] Testing STEP 4: Column Detection...")
    columns_result = detect_columns(filtered_result.get('entities', []),
                                    slabs_result.get('slabs', []),
                                    walls_result.get('double_line_walls', []))
    
    print(f"Column detection complete:")
    print(f"  -> Total columns: {columns_result['statistics']['total_columns']}")
    print(f"  -> Candidates: {columns_result['statistics']['candidates']}")
    if 'repeated_patterns' in columns_result['statistics']:
        print(f"  -> Repeated patterns: {columns_result['statistics']['repeated_patterns']}")
    
    if columns_result['columns']:
        print(f"  -> Detected columns:")
        for col in columns_result['columns'][:5]:
            print(f"     Column: area={col['area']:.3f}, aspect_ratio={col['aspect_ratio']:.2f}, confidence={col['confidence']}, grid_aligned={col['grid_aligned']}")
    
    # Run Layer 3 Step 5
    print("\n[7] Testing STEP 5: Door & Window Detection...")
    dw_result = detect_doors_windows(layer1_output, layer2_output,
                                     walls_result.get('double_line_walls', []),
                                     walls_result.get('learned_thickness'))
    
    print(f"Door & Window detection complete:")
    print(f"  -> Total doors: {dw_result['statistics']['total_doors']}")
    print(f"  -> Total windows: {dw_result['statistics']['total_windows']}")
    print(f"  -> Text candidates: {dw_result['statistics']['text_candidates']}")
    if 'validated_codes' in dw_result['statistics']:
        print(f"  -> Validated codes: {dw_result['statistics']['validated_codes']}")
    
    if dw_result['doors']:
        print(f"  -> Detected doors:")
        for door in dw_result['doors'][:3]:
            print(f"     {door['code']}: confidence={door['confidence']}, has_arc={door['has_arc']}, wall_dist={door['wall_distance']:.3f}")
    
    if dw_result['windows']:
        print(f"  -> Detected windows:")
        for window in dw_result['windows'][:3]:
            print(f"     {window['code']}: confidence={window['confidence']}, wall_dist={window['wall_distance']:.3f}")
    
    # Run Layer 3 Step 6
    print("\n[8] Testing STEP 6: Dimension Parsing...")
    dim_result = parse_dimensions(layer1_output,
                                  walls_result.get('double_line_walls', []),
                                  slabs_result.get('slabs', []),
                                  layer2_output.get('scale_info'),
                                  walls_result.get('learned_thickness'))
    
    print(f"Dimension parsing complete:")
    print(f"  -> Total dimensions: {dim_result['statistics']['total_dimensions']}")
    print(f"  -> Numeric candidates: {dim_result['statistics']['numeric_candidates']}")
    if 'overrides_applied' in dim_result['statistics']:
        print(f"  -> Overrides applied: {dim_result['statistics']['overrides_applied']}")
    
    if dim_result['dimensions']:
        print(f"  -> Parsed dimensions:")
        for dim in dim_result['dimensions'][:5]:
            print(f"     {dim['value']:.0f}{dim['unit']} -> {dim['linked_entity_type']} {dim['dimension_type']}, confidence={dim['confidence']:.2f}, diff={dim['difference']:.1f}")
    
    # Run Layer 3 Step 7
    print("\n[9] Testing STEP 7: Relationship Graph Construction...")
    graph_result = build_relationship_graph(
        walls_result.get('double_line_walls', []),
        slabs_result.get('slabs', []),
        columns_result.get('columns', []),
        dw_result.get('doors', []),
        dw_result.get('windows', [])
    )
    
    print(f"Relationship graph complete:")
    print(f"  -> Nodes: {graph_result['statistics']['nodes']}")
    print(f"  -> Edges: {graph_result['statistics']['edges']}")
    print(f"  -> Door-Wall links: {graph_result['statistics']['door_wall_links']}")
    print(f"  -> Column-Slab links: {graph_result['statistics']['column_slab_links']}")
    print(f"  -> Wall junctions: {graph_result['statistics']['wall_junctions']}")
    print(f"  -> Connected components: {graph_result['statistics']['connected_components']}")
    print(f"  -> Tolerance: {graph_result['tolerance']:.4f}")
    print(f"  -> Validation: {'PASS' if graph_result['validation']['valid'] else 'WARNINGS'}")
    
    if graph_result['validation']['warnings']:
        print(f"  -> Warnings:")
        for warning in graph_result['validation']['warnings'][:5]:
            print(f"     - {warning}")
    
    # Run Layer 3 Step 8
    print("\n[10] Testing STEP 8: Material Assignment...")
    material_result = assign_materials(
        walls_result.get('double_line_walls', []),
        slabs_result.get('slabs', []),
        columns_result.get('columns', []),
        layer2_output.get('legend_dictionary', {}),
        layer2_output.get('schedules', {}),
        graph_result.get('graph')
    )
    
    print(f"Material assignment complete:")
    print(f"  -> Total elements: {material_result['statistics']['total_elements']}")
    print(f"  -> Average confidence: {material_result['statistics']['average_confidence']:.2f}")
    print(f"  -> Material distribution: {material_result['statistics']['material_distribution']}")
    print(f"  -> Evidence sources: {material_result['statistics']['evidence_source_usage']}")
    print(f"  -> Material catalog size: {len(material_result['material_catalog'])}")
    
    # Save results
    print("\n[11] Saving results...")
    output = {
        'layer1_summary': layer1_output.get('entity_count', {}),
        'layer2_summary': {
            'title_block': 'found' if layer2_output.get('title_block_region') else 'not_found',
            'scale': layer2_output.get('scale_info'),
            'schedules': len(layer2_output.get('schedules', {}))
        },
        'layer3_step1': {
            'total_entities': filtered_result['total_entities'],
            'drawing_entities_count': filtered_result['drawing_entities_count'],
            'filtered_out_count': filtered_result['filtered_out_count'],
            'retention_rate': filtered_result['statistics']['retention_rate'],
            'buffer_size': filtered_result['drawing_polygon']['buffer_size'],
            'entity_types': filtered_result['statistics']['entity_types']
        },
        'layer3_step2': walls_result['statistics'],
        'layer3_step3': {
            'total_slabs': slabs_result['statistics']['total_slabs'],
            'candidates': slabs_result['statistics']['candidates']
        },
        'layer3_step4': {
            'total_columns': columns_result['statistics']['total_columns'],
            'candidates': columns_result['statistics']['candidates']
        },
        'layer3_step5': {
            'total_doors': dw_result['statistics']['total_doors'],
            'total_windows': dw_result['statistics']['total_windows'],
            'text_candidates': dw_result['statistics']['text_candidates']
        },
        'layer3_step6': {
            'total_dimensions': dim_result['statistics']['total_dimensions'],
            'numeric_candidates': dim_result['statistics']['numeric_candidates']
        },
        'layer3_step7': graph_result['statistics'],
        'layer3_step8': material_result['statistics']
    }
    
    with open('layer3_test_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("Results saved to: layer3_test_results.json")
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
