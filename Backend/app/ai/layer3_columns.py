import numpy as np
import math
from shapely.geometry import Polygon, Point, LineString
from shapely.strtree import STRtree
from sklearn.cluster import DBSCAN
from typing import List, Dict, Optional, Tuple
import uuid

def detect_columns(filtered_entities: List[Dict], slabs: List[Dict], 
                   walls: List[Dict]) -> Dict:
    """Detect columns using size clustering and repetition pattern analysis
    
    Args:
        filtered_entities: Entities from Layer 3 Step 1
        slabs: Detected slabs from Layer 3 Step 3
        walls: Detected walls from Layer 3 Step 2
    
    Returns:
        Dict with detected columns and statistics
    """
    # Step 4.1: Extract closed polygon candidates
    all_closed_polygons = _extract_closed_polygons(filtered_entities)
    
    if len(all_closed_polygons) < 2:
        return {
            'columns': [],
            'statistics': {
                'total_columns': 0,
                'candidates': len(all_closed_polygons)
            }
        }
    
    # Step 4.2: Compute geometric features
    polygons_with_features = _compute_geometric_features(all_closed_polygons)
    
    # Step 4.3: Filter by size distribution (lower-middle range)
    size_candidates = _filter_by_size_percentile(polygons_with_features)
    
    if len(size_candidates) < 2:
        return {
            'columns': [],
            'statistics': {
                'total_columns': 0,
                'candidates': len(all_closed_polygons),
                'size_filtered': len(size_candidates)
            }
        }
    
    # Step 4.4: Filter by shape regularity
    regular_shapes = _filter_by_shape_regularity(size_candidates)
    
    # Step 4.5: Detect repetition patterns (clustering)
    repeated_columns = _detect_repetition_patterns(regular_shapes)
    
    # Step 4.6: Validate spatial context
    if slabs or walls:
        validated_columns = _validate_spatial_context(repeated_columns, slabs, walls)
    else:
        validated_columns = repeated_columns
    
    # Step 4.7: Check grid alignment
    aligned_columns = _check_grid_alignment(validated_columns)
    
    # Score and filter
    scored_columns = _score_column_candidates(aligned_columns, slabs, walls)
    
    # Create final column objects
    columns = _create_column_objects(scored_columns)
    
    return {
        'columns': columns,
        'statistics': {
            'total_columns': len(columns),
            'candidates': len(all_closed_polygons),
            'size_filtered': len(size_candidates),
            'regular_shapes': len(regular_shapes),
            'repeated_patterns': len(repeated_columns),
            'after_validation': len(validated_columns)
        }
    }

def _extract_closed_polygons(entities: List[Dict]) -> List[Dict]:
    """Extract closed polylines and circles as polygons"""
    candidates = []
    
    for entity in entities:
        data = entity['data']
        
        # Closed polylines
        if entity['type'] == 'POLYLINE':
            coords = data.get('coordinates', [])
            is_closed = data.get('closed', False)
            
            if not is_closed or len(coords) < 3:
                continue
            
            points = []
            for coord in coords:
                x = coord.get('x') if isinstance(coord, dict) else coord.x
                y = coord.get('y') if isinstance(coord, dict) else coord.y
                points.append((x, y))
            
            try:
                polygon = Polygon(points)
                if polygon.is_valid and polygon.area > 0.01:
                    candidates.append({
                        'geometry': polygon,
                        'type': 'polyline',
                        'layer': data.get('layer', '0')
                    })
            except:
                continue
        
        # Circles
        elif entity['type'] == 'CIRCLE':
            coords = data.get('coordinates', [])
            if len(coords) >= 1:
                center = coords[0]
                cx = center.get('x') if isinstance(center, dict) else center.x
                cy = center.get('y') if isinstance(center, dict) else center.y
                
                # Get radius from metadata or estimate
                radius = data.get('metadata', {}).get('radius', 0.1)
                
                # Create circular polygon
                circle = Point(cx, cy).buffer(radius)
                if circle.area > 0.01:
                    candidates.append({
                        'geometry': circle,
                        'type': 'circle',
                        'layer': data.get('layer', '0')
                    })
    
    return candidates

