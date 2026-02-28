import numpy as np
import math
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree
from sklearn.cluster import DBSCAN
from typing import List, Dict, Tuple, Optional
import uuid

def detect_walls(filtered_entities: List[Dict], scale_info: Optional[Dict] = None) -> Dict:
    """Detect walls using adaptive parallel line pairing and polyline analysis
    
    Args:
        filtered_entities: Entities from Layer 3 Step 1
        scale_info: Scale information from Layer 2
    
    Returns:
        Dict with detected walls and statistics
    """
    # Extract lines and polylines
    lines = _extract_lines(filtered_entities)
    polylines = _extract_polylines(filtered_entities)
    
    if len(lines) < 2:
        return {
            'double_line_walls': [],
            'polyline_walls': [],
            'learned_thickness': None,
            'statistics': {'total_walls': 0}
        }
    
    # Step 2A.1: Extract candidate long lines (adaptive threshold)
    long_lines = _extract_long_lines(lines)
    
    # Step 2A.2: Compute orientations
    line_data = _compute_line_orientations(long_lines)
    
    # Step 2A.3: Learn wall thickness from parallel line distances
    learned_thickness = _learn_wall_thickness(line_data)
    
    # Step 2A.4: Pair lines using learned thickness
    double_line_walls = _pair_parallel_lines(line_data, learned_thickness)
    
    # Step 2B: Detect polyline walls
    polyline_walls = _detect_polyline_walls(polylines, learned_thickness)
    
    return {
        'double_line_walls': double_line_walls,
        'polyline_walls': polyline_walls,
        'learned_thickness': learned_thickness,
        'statistics': {
            'total_walls': len(double_line_walls) + len(polyline_walls),
            'double_line_count': len(double_line_walls),
            'polyline_count': len(polyline_walls),
            'candidate_lines': len(long_lines),
            'total_lines': len(lines)
        }
    }

def _extract_lines(entities: List[Dict]) -> List[Dict]:
    """Extract LINE entities"""
    lines = []
    for entity in entities:
        if entity['type'] == 'LINE':
            lines.append(entity['data'])
    return lines

def _extract_polylines(entities: List[Dict]) -> List[Dict]:
    """Extract POLYLINE entities"""
    polylines = []
    for entity in entities:
        if entity['type'] == 'POLYLINE':
            polylines.append(entity['data'])
    return polylines

def _extract_long_lines(lines: List[Dict]) -> List[Dict]:
    """Extract long lines using adaptive threshold (40% of median)
    
    Args:
        lines: List of line entities
    
    Returns:
        List of long lines
    """
    if not lines:
        return []
    
    # Compute lengths
    lengths = []
    for line in lines:
        coords = line.get('coordinates', [])
        if len(coords) >= 2:
            length = _compute_length(coords[0], coords[1])
            lengths.append(length)
    
    if not lengths:
        return []
    
    # Adaptive threshold: 40% of median length
    median_length = np.median(lengths)
    threshold = 0.4 * median_length
    
    # Filter long lines
    long_lines = []
    for i, line in enumerate(lines):
        if i < len(lengths) and lengths[i] > threshold:
            long_lines.append(line)
    
    return long_lines

