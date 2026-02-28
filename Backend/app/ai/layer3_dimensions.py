import numpy as np
import re
import math
from shapely.geometry import Point, LineString
from shapely.strtree import STRtree
from sklearn.cluster import DBSCAN
from typing import List, Dict, Optional, Tuple
import uuid

def parse_dimensions(layer1_output: Dict, walls: List[Dict], slabs: List[Dict],
                     scale_info: Optional[Dict], learned_thickness: Optional[float]) -> Dict:
    """Parse dimension annotations and link to geometry
    
    Args:
        layer1_output: Layer 1 output with texts
        walls: Detected walls
        slabs: Detected slabs
        scale_info: Scale information from Layer 2
        learned_thickness: Learned wall thickness
    
    Returns:
        Dict with parsed dimensions and overrides
    """
    # Step 6.1: Extract numeric text candidates
    texts = layer1_output.get('text', [])
    numeric_texts = _extract_numeric_texts(texts)
    
    if not numeric_texts:
        return {
            'dimensions': [],
            'overrides': {},
            'statistics': {
                'total_dimensions': 0,
                'numeric_candidates': 0
            }
        }
    
    # Step 6.2: Learn typical dimension text height
    dimension_texts = _filter_by_text_height_clustering(numeric_texts)
    
    # Step 6.3: Build geometry spatial index
    geometry_index = _build_geometry_index(walls, slabs)
    
    # Step 6.4: Compute scale factor
    scale_factor = _compute_scale_factor(scale_info)
    
    # Step 6.5: Compute adaptive search radius
    search_radius = _compute_search_radius(learned_thickness)
    
    # Step 6.6: Associate dimensions to geometry
    dimensions = []
    overrides = {}
    
    for dim_text in dimension_texts:
        # Find candidate geometries
        candidates = _find_candidate_geometries(dim_text, geometry_index, 
                                                search_radius, scale_factor)
        
        if not candidates:
            continue
        
        # Pick best match
        best_match = _select_best_match(candidates)
        
        if best_match:
            # Create dimension object
            dimension = {
                'id': str(uuid.uuid4()),
                'value': dim_text['numeric_value'],
                'unit': dim_text.get('unit', 'mm'),
                'text_position': dim_text['position'],
                'linked_entity_id': best_match['entity_id'],
                'linked_entity_type': best_match['entity_type'],
                'dimension_type': best_match['dimension_type'],
                'source': 'explicit',
                'confidence': best_match['confidence'],
                'scaled_value': best_match['scaled_value'],
                'difference': abs(dim_text['numeric_value'] - best_match['scaled_value'])
            }
            
            dimensions.append(dimension)
            
            # Check if should override
            if _should_override(dimension, scale_factor):
                overrides[best_match['entity_id']] = {
                    'dimension_type': best_match['dimension_type'],
                    'explicit_value': dim_text['numeric_value'],
                    'scaled_value': best_match['scaled_value']
                }
    
    return {
        'dimensions': dimensions,
        'overrides': overrides,
        'statistics': {
            'total_dimensions': len(dimensions),
            'numeric_candidates': len(numeric_texts),
            'filtered_by_height': len(dimension_texts),
            'overrides_applied': len(overrides)
        }
    }

def _extract_numeric_texts(texts: List[Dict]) -> List[Dict]:
    """Extract numeric text candidates"""
    numeric = []
    
    for text in texts:
        content = text.get('text', '').strip()
        
        # Match pure numeric or numeric with unit
        match = re.match(r'^(\d+(?:\.\d+)?)\s*(mm|m|cm)?$', content, re.IGNORECASE)
        
        if match:
            value = float(match.group(1))
            unit = match.group(2).lower() if match.group(2) else 'mm'
            
            # Normalize to mm
            if unit == 'm':
                value *= 1000
            elif unit == 'cm':
                value *= 10
            
            numeric.append({
                'text': content,
                'numeric_value': value,
                'unit': 'mm',
                'position': text['position'],
                'layer': text.get('layer', '0')
            })
    
    return numeric

def _filter_by_text_height_clustering(numeric_texts: List[Dict]) -> List[Dict]:
    """Filter by text height clustering to identify dimension texts
    
    Note: In our current implementation, text height is not available from Layer 1.
    This is a placeholder for when text height metadata is added.
    For now, return all numeric texts.
    """
    # TODO: When text height is available, cluster and filter
    # For now, return all
    return numeric_texts

