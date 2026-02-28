import numpy as np
import re
from shapely.geometry import Point, LineString
from shapely.strtree import STRtree
from typing import List, Dict, Optional, Tuple
import uuid
from collections import defaultdict

def detect_doors_windows(layer1_output: Dict, layer2_output: Dict, 
                         walls: List[Dict], learned_thickness: Optional[float]) -> Dict:
    """Detect doors and windows using text-schedule linking and geometry
    
    Args:
        layer1_output: Layer 1 output with texts and entities
        layer2_output: Layer 2 output with schedules
        walls: Detected walls from Layer 3 Step 2
        learned_thickness: Learned wall thickness
    
    Returns:
        Dict with detected doors and windows
    """
    # Step 5.1: Extract and filter text candidates
    texts = layer1_output.get('text', [])
    code_candidates = _extract_code_candidates(texts)
    
    # Step 5.2: Validate against schedules
    schedules = layer2_output.get('schedules', {})
    validated_codes = _validate_against_schedules(code_candidates, schedules)
    
    if not validated_codes:
        return {
            'doors': [],
            'windows': [],
            'statistics': {
                'total_doors': 0,
                'total_windows': 0,
                'text_candidates': len(code_candidates)
            }
        }
    
    # Step 5.3: Build wall spatial index
    wall_tree, wall_data = _build_wall_index(walls)
    
    # Step 5.4: Compute adaptive search radius
    search_radius = _compute_search_radius(learned_thickness)
    
    # Step 5.5: Extract arc geometries (door swings)
    arcs = _extract_arcs(layer1_output)
    arc_tree = STRtree([Point(a['center']) for a in arcs]) if arcs else None
    
    # Link codes to walls and geometry
    doors = []
    windows = []
    
    for code_info in validated_codes:
        # Find nearest wall
        linked_wall = _find_nearest_wall(code_info, wall_tree, wall_data, search_radius)
        
        if not linked_wall:
            continue
        
        # Check for arc (door swing)
        has_arc = _check_arc_nearby(code_info, arcs, arc_tree, search_radius) if arc_tree else False
        
        # Score the detection
        score = _score_detection(code_info, linked_wall, has_arc, schedules)
        
        # Create object
        obj = {
            'id': str(uuid.uuid4()),
            'code': code_info['text'],
            'type': code_info['type'],
            'position': code_info['position'],
            'linked_wall': linked_wall['wall_id'],
            'wall_distance': linked_wall['distance'],
            'has_arc': has_arc,
            'confidence': score,
            'layer': code_info.get('layer', '0')
        }
        
        # Add dimensions from schedule
        if code_info['schedule_data']:
            obj['width'] = code_info['schedule_data'].get('width')
            obj['height'] = code_info['schedule_data'].get('height')
        
        # Classify as door or window
        if code_info['type'] == 'door':
            doors.append(obj)
        else:
            windows.append(obj)
    
    return {
        'doors': doors,
        'windows': windows,
        'statistics': {
            'total_doors': len(doors),
            'total_windows': len(windows),
            'text_candidates': len(code_candidates),
            'validated_codes': len(validated_codes)
        }
    }

def _extract_code_candidates(texts: List[Dict]) -> List[Dict]:
    """Extract short alphanumeric text candidates (potential codes)"""
    candidates = []
    
    for text in texts:
        content = text.get('text', '').strip()
        
        # Filter short alphanumeric texts (length <= 4)
        if len(content) <= 4 and content:
            # Check if it has letter + number pattern
            if re.match(r'^[A-Z]\d+$', content, re.IGNORECASE):
                candidates.append({
                    'text': content.upper(),
                    'position': text['position'],
                    'layer': text.get('layer', '0')
                })
    
    return candidates

def _validate_against_schedules(candidates: List[Dict], schedules: Dict) -> List[Dict]:
    """Validate text codes against schedule tables"""
    validated = []
    
    # Build schedule lookup
    schedule_lookup = {}
    for schedule_key, schedule_data in schedules.items():
        headers = schedule_data.get('headers', [])
        data_rows = schedule_data.get('data', [])
        
        # Find code column (usually first column or contains 'mark', 'code', 'no')
        code_col = None
        for i, header in enumerate(headers):
            if i == 0 or any(kw in header.lower() for kw in ['mark', 'code', 'no', 'type']):
                code_col = header
                break
        
        if not code_col:
            continue
        
        # Build lookup
        for row in data_rows:
            code = row.get(code_col, '').strip().upper()
            if code:
                # Determine type from schedule key or code prefix
                if 'door' in schedule_key.lower() or code.startswith('D'):
                    obj_type = 'door'
                elif 'window' in schedule_key.lower() or code.startswith('W'):
                    obj_type = 'window'
                else:
                    obj_type = 'unknown'
                
                # Extract dimensions
                width = _extract_dimension(row, ['width', 'w'])
                height = _extract_dimension(row, ['height', 'h'])
                
                schedule_lookup[code] = {
                    'type': obj_type,
                    'width': width,
                    'height': height,
                    'row': row
                }
    
    # Validate candidates
    for candidate in candidates:
        code = candidate['text']
        if code in schedule_lookup:
            candidate['type'] = schedule_lookup[code]['type']
            candidate['schedule_data'] = schedule_lookup[code]
            validated.append(candidate)
    
    return validated

