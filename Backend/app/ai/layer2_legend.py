import numpy as np
from typing import List, Dict, Optional, Tuple
import math

# Legend keywords
LEGEND_KEYWORDS = ['legend', 'symbol', 'key', 'codes', 'notation']

def detect_legend_region(text_entities: List[Dict], labels: np.ndarray, 
                         layer1_output: Dict) -> Optional[Dict]:
    """Detect legend region from text clusters and nearby shapes
    
    Args:
        text_entities: List of text dicts with 'text' and 'position'
        labels: Cluster labels from DBSCAN
        layer1_output: Layer 1 output with geometry
    
    Returns:
        Dict with legend info or None
    """
    if len(text_entities) == 0:
        return None
    
    # Get unique cluster IDs (exclude noise -1)
    unique_labels = set(labels)
    cluster_ids = [int(l) for l in unique_labels if l != -1]
    
    if len(cluster_ids) == 0:
        return None
    
    # Score each cluster for legend likelihood
    legend_candidates = []
    for cluster_id in cluster_ids:
        cluster_indices = np.where(labels == cluster_id)[0]
        cluster_texts = [text_entities[i] for i in cluster_indices]
        
        score = _score_cluster_for_legend(cluster_texts)
        if score > 0:
            legend_candidates.append({
                'cluster_id': int(cluster_id),
                'score': score,
                'texts': cluster_texts,
                'indices': [int(i) for i in cluster_indices]
            })
    
    if not legend_candidates:
        return {
            'status': 'not_found',
            'legend_dictionary': {},
            'confidence': 'low'
        }
    
    # Sort by score and pick best
    legend_candidates.sort(key=lambda x: x['score'], reverse=True)
    best_candidate = legend_candidates[0]
    
    # Compute legend region bbox
    positions = [t['position'] for t in best_candidate['texts']]
    bbox = _compute_bbox(positions)
    
    # Expand bbox by margin (15% of dimensions)
    expanded_bbox = _expand_bbox(bbox, margin_percent=0.15)
    
    # Extract shapes inside legend region
    shapes_in_region = _extract_shapes_in_region(layer1_output, expanded_bbox)
    
    # Build legend dictionary (shape signature -> text label)
    legend_dict = _build_legend_dictionary(shapes_in_region, best_candidate['texts'])
    
    return {
        'status': 'found',
        'cluster_id': best_candidate['cluster_id'],
        'score': best_candidate['score'],
        'bounding_box': bbox,
        'expanded_bbox': expanded_bbox,
        'legend_dictionary': legend_dict,
        'shape_count': len(shapes_in_region),
        'confidence': 'high' if len(legend_dict) > 0 else 'medium'
    }

def _score_cluster_for_legend(texts: List[Dict]) -> int:
    """Score a cluster based on legend keywords
    
    Args:
        texts: List of text dicts
    
    Returns:
        Score (higher = more likely legend)
    """
    score = 0
    
    for text_dict in texts:
        text = text_dict.get('text', '').lower()
        
        # Check for legend keywords
        for keyword in LEGEND_KEYWORDS:
            if keyword in text:
                score += 2
    
    return score

def _compute_bbox(positions: List[List[float]]) -> Dict:
    """Compute bounding box from positions"""
    if not positions:
        return {'min_x': 0, 'min_y': 0, 'max_x': 0, 'max_y': 0}
    
    xs = [p[0] for p in positions]
    ys = [p[1] for p in positions]
    
    return {
        'min_x': min(xs),
        'min_y': min(ys),
        'max_x': max(xs),
        'max_y': max(ys)
    }

def _expand_bbox(bbox: Dict, margin_percent: float = 0.15) -> Dict:
    """Expand bounding box by percentage margin
    
    Args:
        bbox: Original bounding box
        margin_percent: Percentage to expand (e.g., 0.15 = 15%)
    
    Returns:
        Expanded bounding box
    """
    width = bbox['max_x'] - bbox['min_x']
    height = bbox['max_y'] - bbox['min_y']
    
    margin_x = width * margin_percent
    margin_y = height * margin_percent
    
    return {
        'min_x': bbox['min_x'] - margin_x,
        'min_y': bbox['min_y'] - margin_y,
        'max_x': bbox['max_x'] + margin_x,
        'max_y': bbox['max_y'] + margin_y
    }

