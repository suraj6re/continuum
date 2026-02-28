import numpy as np
import math
from shapely.geometry import Polygon, Point, LineString
from shapely.strtree import STRtree
from typing import List, Dict, Optional
import uuid

def detect_slabs(filtered_entities: List[Dict], walls: List[Dict]) -> Dict:
    """Detect slabs using adaptive area thresholds and containment analysis
    
    Args:
        filtered_entities: Entities from Layer 3 Step 1
        walls: Detected walls from Layer 3 Step 2
    
    Returns:
        Dict with detected slabs and statistics
    """
    # Step 3.1: Extract closed polygon candidates
    candidate_polygons = _extract_closed_polygons(filtered_entities)
    
    if len(candidate_polygons) < 1:
        return {
            'slabs': [],
            'statistics': {
                'total_slabs': 0,
                'candidates': 0
            }
        }
    
    # Step 3.2: Compute area distribution and filter by percentile
    large_polygons = _filter_by_area_percentile(candidate_polygons, percentile=90)
    
    if not large_polygons:
        # Fallback: pick largest polygon
        largest = max(candidate_polygons, key=lambda x: x['area'])
        large_polygons = [largest]
    
    # Step 3.3: Analyze containment relationships
    polygons_with_containment = _analyze_containment(large_polygons, candidate_polygons)
    
    # Step 3.4: Cross-check with wall network
    if walls:
        polygons_with_walls = _analyze_wall_containment(polygons_with_containment, walls)
    else:
        polygons_with_walls = polygons_with_containment
    
    # Step 3.5: Score and rank candidates
    scored_slabs = _score_slab_candidates(polygons_with_walls)
    
    # Step 3.6: Filter by shape regularity
    valid_slabs = _filter_by_shape_regularity(scored_slabs)
    
    # Create final slab objects
    slabs = _create_slab_objects(valid_slabs)
    
    return {
        'slabs': slabs,
        'statistics': {
            'total_slabs': len(slabs),
            'candidates': len(candidate_polygons),
            'large_polygons': len(large_polygons),
            'after_containment': len(polygons_with_containment),
            'after_scoring': len(scored_slabs)
        }
    }

def _extract_closed_polygons(entities: List[Dict]) -> List[Dict]:
    """Extract closed polylines and convert to polygons
    
    Args:
        entities: List of entities
    
    Returns:
        List of polygon candidates with metadata
    """
    candidates = []
    
    for entity in entities:
        if entity['type'] != 'POLYLINE':
            continue
        
        data = entity['data']
        coords = data.get('coordinates', [])
        is_closed = data.get('closed', False)
        
        if not is_closed or len(coords) < 3:
            continue
        
        # Extract points
        points = []
        for coord in coords:
            x = coord.get('x') if isinstance(coord, dict) else coord.x
            y = coord.get('y') if isinstance(coord, dict) else coord.y
            points.append((x, y))
        
        # Create polygon
        try:
            polygon = Polygon(points)
            
            if not polygon.is_valid or polygon.area < 0.1:
                continue
            
            candidates.append({
                'geometry': polygon,
                'area': polygon.area,
                'perimeter': polygon.length,
                'layer': data.get('layer', '0'),
                'original': data
            })
        except:
            continue
    
    return candidates

def _filter_by_area_percentile(candidates: List[Dict], percentile: float = 90) -> List[Dict]:
    """Filter polygons by area percentile
    
    Args:
        candidates: List of polygon candidates
        percentile: Percentile threshold (default 90)
    
    Returns:
        List of large polygons
    """
    if not candidates:
        return []
    
    areas = [c['area'] for c in candidates]
    threshold = np.percentile(areas, percentile)
    
    return [c for c in candidates if c['area'] >= threshold]

def _analyze_containment(large_polygons: List[Dict], all_polygons: List[Dict]) -> List[Dict]:
    """Analyze how many polygons each large polygon contains
    
    Args:
        large_polygons: Large polygon candidates
        all_polygons: All polygon candidates
    
    Returns:
        Large polygons with containment counts
    """
    # Build spatial index for efficiency
    all_geoms = [p['geometry'] for p in all_polygons]
    tree = STRtree(all_geoms)
    
    for large_poly in large_polygons:
        large_geom = large_poly['geometry']
        
        # Query potentially contained polygons
        candidate_indices = tree.query(large_geom)
        
        contains_count = 0
        for idx in candidate_indices:
            other_geom = all_polygons[idx]['geometry']
            
            # Skip self
            if large_geom.equals(other_geom):
                continue
            
            # Check containment
            if large_geom.contains(other_geom):
                contains_count += 1
        
        large_poly['contains_count'] = contains_count
    
    return large_polygons

