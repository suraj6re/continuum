"""Duplicate & Overlap Merger - Prevents Double QTO"""
from typing import List, Dict
import math

def distance(p1: List[float], p2: List[float]) -> float:
    """Calculate Euclidean distance between two points"""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def centerline_overlap(line1: List[List[float]], line2: List[List[float]], tolerance: float = 0.1) -> bool:
    """Check if two centerlines overlap within tolerance"""
    if not line1 or not line2:
        return False
    
    # Check if endpoints are close
    d1 = distance(line1[0], line2[0])
    d2 = distance(line1[-1], line2[-1])
    d3 = distance(line1[0], line2[-1])
    d4 = distance(line1[-1], line2[0])
    
    return min(d1, d2, d3, d4) < tolerance

def merge_walls(wall1: Dict, wall2: Dict) -> Dict:
    """Merge two overlapping walls"""
    merged = wall1.copy()
    
    # Recalculate length (take max)
    len1 = wall1['dimensions'].get('length', 0)
    len2 = wall2['dimensions'].get('length', 0)
    merged['dimensions']['length'] = max(len1, len2)
    
    # Average confidence
    conf1 = wall1.get('confidence', 0.5)
    conf2 = wall2.get('confidence', 0.5)
    merged['confidence'] = (conf1 + conf2) / 2
    
    # Keep better material
    if wall2['material']['category'] != 'Unknown':
        merged['material'] = wall2['material']
    
    return merged

def merge_columns(col1: Dict, col2: Dict) -> Dict:
    """Merge two nearly identical columns"""
    merged = col1.copy()
    
    # Average dimensions
    w1 = col1['dimensions'].get('width', 0)
    w2 = col2['dimensions'].get('width', 0)
    d1 = col1['dimensions'].get('depth', 0)
    d2 = col2['dimensions'].get('depth', 0)
    
    merged['dimensions']['width'] = (w1 + w2) / 2
    merged['dimensions']['depth'] = (d1 + d2) / 2
    
    # Average confidence
    merged['confidence'] = (col1.get('confidence', 0.5) + col2.get('confidence', 0.5)) / 2
    
    return merged

def merge_duplicate_nodes(nodes: List[Dict], tolerance: float = 0.1) -> List[Dict]:
    """Merge duplicate and overlapping nodes
    
    Args:
        nodes: List of canonical nodes
        tolerance: Distance tolerance for overlap detection
    
    Returns:
        Deduplicated nodes
    """
    if not nodes:
        return []
    
    merged_nodes = []
    merged_ids = set()
    
    for i, node1 in enumerate(nodes):
        if node1['id'] in merged_ids:
            continue
        
        # Check for duplicates
        found_duplicate = False
        
        for j, node2 in enumerate(nodes[i+1:], start=i+1):
            if node2['id'] in merged_ids:
                continue
            
            # Only merge same types
            if node1['type'] != node2['type']:
                continue
            
            # Check for overlap based on type
            if node1['type'] == 'Wall':
                centerline1 = node1.get('geometry', {}).get('centerline', [])
                centerline2 = node2.get('geometry', {}).get('centerline', [])
                
                if centerline_overlap(centerline1, centerline2, tolerance):
                    # Merge walls
                    merged = merge_walls(node1, node2)
                    merged_nodes.append(merged)
                    merged_ids.add(node1['id'])
                    merged_ids.add(node2['id'])
                    found_duplicate = True
                    break
            
            elif node1['type'] == 'Column':
                # Check if columns are at same location
                geom1 = node1.get('geometry', {}).get('centerline', [[0,0]])
                geom2 = node2.get('geometry', {}).get('centerline', [[0,0]])
                
                if geom1 and geom2:
                    dist = distance(geom1[0], geom2[0])
                    if dist < tolerance:
                        # Merge columns
                        merged = merge_columns(node1, node2)
                        merged_nodes.append(merged)
                        merged_ids.add(node1['id'])
                        merged_ids.add(node2['id'])
                        found_duplicate = True
                        break
        
        # If no duplicate found, keep original
        if not found_duplicate:
            merged_nodes.append(node1)
            merged_ids.add(node1['id'])
    
    return merged_nodes