def _compute_length(p1, p2) -> float:
    """Compute distance between two points"""
    x1 = p1.get('x') if isinstance(p1, dict) else p1.x
    y1 = p1.get('y') if isinstance(p1, dict) else p1.y
    x2 = p2.get('x') if isinstance(p2, dict) else p2.x
    y2 = p2.get('y') if isinstance(p2, dict) else p2.y
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def _compute_line_orientations(lines: List[Dict]) -> List[Dict]:
    """Compute orientation for each line
    
    Args:
        lines: List of line entities
    
    Returns:
        List of line data with geometry and orientation
    """
    line_data = []
    
    for line in lines:
        coords = line.get('coordinates', [])
        if len(coords) >= 2:
            p1, p2 = coords[0], coords[1]
            x1 = p1.get('x') if isinstance(p1, dict) else p1.x
            y1 = p1.get('y') if isinstance(p1, dict) else p1.y
            x2 = p2.get('x') if isinstance(p2, dict) else p2.x
            y2 = p2.get('y') if isinstance(p2, dict) else p2.y
            
            # Create Shapely LineString
            geom = LineString([(x1, y1), (x2, y2)])
            
            # Compute orientation (angle in radians)
            angle = math.atan2(y2 - y1, x2 - x1)
            
            line_data.append({
                'geometry': geom,
                'coords': [(x1, y1), (x2, y2)],
                'angle': angle,
                'length': geom.length,
                'layer': line.get('layer', '0'),
                'original': line
            })
    
    return line_data

def _learn_wall_thickness(line_data: List[Dict]) -> Optional[float]:
    """Learn wall thickness by clustering distances between parallel lines
    
    Args:
        line_data: List of line data with geometry
    
    Returns:
        Learned wall thickness or None
    """
    if len(line_data) < 2:
        return None
    
    # Build spatial index
    geometries = [ld['geometry'] for ld in line_data]
    tree = STRtree(geometries)
    
    # Collect distances between nearby parallel lines
    distances = []
    angle_tolerance = math.radians(5)  # 5 degrees
    
    for i, line1 in enumerate(line_data):
        # Query nearby lines
        nearby_indices = tree.query(line1['geometry'].buffer(2.0))
        
        for j in nearby_indices:
            if i >= j:
                continue
            
            line2 = line_data[j]
            
            # Check if nearly parallel
            angle_diff = abs(line1['angle'] - line2['angle'])
            if angle_diff > angle_tolerance and angle_diff < (math.pi - angle_tolerance):
                continue
            
            # Compute perpendicular distance
            dist = line1['geometry'].distance(line2['geometry'])
            
            # Only consider reasonable wall thickness range (0.05 to 1.0 units)
            if 0.05 < dist < 1.0:
                distances.append(dist)
    
    if len(distances) < 3:
        return 0.2  # Default fallback
    
    # Cluster distances using DBSCAN
    distances_array = np.array(distances).reshape(-1, 1)
    clustering = DBSCAN(eps=0.05, min_samples=2).fit(distances_array)
    
    # Find largest cluster
    labels = clustering.labels_
    if len(set(labels)) == 1 and labels[0] == -1:
        # No clusters found, use median
        return float(np.median(distances))
    
    # Get most common cluster
    unique_labels = [l for l in set(labels) if l != -1]
    if not unique_labels:
        return float(np.median(distances))
    
    cluster_sizes = [(l, list(labels).count(l)) for l in unique_labels]
    largest_cluster = max(cluster_sizes, key=lambda x: x[1])[0]
    
    # Return mean of largest cluster
    cluster_distances = [distances[i] for i, l in enumerate(labels) if l == largest_cluster]
    return float(np.mean(cluster_distances))

def _pair_parallel_lines(line_data: List[Dict], learned_thickness: Optional[float]) -> List[Dict]:
    """Pair parallel lines to form walls
    
    Args:
        line_data: List of line data
        learned_thickness: Learned wall thickness
    
    Returns:
        List of detected double-line walls
    """
    if not learned_thickness or len(line_data) < 2:
        return []
    
    # Build spatial index
    geometries = [ld['geometry'] for ld in line_data]
    tree = STRtree(geometries)
    
    walls = []
    paired = set()
    
    angle_tolerance = math.radians(5)
    thickness_tolerance = learned_thickness * 0.3  # ±30%
    
    for i, line1 in enumerate(line_data):
        if i in paired:
            continue
        
        # Query nearby lines
        search_buffer = learned_thickness * 2
        nearby_indices = tree.query(line1['geometry'].buffer(search_buffer))
        
        for j in nearby_indices:
            if i >= j or j in paired:
                continue
            
            line2 = line_data[j]
            
            # Check parallel
            angle_diff = abs(line1['angle'] - line2['angle'])
            if angle_diff > angle_tolerance and angle_diff < (math.pi - angle_tolerance):
                continue
            
            # Check distance
            dist = line1['geometry'].distance(line2['geometry'])
            if abs(dist - learned_thickness) > thickness_tolerance:
                continue
            
            # Check overlap projection
            overlap = _compute_overlap_ratio(line1, line2)
            if overlap < 0.6:
                continue
            
            # Create wall
            wall = _create_wall_from_pair(line1, line2, dist)
            walls.append(wall)
            
            paired.add(i)
            paired.add(j)
            break
    
    return walls