def _build_geometry_index(walls: List[Dict], slabs: List[Dict]) -> Dict:
    """Build spatial index for walls and slabs"""
    geometries = []
    metadata = []
    
    # Add walls
    for wall in walls:
        centerline = wall.get('centerline', [])
        if len(centerline) >= 2:
            line = LineString(centerline)
            geometries.append(line)
            metadata.append({
                'entity_id': wall['id'],
                'entity_type': 'wall',
                'geometry': line,
                'length': wall.get('length', line.length),
                'thickness': wall.get('thickness', 0.2)
            })
    
    # Add slabs
    for slab in slabs:
        polygon_coords = slab.get('polygon', [])
        if len(polygon_coords) >= 3:
            from shapely.geometry import Polygon
            poly = Polygon(polygon_coords)
            geometries.append(poly)
            metadata.append({
                'entity_id': slab['id'],
                'entity_type': 'slab',
                'geometry': poly,
                'area': slab.get('area', poly.area),
                'perimeter': slab.get('perimeter', poly.length)
            })
    
    tree = STRtree(geometries) if geometries else None
    
    return {
        'tree': tree,
        'metadata': metadata,
        'geometries': geometries
    }

def _compute_scale_factor(scale_info: Optional[Dict]) -> float:
    """Compute scale factor from Layer 2 scale info"""
    if scale_info and scale_info.get('ratio'):
        # ratio = drawing_unit / real_unit
        # For 1:100, ratio = 0.01
        # So real = drawing / ratio
        return 1.0 / scale_info['ratio']
    return 1.0  # No scaling

def _compute_search_radius(learned_thickness: Optional[float]) -> float:
    """Compute adaptive search radius"""
    if learned_thickness:
        return 3.0 * learned_thickness
    return 1.0  # Fallback

def _find_candidate_geometries(dim_text: Dict, geometry_index: Dict,
                                search_radius: float, scale_factor: float) -> List[Dict]:
    """Find candidate geometries for dimension text"""
    tree = geometry_index.get('tree')
    metadata = geometry_index.get('metadata', [])
    
    if not tree or not metadata:
        return []
    
    text_point = Point(dim_text['position'])
    
    # Query nearby geometries
    nearby_indices = tree.query(text_point.buffer(search_radius))
    
    candidates = []
    
    for idx in nearby_indices:
        if idx >= len(metadata):
            continue
        
        geom_meta = metadata[idx]
        geom = geom_meta['geometry']
        
        # Compute distance
        distance = text_point.distance(geom)
        
        # For walls: check if dimension matches length or thickness
        if geom_meta['entity_type'] == 'wall':
            # Length dimension
            scaled_length = geom_meta['length'] * scale_factor
            length_error = abs(dim_text['numeric_value'] - scaled_length) / scaled_length if scaled_length > 0 else 1.0
            
            if length_error < 0.2:  # Within 20%
                candidates.append({
                    'entity_id': geom_meta['entity_id'],
                    'entity_type': 'wall',
                    'dimension_type': 'length',
                    'scaled_value': scaled_length,
                    'distance': distance,
                    'error': length_error,
                    'confidence': 1.0 - length_error
                })
            
            # Thickness dimension
            scaled_thickness = geom_meta['thickness'] * scale_factor * 1000  # Convert to mm
            thickness_error = abs(dim_text['numeric_value'] - scaled_thickness) / scaled_thickness if scaled_thickness > 0 else 1.0
            
            if thickness_error < 0.3:  # Within 30%
                candidates.append({
                    'entity_id': geom_meta['entity_id'],
                    'entity_type': 'wall',
                    'dimension_type': 'thickness',
                    'scaled_value': scaled_thickness,
                    'distance': distance,
                    'error': thickness_error,
                    'confidence': 1.0 - thickness_error
                })
        
        # For slabs: check perimeter or area-derived dimensions
        elif geom_meta['entity_type'] == 'slab':
            scaled_perimeter = geom_meta['perimeter'] * scale_factor
            perimeter_error = abs(dim_text['numeric_value'] - scaled_perimeter) / scaled_perimeter if scaled_perimeter > 0 else 1.0
            
            if perimeter_error < 0.2:
                candidates.append({
                    'entity_id': geom_meta['entity_id'],
                    'entity_type': 'slab',
                    'dimension_type': 'perimeter',
                    'scaled_value': scaled_perimeter,
                    'distance': distance,
                    'error': perimeter_error,
                    'confidence': 1.0 - perimeter_error
                })
    
    return candidates

def _select_best_match(candidates: List[Dict]) -> Optional[Dict]:
    """Select best matching geometry based on error and distance"""
    if not candidates:
        return None
    
    # Sort by error (lower is better), then by distance
    candidates.sort(key=lambda x: (x['error'], x['distance']))
    
    return candidates[0]

def _should_override(dimension: Dict, scale_factor: float) -> bool:
    """Determine if explicit dimension should override scaled measurement
    
    Priority rule: EXPLICIT DIMENSION > SCALE MEASUREMENT
    Override if error is within acceptable tolerance
    """
    error = dimension['difference'] / dimension['scaled_value'] if dimension['scaled_value'] > 0 else 1.0
    
    # Override if error < 15% (adaptive tolerance)
    return error < 0.15
