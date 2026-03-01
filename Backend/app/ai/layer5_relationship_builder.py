"""Relationship Builder - Detects Spatial Relationships"""
from typing import List, Dict
import math

def point_on_line(point: List[float], line_start: List[float], line_end: List[float], tolerance: float = 0.2) -> bool:
    """Check if point lies on line segment within tolerance"""
    x, y = point
    x1, y1 = line_start
    x2, y2 = line_end
    
    # Calculate distance from point to line
    line_len = math.sqrt((x2-x1)**2 + (y2-y1)**2)
    if line_len == 0:
        return False
    
    dist = abs((y2-y1)*x - (x2-x1)*y + x2*y1 - y2*x1) / line_len
    
    # Check if point is within line segment bounds
    min_x, max_x = min(x1, x2), max(x1, x2)
    min_y, max_y = min(y1, y2), max(y1, y2)
    
    in_bounds = (min_x - tolerance <= x <= max_x + tolerance and 
                 min_y - tolerance <= y <= max_y + tolerance)
    
    return dist < tolerance and in_bounds

def point_in_polygon(point: List[float], polygon: List[List[float]]) -> bool:
    """Check if point is inside polygon using ray casting"""
    if not polygon or len(polygon) < 3:
        return False
    
    x, y = point
    n = len(polygon)
    inside = False
    
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside

def distance(p1: List[float], p2: List[float]) -> float:
    """Calculate Euclidean distance"""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def build_relationships(nodes: List[Dict], tolerance: float = 0.3) -> List[Dict]:
    """Build spatial relationships between elements
    
    Args:
        nodes: List of canonical nodes
        tolerance: Distance tolerance for relationship detection
    
    Returns:
        List of relationship edges
    """
    relationships = []
    
    # Create lookup by type
    walls = [n for n in nodes if n['type'] == 'Wall']
    slabs = [n for n in nodes if n['type'] == 'Slab']
    columns = [n for n in nodes if n['type'] == 'Column']
    doors = [n for n in nodes if n['type'] == 'Door']
    windows = [n for n in nodes if n['type'] == 'Window']
    
    # Door/Window → Wall (attached_to)
    for opening in doors + windows:
        opening_geom = opening.get('geometry', {}).get('centerline', [])
        if not opening_geom:
            continue
        
        opening_midpoint = opening_geom[0] if opening_geom else [0, 0]
        
        for wall in walls:
            wall_centerline = wall.get('geometry', {}).get('centerline', [])
            if len(wall_centerline) >= 2:
                if point_on_line(opening_midpoint, wall_centerline[0], wall_centerline[-1], tolerance):
                    relationships.append({
                        'from': opening['id'],
                        'to': wall['id'],
                        'relation': 'attached_to'
                    })
                    break
    
    # Column → Slab (inside)
    for column in columns:
        col_geom = column.get('geometry', {}).get('centerline', [])
        if not col_geom:
            continue
        
        col_centroid = col_geom[0] if col_geom else [0, 0]
        
        for slab in slabs:
            slab_polygon = slab.get('geometry', {}).get('polygon', [])
            if point_in_polygon(col_centroid, slab_polygon):
                relationships.append({
                    'from': column['id'],
                    'to': slab['id'],
                    'relation': 'inside'
                })
                break
    
    # Wall → Wall (intersects)
    for i, wall1 in enumerate(walls):
        wall1_line = wall1.get('geometry', {}).get('centerline', [])
        if len(wall1_line) < 2:
            continue
        
        for wall2 in walls[i+1:]:
            wall2_line = wall2.get('geometry', {}).get('centerline', [])
            if len(wall2_line) < 2:
                continue
            
            # Check if endpoints are close
            for p1 in [wall1_line[0], wall1_line[-1]]:
                for p2 in [wall2_line[0], wall2_line[-1]]:
                    if distance(p1, p2) < tolerance:
                        relationships.append({
                            'from': wall1['id'],
                            'to': wall2['id'],
                            'relation': 'intersects'
                        })
                        break
    
    # Slab → Wall (supported_by)
    for slab in slabs:
        slab_polygon = slab.get('geometry', {}).get('polygon', [])
        if not slab_polygon:
            continue
        
        for wall in walls:
            wall_line = wall.get('geometry', {}).get('centerline', [])
            if len(wall_line) >= 2:
                # Check if wall endpoints are near slab edges
                for point in wall_line:
                    if point_in_polygon(point, slab_polygon):
                        relationships.append({
                            'from': slab['id'],
                            'to': wall['id'],
                            'relation': 'supported_by'
                        })
                        break
    
    return relationships