def _extract_shapes_in_region(layer1_output: Dict, bbox: Dict) -> List[Dict]:
    """Extract geometry shapes inside bounding box
    
    Args:
        layer1_output: Layer 1 output with geometry
        bbox: Bounding box to filter shapes
    
    Returns:
        List of shapes inside region
    """
    shapes = []
    geometry = layer1_output.get('geometry', {})
    
    # Extract lines
    if 'LINE' in geometry:
        for entity in geometry['LINE']:
            if _is_entity_in_bbox(entity, bbox):
                shapes.append({
                    'type': 'LINE',
                    'entity': entity,
                    'signature': _compute_shape_signature(entity, 'LINE')
                })
    
    # Extract circles
    if 'CIRCLE' in geometry:
        for entity in geometry['CIRCLE']:
            if _is_entity_in_bbox(entity, bbox):
                shapes.append({
                    'type': 'CIRCLE',
                    'entity': entity,
                    'signature': _compute_shape_signature(entity, 'CIRCLE')
                })
    
    # Extract polylines
    if 'POLYLINE' in geometry:
        for entity in geometry['POLYLINE']:
            if _is_entity_in_bbox(entity, bbox):
                shapes.append({
                    'type': 'POLYLINE',
                    'entity': entity,
                    'signature': _compute_shape_signature(entity, 'POLYLINE')
                })
    
    return shapes

def _is_entity_in_bbox(entity: Dict, bbox: Dict) -> bool:
    """Check if entity is inside bounding box
    
    Args:
        entity: Geometry entity
        bbox: Bounding box
    
    Returns:
        True if entity is inside bbox
    """
    coords = entity.get('coordinates', [])
    if not coords:
        return False
    
    for coord in coords:
        x = coord.get('x') if isinstance(coord, dict) else (coord.x if hasattr(coord, 'x') else 0)
        y = coord.get('y') if isinstance(coord, dict) else (coord.y if hasattr(coord, 'y') else 0)
        
        if bbox['min_x'] <= x <= bbox['max_x'] and bbox['min_y'] <= y <= bbox['max_y']:
            return True
    
    return False

def _compute_shape_signature(entity: Dict, entity_type: str) -> str:
    """Compute unique signature for a shape
    
    Args:
        entity: Geometry entity
        entity_type: Type of entity (LINE, CIRCLE, etc.)
    
    Returns:
        Signature string
    """
    coords = entity.get('coordinates', [])
    
    if entity_type == 'LINE' and len(coords) >= 2:
        return f"line-2pts"
    elif entity_type == 'CIRCLE':
        return f"circle"
    elif entity_type == 'POLYLINE':
        return f"poly-{len(coords)}pts"
    
    return f"{entity_type.lower()}"

def _build_legend_dictionary(shapes: List[Dict], texts: List[Dict]) -> Dict[str, str]:
    """Build legend dictionary by pairing shapes with nearest text
    
    Args:
        shapes: List of shape dicts
        texts: List of text dicts
    
    Returns:
        Dictionary mapping shape signature to text label
    """
    legend_dict = {}
    
    for shape in shapes:
        # Find nearest text to this shape
        shape_center = _get_shape_center(shape['entity'])
        if not shape_center:
            continue
        
        nearest_text = None
        min_distance = float('inf')
        
        for text_dict in texts:
            text_pos = text_dict['position']
            distance = math.sqrt(
                (shape_center[0] - text_pos[0])**2 + 
                (shape_center[1] - text_pos[1])**2
            )
            
            if distance < min_distance:
                min_distance = distance
                nearest_text = text_dict['text']
        
        if nearest_text:
            legend_dict[shape['signature']] = nearest_text
    
    return legend_dict

def _get_shape_center(entity: Dict) -> Optional[List[float]]:
    """Get center point of a shape
    
    Args:
        entity: Geometry entity
    
    Returns:
        [x, y] center coordinates or None
    """
    coords = entity.get('coordinates', [])
    if not coords:
        return None
    
    xs = []
    ys = []
    
    for coord in coords:
        x = coord.get('x') if isinstance(coord, dict) else (coord.x if hasattr(coord, 'x') else 0)
        y = coord.get('y') if isinstance(coord, dict) else (coord.y if hasattr(coord, 'y') else 0)
        xs.append(x)
        ys.append(y)
    
    if xs and ys:
        return [sum(xs) / len(xs), sum(ys) / len(ys)]
    
    return None
