import numpy as np
import math
from typing import List, Tuple
from app.ai.geometry_model import Point, GeometryEntity

def curve_to_polyline(control_points: List[Point], num_segments: int = 20) -> List[Point]:
    """Approximate curve to polyline using linear interpolation"""
    if len(control_points) < 2:
        return control_points
    
    polyline = []
    for i in range(num_segments + 1):
        t = i / num_segments
        point = bezier_point(control_points, t)
        polyline.append(point)
    
    return polyline

def bezier_point(control_points: List[Point], t: float) -> Point:
    """Calculate point on Bezier curve at parameter t"""
    n = len(control_points) - 1
    x = y = 0.0
    
    for i, p in enumerate(control_points):
        coeff = binomial_coefficient(n, i) * (1 - t) ** (n - i) * t ** i
        x += coeff * p.x
        y += coeff * p.y
    
    return Point(x, y)

def binomial_coefficient(n: int, k: int) -> int:
    """Calculate binomial coefficient"""
    if k > n:
        return 0
    if k == 0 or k == n:
        return 1
    
    result = 1
    for i in range(min(k, n - k)):
        result = result * (n - i) // (i + 1)
    return result

def apply_transform_matrix(point: Point, matrix: np.ndarray) -> Point:
    """Apply transformation matrix to point"""
    vec = np.array([point.x, point.y, point.z, 1.0])
    transformed = matrix @ vec
    return Point(transformed[0], transformed[1], transformed[2])

def create_transform_matrix(tx: float = 0, ty: float = 0, tz: float = 0,
                           sx: float = 1, sy: float = 1, sz: float = 1,
                           rotation: float = 0) -> np.ndarray:
    """Create 4x4 transformation matrix"""
    # Translation
    T = np.array([
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1]
    ])
    
    # Scale
    S = np.array([
        [sx, 0, 0, 0],
        [0, sy, 0, 0],
        [0, 0, sz, 0],
        [0, 0, 0, 1]
    ])
    
    # Rotation (around Z axis)
    rad = math.radians(rotation)
    R = np.array([
        [math.cos(rad), -math.sin(rad), 0, 0],
        [math.sin(rad), math.cos(rad), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])
    
    return T @ R @ S

def calculate_distance(p1: Point, p2: Point) -> float:
    """Calculate Euclidean distance between two points"""
    return math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2 + (p2.z - p1.z)**2)

def calculate_area_polygon(points: List[Point]) -> float:
    """Calculate area of polygon using shoelace formula"""
    if len(points) < 3:
        return 0.0
    
    area = 0.0
    for i in range(len(points)):
        j = (i + 1) % len(points)
        area += points[i].x * points[j].y
        area -= points[j].x * points[i].y
    
    return abs(area) / 2.0

def normalize_units(value: float, from_unit: str, to_unit: str = "meters") -> float:
    """Normalize units to target unit"""
    to_meters = {
        'inches': 0.0254,
        'feet': 0.3048,
        'millimeters': 0.001,
        'centimeters': 0.01,
        'meters': 1.0,
        'unitless': 1.0
    }
    
    # Convert to meters first
    in_meters = value * to_meters.get(from_unit, 1.0)
    
    # Convert to target unit
    return in_meters / to_meters.get(to_unit, 1.0)

def flip_y_coordinate(point: Point, page_height: float) -> Point:
    """Flip Y coordinate for SVG to CAD conversion"""
    return Point(point.x, page_height - point.y, point.z)

def parse_svg_transform(transform_str: str) -> np.ndarray:
    """Parse SVG transform attribute to matrix"""
    if not transform_str or 'matrix' not in transform_str:
        return np.eye(4)
    
    # Extract matrix values
    start = transform_str.find('(') + 1
    end = transform_str.find(')')
    values = [float(v) for v in transform_str[start:end].split()]
    
    if len(values) == 6:
        # SVG matrix(a, b, c, d, e, f)
        a, b, c, d, e, f = values
        return np.array([
            [a, c, 0, e],
            [b, d, 0, f],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
    
    return np.eye(4)

def deduplicate_geometry(entities: List[GeometryEntity], tolerance: float = 0.001) -> List[GeometryEntity]:
    """Remove duplicate geometry entities"""
    unique = []
    
    for entity in entities:
        is_duplicate = False
        for existing in unique:
            if entities_equal(entity, existing, tolerance):
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique.append(entity)
    
    return unique

def entities_equal(e1: GeometryEntity, e2: GeometryEntity, tolerance: float) -> bool:
    """Check if two entities are equal within tolerance"""
    if e1.entity_type != e2.entity_type:
        return False
    
    if len(e1.coordinates) != len(e2.coordinates):
        return False
    
    for p1, p2 in zip(e1.coordinates, e2.coordinates):
        if calculate_distance(p1, p2) > tolerance:
            return False
    
    return True

def compute_global_bounding_box(entities: List[GeometryEntity]) -> dict:
    """Compute global bounding box from all entities"""
    if not entities:
        return {'min_x': 0, 'min_y': 0, 'max_x': 0, 'max_y': 0}
    
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')
    
    for entity in entities:
        if entity.bounding_box:
            min_x = min(min_x, entity.bounding_box.min_x)
            min_y = min(min_y, entity.bounding_box.min_y)
            max_x = max(max_x, entity.bounding_box.max_x)
            max_y = max(max_y, entity.bounding_box.max_y)
    
    return {'min_x': min_x, 'min_y': min_y, 'max_x': max_x, 'max_y': max_y}

def filter_junk_entities(entities: List[GeometryEntity], 
                        min_line_length: float = 0.001,
                        filter_borders: bool = False,
                        global_bbox: dict = None) -> List[GeometryEntity]:
    """Filter out junk entities (STEP 7 - for Layer 2 use)
    
    For now, this function exists but filtering is disabled.
    Layer 2 will enable filtering by setting parameters.
    
    Args:
        entities: List of entities to filter
        min_line_length: Minimum line length threshold (meters)
        filter_borders: Whether to filter border rectangles
        global_bbox: Global bounding box for border detection
    
    Returns:
        Filtered list of entities (currently returns all)
    """
    # STEP 7: For now, just store everything. Filtering comes in Layer 2.
    return entities
