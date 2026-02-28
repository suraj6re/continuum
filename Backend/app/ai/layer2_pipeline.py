"""Layer 2 Pipeline - Semantic Understanding"""
from typing import Dict
from app.ai.layer2_boundary import load_geometry_and_compute_extents
from app.ai.layer2_text_clustering import cluster_text_dbscan
from app.ai.layer2_title_block import identify_title_block
from app.ai.layer2_legend import detect_legend_region
from app.ai.layer2_schedule import detect_schedule_tables
from app.ai.layer2_region_tagging import tag_regions
from app.ai.layer2_output import build_layer2_output

def run_layer2_pipeline(layer1_output: Dict) -> Dict:
    """Run complete Layer 2 semantic understanding pipeline
    
    Args:
        layer1_output: Complete Layer 1 output with geometry and text
    
    Returns:
        Layer 2 output with semantic regions and metadata
    """
    
    text_entities = layer1_output.get('text', [])
    
    # Check if we have enough text for clustering
    if len(text_entities) < 4:
        return {
            'status': 'insufficient_data',
            'message': 'Not enough text entities for semantic analysis',
            'drawing_region': {
                'bbox': layer1_output.get('bounding_box'),
                'text_count': len(text_entities),
                'texts': text_entities
            }
        }
    
    # Step 1: Compute sheet border and extents
    all_lines, extents = load_geometry_and_compute_extents(layer1_output)
    sheet_border = extents  # Use computed extents as sheet border
    
    # Step 2: Cluster text entities
    labels, params = cluster_text_dbscan(text_entities)
    
    # Step 3: Identify title block
    title_block = identify_title_block(text_entities, labels)
    
    # Step 4: Detect legend region
    legend_info = detect_legend_region(text_entities, labels, layer1_output)
    
    # Step 5: Detect schedule tables
    schedule_tables = detect_schedule_tables(layer1_output, text_entities)
    
    # Step 6: Tag all text by region
    region_tags = tag_regions(text_entities, title_block, legend_info, schedule_tables, sheet_border)
    
    # Step 7: Build structured output
    layer2_output = build_layer2_output(
        sheet_border, 
        title_block, 
        legend_info, 
        schedule_tables, 
        region_tags, 
        layer1_output
    )
    
    # Add processing metadata
    layer2_output['status'] = 'success'
    layer2_output['clustering_params'] = params
    layer2_output['total_clusters'] = len(set(labels)) - (1 if -1 in labels else 0)
    
    return layer2_output
