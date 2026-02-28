from typing import Dict, List
import uuid

def build_layer3_output(walls: List[Dict], slabs: List[Dict], columns: List[Dict],
                        doors: List[Dict], windows: List[Dict], 
                        confidence_result: Dict, graph_result: Dict,
                        material_result: Dict) -> Dict:
    """Build final Layer 3 output structure
    
    Args:
        walls: Detected walls
        slabs: Detected slabs
        columns: Detected columns
        doors: Detected doors
        windows: Detected windows
        confidence_result: Confidence scores
        graph_result: Relationship graph
        material_result: Material assignments
    
    Returns:
        Final structured output
    """
    elements = []
    element_confidence = confidence_result.get('element_confidence', {})
    
    # Process walls
    for wall in walls:
        elem_id = wall['id']
        conf = element_confidence.get(elem_id, {})
        
        elements.append({
            'id': elem_id,
            'type': 'Wall',
            'length': round(wall.get('length', 0), 2),
            'thickness': round(wall.get('thickness', 0), 3),
            'height': wall.get('height', 3.0),
            'material': wall.get('material', 'Unknown'),
            'confidence': round(conf.get('overall', 0.5), 2)
        })
    
    # Process slabs
    for slab in slabs:
        elem_id = slab['id']
        conf = element_confidence.get(elem_id, {})
        
        # Get thickness from slab data or use default
        thickness = slab.get('thickness', 0.15)
        
        elements.append({
            'id': elem_id,
            'type': 'Slab',
            'area': round(slab.get('area', 0), 2),
            'thickness': round(thickness, 3),
            'material': slab.get('material', 'Concrete'),
            'confidence': round(conf.get('overall', 0.5), 2)
        })
    
    # Process columns
    for col in columns:
        elem_id = col['id']
        conf = element_confidence.get(elem_id, {})
        
        # Use actual width/depth from detection
        width = col.get('width', 0.3)
        depth = col.get('depth', 0.3)
        height = col.get('height', 3.0)
        
        elements.append({
            'id': elem_id,
            'type': 'Column',
            'width': round(width, 2),
            'depth': round(depth, 2),
            'height': round(height, 2),
            'material': col.get('material', 'RCC'),
            'confidence': round(conf.get('overall', 0.5), 2)
        })
    
    # Process doors
    for door in doors:
        elem_id = door['id']
        conf = element_confidence.get(elem_id, {})
        
        # Use actual dimensions from detection
        width = door.get('width', 0.9)  # Default 0.9m if not found
        height = door.get('height', 2.1)  # Default 2.1m if not found
        
        elements.append({
            'id': elem_id,
            'type': 'Door',
            'code': door.get('code', ''),
            'width': round(width, 2),
            'height': round(height, 2),
            'material': door.get('material', 'Wood'),
            'confidence': round(conf.get('overall', 0.5), 2)
        })
    
    # Process windows
    for window in windows:
        elem_id = window['id']
        conf = element_confidence.get(elem_id, {})
        
        # Use actual dimensions from detection
        width = window.get('width', 1.2)  # Default 1.2m if not found
        height = window.get('height', 1.5)  # Default 1.5m if not found
        
        elements.append({
            'id': elem_id,
            'type': 'Window',
            'code': window.get('code', ''),
            'width': round(width, 2),
            'height': round(height, 2),
            'material': window.get('material', 'Aluminum'),
            'confidence': round(conf.get('overall', 0.5), 2)
        })
    
    # Build relationships
    relationships = []
    if graph_result and 'graph' in graph_result:
        graph = graph_result['graph']
        for edge in graph.edges(data=True):
            relationships.append({
                'source': edge[0],
                'target': edge[1],
                'type': edge[2].get('type', 'connected')
            })
    
    # Build summary
    summary = {
        'total_walls': len(walls),
        'total_slabs': len(slabs),
        'total_columns': len(columns),
        'total_doors': len(doors),
        'total_windows': len(windows),
        'total_elements': len(elements),
        'avg_confidence': round(confidence_result.get('statistics', {}).get('average_confidence', 0), 2),
        'flagged_count': len(confidence_result.get('flagged_elements', []))
    }
    
    return {
        'elements': elements,
        'relationships': relationships,
        'summary': summary,
        'flagged_for_review': confidence_result.get('flagged_elements', [])
    }
