"""Test Layer 2 - Step 1 & Step 2"""
import json
from app.ai.pipeline import route_preprocessing
from app.ai.layer2_boundary import load_geometry_and_compute_extents
from app.ai.layer2_text_clustering import cluster_text_dbscan

if __name__ == '__main__':
    from app.ai.layer2_title_block import identify_title_block
    
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
        else:
            print("No title block identified")
    else:
        print(f"Not enough text entities ({len(text_entities)} < 4)")
        n_clusters = 0
        params = {}
        labels = []
        title_block = None
    
    print("\n[5] Saving test results...")
    output = {
        'step1_sheet_border': sheet_border,
        'step1_total_lines': len(all_lines),
        'step1_extents': extents,
        'step2_clusters': n_clusters,
        'step2_params': params,
        'step2_labels': labels.tolist() if len(text_entities) >= 4 else [],
        'title_block': title_block
    }
    
    with open('layer2_test_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("Results saved to: layer2_test_results.json")
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
