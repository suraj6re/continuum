"""Confidence Integration - Combines Multiple Confidence Scores"""
from typing import List, Dict

def integrate_confidence(nodes: List[Dict]) -> List[Dict]:
    """Integrate multiple confidence sources into final confidence score
    
    Args:
        nodes: List of canonical nodes
    
    Returns:
        Nodes with integrated confidence scores
    """
    for node in nodes:
        # Get individual confidence components
        geometry_conf = node.get('confidence', 0.5)  # From Layer 3 detection
        
        # Material confidence
        material = node.get('material', {})
        material_conf = 1.0 if material.get('grade') != 'Standard' else 0.8
        if material.get('category') == 'Unknown':
            material_conf = 0.5
        
        # Dimension confidence
        dimensions = node.get('dimensions', {})
        dimension_conf = 1.0  # Assume explicit dimensions are accurate
        
        # Check if dimensions are defaults (lower confidence)
        if node['type'] == 'Wall':
            if dimensions.get('height', 0) == 3.0:  # Default height
                dimension_conf = 0.7
        elif node['type'] == 'Column':
            if dimensions.get('width', 0) == 0.3 and dimensions.get('depth', 0) == 0.3:
                dimension_conf = 0.7
        
        # Weighted combination
        final_confidence = (
            0.5 * geometry_conf +
            0.3 * material_conf +
            0.2 * dimension_conf
        )
        
        # Store component confidences for traceability
        node['confidence'] = round(final_confidence, 2)
        node['confidence_breakdown'] = {
            'geometry': round(geometry_conf, 2),
            'material': round(material_conf, 2),
            'dimension': round(dimension_conf, 2)
        }
    
    return nodes
