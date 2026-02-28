from shapely.geometry import Polygon, Point, LineString
from typing import List, Dict, Optional

def filter_to_drawing_region(layer1_output: Dict, layer2_output: Dict, 
                              buffer_ratio: float = 0.001) -> Dict:
    """Filter entities to drawing region only
    
    Args:
        layer1_output: Layer 1 output with all entities
        layer2_output: Layer 2 output with regions
        buffer_ratio: Buffer ratio for tolerance (default 0.1% of drawing size)
    
    Returns:
        Dict with filtered entities and statistics
    """
    # Get drawing region bbox
    drawing_region = layer2_output.get('drawing_region', {}).get('bbox')
    
    if not drawing_region:
        # Fallback to sheet border
        drawing_region = layer2_output.get('layer1_reference', {}).get('bounding_box')
    
    if not drawing_region:
        return {
            'entities': [],
            'error': 'No drawing region found'
        }
    
    # Create polygon from drawing region
    drawing_polygon = _create_polygon_from_bbox(drawing_region)
    
    # Add adaptive buffer (relative to drawing size)
    width = drawing_region['max_x'] - drawing_region['min_x']
    height = drawing_region['max_y'] - drawing_region['min_y']
    buffer_size = min(width, height) * buffer_ratio
    drawing_polygon = drawing_polygon.buffer(buffer_size)
    
    # Extract all entities from Layer 1
    all_entities = _extract_all_entities(layer1_output)
    
    # Filter entities by centroid containment
    drawing_entities = []
    filtered_out = []
    
    for entity in all_entities:
        centroid = _get_entity_centroid(entity)
        
        if centroid and drawing_polygon.contains(centroid):
            drawing_entities.append(entity)
        else:
            filtered_out.append(entity)
    
    return {
        'entities': drawing_entities,
        'total_entities': len(all_entities),
        'drawing_entities_count': len(drawing_entities),
        'filtered_out_count': len(filtered_out),
        'drawing_polygon': {
            'bbox': drawing_region,
            'buffer_size': buffer_size
        },
        'statistics': {
            'retention_rate': len(drawing_entities) / len(all_entities) if all_entities else 0,
            'entity_types': _count_entity_types(drawing_entities)
        }
    }

def _create_polygon_from_bbox(bbox: Dict) -> Polygon:
    """Create Shapely polygon from bounding box
    
    Args:
        bbox: Bounding box with min_x, min_y, max_x, max_y
    
    Returns:
        Shapely Polygon
    """
    return Polygon([
        (bbox['min_x'], bbox['min_y']),
        (bbox['max_x'], bbox['min_y']),
        (bbox['max_x'], bbox['max_y']),
        (bbox['min_x'], bbox['max_y'])
    ])

def _extract_all_entities(layer1_output: Dict) -> List[Dict]:
    """Extract all geometry entities from Layer 1 output
    
    Args:
        layer1_output: Layer 1 output
    
    Returns:
        List of all entities
    """
    entities = []
    geometry = layer1_output.get('geometry', {})
    
    for entity_type, entity_list in geometry.items():
        for entity in entity_list:
            entities.append({
                'type': entity_type,
                'data': entity
            })
    
    return entities

def _get_entity_centroid(entity: Dict) -> Optional[Point]:
    """Get centroid of an entity
    
    Args:
        entity: Entity dict with type and data
    
    Returns:
        Shapely Point representing centroid or None
    """
    entity_type = entity['type']
    data = entity['data']
    coords = data.get('coordinates', [])
    
    if not coords:
        return None
    
    try:
        # LINE
        if entity_type == 'LINE' and len(coords) >= 2:
            points = _extract_points(coords[:2])
            if len(points) >= 2:
                geom = LineString(points)
                return geom.centroid
        
        # POLYLINE
        elif entity_type == 'POLYLINE':
            points = _extract_points(coords)
            if len(points) >= 2:
                geom = LineString(points)
                return geom.centroid
        
        # CIRCLE
        elif entity_type == 'CIRCLE' and len(coords) >= 1:
            point = _extract_point(coords[0])
            if point:
                return Point(point)
        
        # ARC
        elif entity_type == 'ARC' and len(coords) >= 1:
            point = _extract_point(coords[0])
            if point:
                return Point(point)
        
        # TEXT (use position)
        elif entity_type == 'TEXT' and len(coords) >= 1:
            point = _extract_point(coords[0])
            if point:
                return Point(point)
        
    except Exception:
        pass
    
    return None

def _extract_point(coord) -> Optional[tuple]:
    """Extract (x, y) from coordinate
    
    Args:
        coord: Coordinate (dict or object with x, y)
    
    Returns:
        (x, y) tuple or None
    """
    try:
        if isinstance(coord, dict):
            return (coord['x'], coord['y'])
        elif hasattr(coord, 'x') and hasattr(coord, 'y'):
            return (coord.x, coord.y)
    except:
        pass
    return None

def _extract_points(coords: List) -> List[tuple]:
    """Extract list of (x, y) tuples from coordinates
    
    Args:
        coords: List of coordinates
    
    Returns:
        List of (x, y) tuples
    """
    points = []
    for coord in coords:
        point = _extract_point(coord)
        if point:
            points.append(point)
    return points

def _count_entity_types(entities: List[Dict]) -> Dict[str, int]:
    """Count entities by type
    
    Args:
        entities: List of entities
    
    Returns:
        Dict with counts by type
    """
    counts = {}
    for entity in entities:
        entity_type = entity['type']
        counts[entity_type] = counts.get(entity_type, 0) + 1
    return counts