def _compute_geometric_features(polygons: List[Dict]) -> List[Dict]:
    """Compute geometric features for each polygon"""
    for poly in polygons:
        geom = poly['geometry']
        
        # Basic metrics
        poly['area'] = geom.area
        poly['perimeter'] = geom.length
        
        # Bounding box
        minx, miny, maxx, maxy = geom.bounds
        width = maxx - minx
        height = maxy - miny
        
        poly['width'] = width
        poly['height'] = height
        poly['centroid'] = geom.centroid
        
        # Aspect ratio
        if height > 0:
            poly['aspect_ratio'] = width / height
        else:
            poly['aspect_ratio'] = 1.0
        
        # Compactness (circularity)
        if poly['perimeter'] > 0:
            poly['compactness'] = (4 * math.pi * poly['area']) / (poly['perimeter'] ** 2)
        else:
            poly['compactness'] = 0
        
        # Rectangularity
        try:
            min_rect = geom.minimum_rotated_rectangle
            if min_rect.area > 0:
                poly['rectangularity'] = poly['area'] / min_rect.area
            else:
                poly['rectangularity'] = 0
        except:
            poly['rectangularity'] = 0
    
    return polygons

def _filter_by_size_percentile(polygons: List[Dict]) -> List[Dict]:
    """Filter by size percentile (10th-40th percentile for columns)"""
    if not polygons:
        return []
    
    areas = [p['area'] for p in polygons]
    q10 = np.percentile(areas, 10)
    q40 = np.percentile(areas, 40)
    
    return [p for p in polygons if q10 <= p['area'] <= q40]

def _filter_by_shape_regularity(polygons: List[Dict]) -> List[Dict]:
    """Filter by shape regularity (rectangular or circular)"""
    if not polygons:
        return []
    
    regular = []
    
    for poly in polygons:
        # Check rectangularity (close to 1 = good rectangle)
        is_rectangular = poly['rectangularity'] > 0.7
        
        # Check circularity (close to 1 = good circle)
        is_circular = poly['compactness'] > 0.7
        
        # Check aspect ratio (close to 1 = square-like)
        is_square_like = 0.5 <= poly['aspect_ratio'] <= 2.0
        
        if is_rectangular or is_circular or is_square_like:
            regular.append(poly)
    
    return regular

def _detect_repetition_patterns(polygons: List[Dict]) -> List[Dict]:
    """Detect repeated patterns using clustering on size features
    
    This is the KEY intelligence - columns repeat with similar sizes
    """
    if len(polygons) < 2:
        return polygons
    
    # Extract features: (area, aspect_ratio)
    features = np.array([[p['area'], p['aspect_ratio']] for p in polygons])
    
    # Normalize features
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # Cluster using DBSCAN
    # eps adaptive: 0.5 works well for normalized features
    clustering = DBSCAN(eps=0.5, min_samples=2).fit(features_scaled)
    
    labels = clustering.labels_
    
    # Find largest cluster (most repeated pattern)
    unique_labels = [l for l in set(labels) if l != -1]
    
    if not unique_labels:
        # No clusters found, return all
        return polygons
    
    # Get cluster sizes
    cluster_sizes = [(l, list(labels).count(l)) for l in unique_labels]
    largest_cluster = max(cluster_sizes, key=lambda x: x[1])[0]
    
    # Return polygons in largest cluster
    repeated = [polygons[i] for i, l in enumerate(labels) if l == largest_cluster]
    
    # Mark cluster membership
    for i, poly in enumerate(polygons):
        poly['cluster_id'] = int(labels[i]) if i < len(labels) else -1
        poly['is_repeated'] = labels[i] == largest_cluster if i < len(labels) else False
    
    return repeated