def _analyze_wall_containment(polygons: List[Dict], walls: List[Dict]) -> List[Dict]:
    """Analyze how many walls each polygon contains
    
    Args:
        polygons: Polygon candidates
        walls: Detected walls
    
    Returns:
        Polygons with wall containment ratios
    """
    if not walls:
        for poly in polygons:
            poly['wall_containment_ratio'] = 0
        return polygons
    
    # Extract wall centerlines
    wall_centers = []
    for wall in walls:
        centerline = wall.get('centerline', [])
        if len(centerline) >= 2:
            line = LineString(centerline)
            wall_centers.append(line.centroid)
    
    total_walls = len(wall_centers)
    
    for poly in polygons:
        geom = poly['geometry']
        
        inside_count = sum(1 for wc in wall_centers if geom.contains(wc))
        
        poly['wall_containment_ratio'] = inside_count / total_walls if total_walls > 0 else 0
        poly['walls_inside'] = inside_count
    
    return polygons

def _score_slab_candidates(polygons: List[Dict]) -> List[Dict]:
    """Score slab candidates using multiple criteria
    
    Args:
        polygons: Polygon candidates with metadata
    
    Returns:
        Scored polygons
    """
    if not polygons:
        return []
    
    # Compute score thresholds
    areas = [p['area'] for p in polygons]
    contains_counts = [p.get('contains_count', 0) for p in polygons]
    wall_ratios = [p.get('wall_containment_ratio', 0) for p in polygons]
    
    area_threshold = np.percentile(areas, 75) if len(areas) > 1 else 0
    contains_threshold = np.percentile(contains_counts, 60) if len(contains_counts) > 1 else 0
    wall_threshold = 0.5  # Contains >50% of walls
    
    for poly in polygons:
        score = 0
        
        # Layer name boost
        layer = poly.get('layer', '').lower()
        if 'slab' in layer or 'floor' in layer:
            score += 2
        
        # Large area
        if poly['area'] >= area_threshold:
            score += 3
        
        # High containment
        if poly.get('contains_count', 0) >= contains_threshold:
            score += 3
        
        # Contains many walls
        if poly.get('wall_containment_ratio', 0) >= wall_threshold:
            score += 2
        
        poly['score'] = score
    
    # Filter by score threshold
    if len(polygons) > 1:
        scores = [p['score'] for p in polygons]
        score_threshold = np.mean(scores)
        return [p for p in polygons if p['score'] >= score_threshold]
    
    return polygons

def _filter_by_shape_regularity(polygons: List[Dict]) -> List[Dict]:
    """Filter out irregular shapes using compactness metric
    
    Args:
        polygons: Scored polygon candidates
    
    Returns:
        Filtered polygons
    """
    if not polygons:
        return []
    
    for poly in polygons:
        area = poly['area']
        perimeter = poly['perimeter']
        
        # Compactness: (4 * π * area) / (perimeter²)
        # Circle = 1.0, Square ≈ 0.785, Rectangle varies
        if perimeter > 0:
            compactness = (4 * math.pi * area) / (perimeter ** 2)
        else:
            compactness = 0
        
        poly['compactness'] = compactness
    
    # Filter out very irregular shapes (compactness < 0.1)
    # But keep if it's the only candidate
    if len(polygons) > 1:
        return [p for p in polygons if p['compactness'] >= 0.1]
    
    return polygons

def _create_slab_objects(polygons: List[Dict]) -> List[Dict]:
    """Create final slab objects
    
    Args:
        polygons: Valid slab polygons
    
    Returns:
        List of slab objects
    """
    slabs = []
    
    for poly in polygons:
        geom = poly['geometry']
        
        slabs.append({
            'id': str(uuid.uuid4()),
            'polygon': list(geom.exterior.coords),
            'area': poly['area'],
            'perimeter': poly['perimeter'],
            'thickness': 0.15,  # Standard slab thickness in meters
            'wall_containment_ratio': poly.get('wall_containment_ratio', 0),
            'nested_polygon_count': poly.get('contains_count', 0),
            'walls_inside': poly.get('walls_inside', 0),
            'confidence': poly.get('score', 0),
            'compactness': poly.get('compactness', 0),
            'layer': poly.get('layer', '0')
        })
    
    return slabs