def _extract_dimension(row: Dict, keywords: List[str]) -> Optional[float]:
    """Extract dimension value from schedule row"""
    for key, value in row.items():
        if any(kw in key.lower() for kw in keywords):
            # Try to extract number
            match = re.search(r'(\d+\.?\d*)', str(value))
            if match:
                try:
                    return float(match.group(1))
                except:
                    pass
    return None

def _build_wall_index(walls: List[Dict]) -> Tuple[Optional[STRtree], List[Dict]]:
    """Build spatial index for walls"""
    if not walls:
        return None, []
    
    wall_data = []
    wall_geoms = []
    
    for wall in walls:
        centerline = wall.get('centerline', [])
        if len(centerline) >= 2:
            line = LineString(centerline)
            wall_geoms.append(line)
            wall_data.append({
                'wall_id': wall['id'],
                'geometry': line,
                'thickness': wall.get('thickness', 0.2)
            })
    
    tree = STRtree(wall_geoms) if wall_geoms else None
    return tree, wall_data

def _compute_search_radius(learned_thickness: Optional[float]) -> float:
    """Compute adaptive search radius based on wall thickness"""
    if learned_thickness:
        return 1.5 * learned_thickness
    return 0.5  # Fallback

def _extract_arcs(layer1_output: Dict) -> List[Dict]:
    """Extract arc geometries (potential door swings)"""
    arcs = []
    geometry = layer1_output.get('geometry', {})
    
    if 'ARC' in geometry:
        for arc_entity in geometry['ARC']:
            coords = arc_entity.get('coordinates', [])
            if len(coords) >= 1:
                center = coords[0]
                cx = center.get('x') if isinstance(center, dict) else center.x
                cy = center.get('y') if isinstance(center, dict) else center.y
                
                # Get arc properties
                metadata = arc_entity.get('metadata', {})
                radius = metadata.get('radius', 0)
                start_angle = metadata.get('start_angle', 0)
                end_angle = metadata.get('end_angle', 0)
                
                # Filter arcs with reasonable door swing angle (60-120 degrees)
                angle_span = abs(end_angle - start_angle)
                if 60 <= angle_span <= 120 and 0.5 <= radius <= 2.0:
                    arcs.append({
                        'center': (cx, cy),
                        'radius': radius,
                        'angle_span': angle_span
                    })
    
    return arcs

def _find_nearest_wall(code_info: Dict, wall_tree: Optional[STRtree], 
                       wall_data: List[Dict], search_radius: float) -> Optional[Dict]:
    """Find nearest wall to text code"""
    if not wall_tree or not wall_data:
        return None
    
    text_point = Point(code_info['position'])
    
    # Query nearby walls
    nearby_indices = wall_tree.query(text_point.buffer(search_radius))
    
    if not nearby_indices:
        return None
    
    # Find closest wall
    min_distance = float('inf')
    closest_wall = None
    
    for idx in nearby_indices:
        if idx < len(wall_data):
            wall = wall_data[idx]
            distance = text_point.distance(wall['geometry'])
            
            if distance < min_distance:
                min_distance = distance
                closest_wall = {
                    'wall_id': wall['wall_id'],
                    'distance': distance,
                    'geometry': wall['geometry']
                }
    
    return closest_wall

def _check_arc_nearby(code_info: Dict, arcs: List[Dict], 
                      arc_tree: STRtree, search_radius: float) -> bool:
    """Check if arc (door swing) exists near text code"""
    if not arcs or not arc_tree:
        return False
    
    text_point = Point(code_info['position'])
    
    # Query nearby arcs
    nearby_indices = arc_tree.query(text_point.buffer(search_radius))
    
    return len(nearby_indices) > 0

def _score_detection(code_info: Dict, linked_wall: Dict, 
                     has_arc: bool, schedules: Dict) -> int:
    """Score door/window detection using multiple signals"""
    score = 0
    
    # Text matches schedule (most important)
    if code_info.get('schedule_data'):
        score += 3
    
    # Near wall
    if linked_wall:
        distance = linked_wall['distance']
        if distance < 0.3:
            score += 2
        elif distance < 0.6:
            score += 1
    
    # Arc detected (door swing)
    if has_arc:
        score += 3
    
    # Type-specific boost
    if code_info['type'] == 'door' and has_arc:
        score += 1  # Doors with arcs are high confidence
    
    return score