def _validate_spatial_context(columns: List[Dict], slabs: List[Dict], 
                               walls: List[Dict]) -> List[Dict]:
    """Validate columns using spatial context (slab containment, wall proximity)"""
    validated = []
    
    # Build slab geometries
    slab_geoms = []
    for slab in slabs:
        try:
            slab_poly = Polygon(slab['polygon'])
            slab_geoms.append(slab_poly)
        except:
            continue
    
    # Build wall spatial index
    wall_lines = []
    for wall in walls:
        centerline = wall.get('centerline', [])
        if len(centerline) >= 2:
            wall_lines.append(LineString(centerline))
    
    wall_tree = STRtree(wall_lines) if wall_lines else None
    
    for col in columns:
        centroid = col['centroid']
        
        # Check slab containment
        inside_slab = any(slab.contains(centroid) for slab in slab_geoms)
        col['inside_slab'] = inside_slab
        
        # Check wall proximity
        if wall_tree:
            nearest_wall_dist = min([centroid.distance(w) for w in wall_lines]) if wall_lines else float('inf')
            col['nearest_wall_distance'] = nearest_wall_dist
        else:
            col['nearest_wall_distance'] = float('inf')
        
        validated.append(col)
    
    return validated

def _check_grid_alignment(columns: List[Dict]) -> List[Dict]:
    """Check if columns align in grid pattern"""
    if len(columns) < 3:
        for col in columns:
            col['grid_aligned'] = False
        return columns
    
    # Extract centroids
    x_coords = [col['centroid'].x for col in columns]
    y_coords = [col['centroid'].y for col in columns]
    
    # Cluster X and Y coordinates
    x_clusters = _cluster_1d_coordinates(x_coords)
    y_clusters = _cluster_1d_coordinates(y_coords)
    
    # If multiple columns share X or Y → grid pattern
    grid_detected = len(x_clusters) > 1 or len(y_clusters) > 1
    
    for col in columns:
        col['grid_aligned'] = grid_detected
    
    return columns

def _cluster_1d_coordinates(coords: List[float], tolerance: float = 0.5) -> List[List[float]]:
    """Cluster 1D coordinates to detect alignment"""
    if len(coords) < 2:
        return []
    
    sorted_coords = sorted(coords)
    clusters = []
    current_cluster = [sorted_coords[0]]
    
    for i in range(1, len(sorted_coords)):
        if sorted_coords[i] - sorted_coords[i-1] < tolerance:
            current_cluster.append(sorted_coords[i])
        else:
            if len(current_cluster) > 1:
                clusters.append(current_cluster)
            current_cluster = [sorted_coords[i]]
    
    if len(current_cluster) > 1:
        clusters.append(current_cluster)
    
    return clusters

def _score_column_candidates(columns: List[Dict], slabs: List[Dict], 
                              walls: List[Dict]) -> List[Dict]:
    """Score column candidates using multiple criteria"""
    if not columns:
        return []
    
    for col in columns:
        score = 0
        
        # Repeated pattern (most important)
        if col.get('is_repeated', False):
            score += 3
        
        # High rectangularity or circularity
        if col.get('rectangularity', 0) > 0.8 or col.get('compactness', 0) > 0.8:
            score += 2
        
        # Inside slab
        if col.get('inside_slab', False):
            score += 2
        
        # Near wall junction
        if col.get('nearest_wall_distance', float('inf')) < 0.5:
            score += 1
        
        # Grid aligned
        if col.get('grid_aligned', False):
            score += 2
        
        col['score'] = score
    
    # Filter by adaptive threshold
    if len(columns) > 1:
        scores = [c['score'] for c in columns]
        threshold = np.mean(scores) + np.std(scores) / 2
        return [c for c in columns if c['score'] >= threshold]
    
    return columns

def _create_column_objects(columns: List[Dict]) -> List[Dict]:
    """Create final column objects"""
    result = []
    
    for col in columns:
        geom = col['geometry']
        
        result.append({
            'id': str(uuid.uuid4()),
            'polygon': list(geom.exterior.coords),
            'area': col['area'],
            'width': col['width'],
            'depth': col['height'],  # Rename for clarity
            'height': 3.0,  # Story height
            'aspect_ratio': col['aspect_ratio'],
            'centroid': [col['centroid'].x, col['centroid'].y],
            'confidence': col.get('score', 0),
            'type': col.get('type', 'polyline'),
            'layer': col.get('layer', '0'),
            'inside_slab': col.get('inside_slab', False),
            'grid_aligned': col.get('grid_aligned', False),
            'rectangularity': col.get('rectangularity', 0),
            'compactness': col.get('compactness', 0)
        })
    
    return result