def _compute_overlap_ratio(line1: Dict, line2: Dict) -> float:
    """Compute overlap ratio of two parallel lines"""
    # Project line2 endpoints onto line1
    l1_start, l1_end = line1['coords']
    l2_start, l2_end = line2['coords']
    
    # Simple overlap check using bounding boxes
    l1_min_x = min(l1_start[0], l1_end[0])
    l1_max_x = max(l1_start[0], l1_end[0])
    l2_min_x = min(l2_start[0], l2_end[0])
    l2_max_x = max(l2_start[0], l2_end[0])
    
    overlap_x = max(0, min(l1_max_x, l2_max_x) - max(l1_min_x, l2_min_x))
    
    l1_min_y = min(l1_start[1], l1_end[1])
    l1_max_y = max(l1_start[1], l1_end[1])
    l2_min_y = min(l2_start[1], l2_end[1])
    l2_max_y = max(l2_start[1], l2_end[1])
    
    overlap_y = max(0, min(l1_max_y, l2_max_y) - max(l1_min_y, l2_min_y))
    
    overlap_length = max(overlap_x, overlap_y)
    avg_length = (line1['length'] + line2['length']) / 2
    
    return overlap_length / avg_length if avg_length > 0 else 0

def _create_wall_from_pair(line1: Dict, line2: Dict, thickness: float) -> Dict:
    """Create wall object from paired lines"""
    # Compute centerline (midpoint between lines)
    l1_start, l1_end = line1['coords']
    l2_start, l2_end = line2['coords']
    
    center_start = ((l1_start[0] + l2_start[0]) / 2, (l1_start[1] + l2_start[1]) / 2)
    center_end = ((l1_end[0] + l2_end[0]) / 2, (l1_end[1] + l2_end[1]) / 2)
    
    centerline = LineString([center_start, center_end])
    
    return {
        'id': str(uuid.uuid4()),
        'type': 'double_line_wall',
        'centerline': list(centerline.coords),
        'thickness': thickness,
        'length': centerline.length,
        'height': 3.0,  # Standard story height
        'orientation': (line1['angle'] + line2['angle']) / 2,
        'layer': line1['layer']
    }

def _detect_polyline_walls(polylines: List[Dict], learned_thickness: Optional[float]) -> List[Dict]:
    """Detect walls from polylines with width property
    
    Args:
        polylines: List of polyline entities
        learned_thickness: Learned thickness for validation
    
    Returns:
        List of polyline walls
    """
    walls = []
    
    for polyline in polylines:
        # Check for width property
        width = polyline.get('metadata', {}).get('width', 0)
        
        if width > 0:
            coords = polyline.get('coordinates', [])
            if len(coords) >= 2:
                points = [(p.get('x') if isinstance(p, dict) else p.x,
                          p.get('y') if isinstance(p, dict) else p.y) for p in coords]
                
                centerline = LineString(points)
                
                walls.append({
                    'id': str(uuid.uuid4()),
                    'type': 'polyline_wall',
                    'centerline': list(centerline.coords),
                    'thickness': width,
                    'length': centerline.length,
                    'height': 3.0,  # Standard story height
                    'layer': polyline.get('layer', '0')
                })
    
    return walls
