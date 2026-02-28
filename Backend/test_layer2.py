"""Test Layer 2 - Step 1 & Step 2"""
import json
from app.ai.pipeline import route_preprocessing
from app.ai.layer2_boundary import load_geometry_and_compute_extents
from app.ai.layer2_text_clustering import cluster_text_dbscan

if __name__ == '__main__':
    from app.ai.layer2_title_block import identify_title_block
    from app.ai.layer2_legend import detect_legend_region
    from app.ai.layer2_schedule import detect_schedule_tables
    from app.ai.layer2_region_tagging import tag_regions
    from app.ai.layer2_output import build_layer2_output
    
    test_file = input("Enter DXF file path: ").strip()
    file_type = 'DXF'
    
    print("="*60)
    print("TESTING LAYER 2 - STEP 1 & STEP 2")
    print("="*60)
    print(f"\n[1] Running Layer 1 (file type: {file_type})...")
    layer1_output = route_preprocessing(test_file, file_type)
    
    print(f"Entities: {layer1_output.get('entity_count', {})}")
    print(f"Text count: {len(layer1_output.get('text', []))}")
    
    print("\n[2] Testing STEP 1: Sheet Border Detection...")
    all_lines, extents = load_geometry_and_compute_extents(layer1_output)
    print(f"Total lines extracted: {len(all_lines)}")
    print(f"Global extents: {extents}")
    
    sheet_border = layer1_output.get('sheet_border')
    if sheet_border:
        print(f"Sheet border found: {sheet_border}")
        width = sheet_border['max_x'] - sheet_border['min_x']
        height = sheet_border['max_y'] - sheet_border['min_y']
        print(f"  -> Border dimensions: {width:.2f} x {height:.2f}")
    else:
        print("No sheet border detected")
    
    print("\n[3] Testing STEP 2: Text Clustering (DBSCAN)...")
    text_entities = layer1_output.get('text', [])
    
    if len(text_entities) >= 4:
        labels, params = cluster_text_dbscan(text_entities)
        print(f"DBSCAN params (auto-computed):")
        print(f"  -> eps: {params['eps']:.4f}")
        print(f"  -> min_samples: {params['min_samples']}")
        
        unique_labels = set(labels)
        n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
        n_noise = list(labels).count(-1)
        
        print(f"Clustering results:")
        print(f"  -> Clusters found: {n_clusters}")
        print(f"  -> Noise points: {n_noise}")
        print(f"  -> Cluster IDs: {sorted(unique_labels)}")
        
        for label in sorted(unique_labels):
            if label != -1:
                count = list(labels).count(label)
                print(f"  -> Cluster {label}: {count} texts")
        
        # NEW: Title block identification
        print("\n[4] Testing Title Block Identification...")
        title_block = identify_title_block(text_entities, labels)
        if title_block:
            print(f"Title block identified:")
            print(f"  -> Cluster ID: {title_block['cluster_id']}")
            print(f"  -> Score: {title_block['score']}")
            print(f"  -> Text count: {title_block['text_count']}")
            print(f"  -> Bounding box: {title_block['bounding_box']}")
            print(f"  -> Metadata extracted:")
            for key, value in title_block['metadata'].items():
                print(f"     {key}: {value}")
            
            # NEW: Scale extraction
            print(f"\n[5] Testing STEP 4: Scale Extraction...")
            scale_info = title_block.get('scale_info', {})
            if scale_info.get('status') == 'found':
                print(f"Scale found:")
                print(f"  -> Ratio: {scale_info['numerator']}:{scale_info['denominator']}")
                print(f"  -> Decimal: {scale_info['ratio']:.6f}")
                print(f"  -> Raw text: {scale_info['raw_text']}")
            else:
                print(f"Scale not found - needs manual override")
        else:
            print("No title block identified")
        
        # NEW: Legend detection
        print(f"\n[6] Testing STEP 5: Legend Region Detection...")
        legend_info = detect_legend_region(text_entities, labels, layer1_output)
        if legend_info and legend_info.get('status') == 'found':
            print(f"Legend region found:")
            print(f"  -> Cluster ID: {legend_info['cluster_id']}")
            print(f"  -> Score: {legend_info['score']}")
            print(f"  -> Bounding box: {legend_info['bounding_box']}")
            print(f"  -> Shape count: {legend_info['shape_count']}")
            print(f"  -> Confidence: {legend_info['confidence']}")
            print(f"  -> Legend dictionary:")
            for sig, label in legend_info['legend_dictionary'].items():
                print(f"     {sig}: {label}")
        else:
            print(f"Legend not found")
            legend_info = None
        
        # NEW: Schedule table detection
        print(f"\n[7] Testing STEP 6: Schedule Table Detection...")
        tables = detect_schedule_tables(layer1_output, text_entities)
        if tables:
            print(f"Tables found: {len(tables)}")
            for idx, table in enumerate(tables):
                print(f"\nTable {idx + 1}:")
                print(f"  -> Grid: {table['rows']}x{table['cols']}")
                print(f"  -> Grid score: {table['grid_score']}")
                print(f"  -> Bbox: {table['bbox']}")
                if table['parsed_data']:
                    print(f"  -> Headers: {table['parsed_data']['headers']}")
                    print(f"  -> Data rows: {table['parsed_data']['row_count']}")
                    for row_idx, row in enumerate(table['parsed_data']['data'][:3]):  # Show first 3 rows
                        print(f"     Row {row_idx + 1}: {row}")
        else:
            print(f"No tables found")
            tables = []
        
        # NEW: Region tagging
        print(f"\n[8] Testing STEP 7: Region Tagging...")
        region_tags = tag_regions(text_entities, title_block, legend_info, tables, sheet_border)
        print(f"Region tagging complete:")
        print(f"  -> Total texts: {region_tags['total_texts']}")
        print(f"  -> Region counts:")
        for region, count in region_tags['region_counts'].items():
            print(f"     {region}: {count}")
        print(f"  -> Tagged texts (sample):")
        for text in region_tags['tagged_texts'][:5]:  # Show first 5
            print(f"     [{text['role']}] {text['text']} at {text['position']}")
        
        # NEW: Build Layer 2 output
        print(f"\n[9] Testing STEP 8: Build Layer 2 Output...")
        layer2_output = build_layer2_output(sheet_border, title_block, legend_info, 
                                            tables, region_tags, layer1_output)
        print(f"Layer 2 output built:")
        print(f"  -> Drawing region: {layer2_output['drawing_region']['text_count']} texts")
        print(f"  -> Title block: {'Found' if layer2_output['title_block_region'] else 'Not found'}")
        print(f"  -> Scale info: {'Found' if layer2_output['scale_info'] else 'Not found'}")
        print(f"  -> Legend: {'Found' if layer2_output['legend_region'] else 'Not found'}")
        print(f"  -> Schedules: {len(layer2_output['schedules'])} tables")
        print(f"  -> Total regions processed: {len(layer2_output['region_statistics']['region_counts'])}")
    else:
        print(f"Not enough text entities ({len(text_entities)} < 4)")
        n_clusters = 0
        params = {}
        labels = []
        title_block = None
    
    print("\n[10] Saving test results...")
    output = {
        'step1_sheet_border': sheet_border,
        'step1_total_lines': len(all_lines),
        'step1_extents': extents,
        'step2_clusters': n_clusters,
        'step2_params': params,
        'step2_labels': labels.tolist() if len(text_entities) >= 4 else [],
        'title_block': title_block,
        'legend_info': legend_info,
        'schedule_tables': tables,
        'region_tags': region_tags,
        'layer2_output': layer2_output
    }
    
    with open('layer2_test_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("Results saved to: layer2_test_results.json")
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
