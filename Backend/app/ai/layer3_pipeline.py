from typing import Dict
from app.ai.layer3_filter import filter_to_drawing_region
from app.ai.layer3_walls import detect_walls
from app.ai.layer3_slabs import detect_slabs
from app.ai.layer3_columns import detect_columns
from app.ai.layer3_doors_windows import detect_doors_windows
from app.ai.layer3_dimensions import parse_dimensions
from app.ai.layer3_graph import build_relationship_graph
from app.ai.layer3_materials import assign_materials
from app.ai.layer3_confidence import compute_confidence_scores
from app.ai.layer3_output import build_layer3_output

def run_layer3_pipeline(layer1_output: Dict, layer2_output: Dict) -> Dict:
    """Run complete Layer 3 pipeline
    
    Args:
        layer1_output: Layer 1 results (geometry extraction)
        layer2_output: Layer 2 results (semantic understanding)
    
    Returns:
        Final structured output with elements, relationships, and summary
    """
    
    # Step 1: Filter to drawing region
    filtered = filter_to_drawing_region(layer1_output, layer2_output)
    if 'error' in filtered:
        return {'error': filtered['error']}
    
    entities = filtered.get('entities', [])
    scale_info = layer2_output.get('scale_info')
    
    # Step 2: Detect walls
    walls_result = detect_walls(entities, scale_info)
    walls = walls_result.get('double_line_walls', []) + walls_result.get('polyline_walls', [])
    learned_thickness = walls_result.get('learned_thickness')
    
    # Step 3: Detect slabs
    slabs_result = detect_slabs(entities, walls)
    slabs = slabs_result.get('slabs', [])
    
    # Step 4: Detect columns
    columns_result = detect_columns(entities, slabs, walls)
    columns = columns_result.get('columns', [])
    
    # Step 5: Detect doors & windows
    dw_result = detect_doors_windows(layer1_output, layer2_output, walls, learned_thickness)
    doors = dw_result.get('doors', [])
    windows = dw_result.get('windows', [])
    
    # Step 6: Parse dimensions
    dimensions_result = parse_dimensions(layer1_output, walls, slabs, scale_info, learned_thickness)
    dimensions = dimensions_result.get('dimensions', [])
    
    # Step 7: Build relationship graph
    graph_result = build_relationship_graph(walls, slabs, columns, doors, windows)
    
    # Step 8: Assign materials
    material_result = assign_materials(
        walls, slabs, columns,
        layer2_output.get('legend_dictionary', {}),
        layer2_output.get('schedules', {}),
        graph_result.get('graph')
    )
    
    # Update elements with materials
    walls = material_result.get('walls', walls)
    slabs = material_result.get('slabs', slabs)
    columns = material_result.get('columns', columns)
    
    # Step 9: Compute confidence scores
    confidence_result = compute_confidence_scores(
        walls, slabs, columns, doors, windows,
        graph_result.get('graph'), dimensions
    )
    
    # Step 10: Build final output
    final_output = build_layer3_output(
        walls, slabs, columns, doors, windows,
        confidence_result, graph_result, material_result
    )
    
    return final_output
