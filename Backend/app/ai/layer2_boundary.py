from typing import Dict, List, Tuple, Optional
import math
from app.ai.geometry_model import GeometryEntity, Point

def identify_sheet_border(all_lines: List[Dict], extents: Dict) -> Optional[Dict]:
    """Identify sheet border from outer boundary lines
    
    Args:
        all_lines: List of all lines
        extents: Global bounding box
    
    Returns:
        Sheet border dict or None
    """
    max_dim = max(extents['max_x'] - extents['min_x'], extents['max_y'] - extents['min_y'])
    threshold = 0.7 * max_dim
    
    # Filter long lines
    long_lines = [l for l in all_lines if l['length'] > threshold]
    if len(long_lines) < 4:
        return None
    
    # Filter by angle
    horiz = _filter_lines_by_angle(long_lines, 0, 3)
    vert = _filter_lines_by_angle(long_lines, 90, 3)
    
    if len(horiz) < 2 or len(vert) < 2:
        return None
    
    # Find extreme lines
    horiz.sort(key=lambda l: min(l['start'][1], l['end'][1]))
    vert.sort(key=lambda l: min(l['start'][0], l['end'][0]))
    
    return {
        'min_x': min(vert[0]['start'][0], vert[0]['end'][0]),
        'max_x': max(vert[-1]['start'][0], vert[-1]['end'][0]),
        'min_y': min(horiz[0]['start'][1], horiz[0]['end'][1]),
        'max_y': max(horiz[-1]['start'][1], horiz[-1]['end'][1])
    }

def _filter_lines_by_angle(lines: List[Dict], target_angle: float, tolerance: float) -> List[Dict]:
    """Filter lines by angle"""
    result = []
    for line in lines:
        dx = line['end'][0] - line['start'][0]
        dy = line['end'][1] - line['start'][1]
        angle = math.degrees(math.atan2(dy, dx)) % 180
        
        if abs(angle - target_angle) <= tolerance or abs(angle - target_angle - 180) <= tolerance:
            result.append(line)
    return result

def load_geometry_and_compute_extents(layer1_output: Dict) -> Tuple[List[Dict], Dict]:
    """Load all geometry from Layer 1 and compute global extents
    
    Args:
        layer1_output: Output from Layer 1 pipeline
    
    Returns:
        Tuple of (all_lines, extents)
        - all_lines: List of {type, start, end, length}
        - extents: {min_x, min_y, max_x, max_y}
    """
    all_lines = []
    geometry = layer1_output.get('geometry', {})
    
    # Process LINE entities
    if 'LINE' in geometry:
        for entity in geometry['LINE']:
            coords = entity.get('coordinates', [])
            if len(coords) >= 2:
                start, end = coords[0], coords[1]
                start_x = start.x if hasattr(start, 'x') else start['x']
                start_y = start.y if hasattr(start, 'y') else start['y']
                end_x = end.x if hasattr(end, 'x') else end['x']
                end_y = end.y if hasattr(end, 'y') else end['y']
                all_lines.append({
                    'type': 'LINE',
                    'start': [start_x, start_y],
                    'end': [end_x, end_y],
                    'length': ((end_x - start_x)**2 + (end_y - start_y)**2)**0.5
                })
    
    # Process POLYLINE entities
    if 'POLYLINE' in geometry:
        for entity in geometry['POLYLINE']:
            points = entity.get('coordinates', [])
            for i in range(len(points) - 1):
                start, end = points[i], points[i + 1]
                start_x = start.x if hasattr(start, 'x') else start['x']
                start_y = start.y if hasattr(start, 'y') else start['y']
                end_x = end.x if hasattr(end, 'x') else end['x']
                end_y = end.y if hasattr(end, 'y') else end['y']
                all_lines.append({
                    'type': 'LINE',
                    'start': [start_x, start_y],
                    'end': [end_x, end_y],
                    'length': ((end_x - start_x)**2 + (end_y - start_y)**2)**0.5
                })
    
    # Use existing bounding_box or compute
    extents = layer1_output.get('bounding_box') or _compute_extents(all_lines)
    
    # Identify sheet border
    sheet_border = identify_sheet_border(all_lines, extents)
    if sheet_border:
        layer1_output['sheet_border'] = sheet_border
    
    return all_lines, extents

def _calculate_length(p1: Dict, p2: Dict) -> float:
    """Calculate Euclidean distance between two points"""
    dx = p2['x'] - p1['x']
    dy = p2['y'] - p1['y']
    return (dx**2 + dy**2)**0.5

def _compute_extents(lines: List[Dict]) -> Dict:
    """Compute min/max extents from all lines"""
    if not lines:
        return {'min_x': 0, 'min_y': 0, 'max_x': 0, 'max_y': 0}
    
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')
    
    for line in lines:
        start = line['start']
        end = line['end']
        
        min_x = min(min_x, start[0], end[0])
        min_y = min(min_y, start[1], end[1])
        max_x = max(max_x, start[0], end[0])
        max_y = max(max_y, start[1], end[1])
    
    return {
        'min_x': min_x,
        'min_y': min_y,
        'max_x': max_x,
        'max_y': max_y
    }
