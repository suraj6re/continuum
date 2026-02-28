"""Level Assignment - Detects and Assigns Floor Levels"""
from typing import List, Dict
import re

def extract_level_from_text(text_entities: List[Dict]) -> str:
    """Extract floor level from text labels
    
    Args:
        text_entities: List of text entities from Layer 2
    
    Returns:
        Detected floor level or 'Ground Floor'
    """
    level_keywords = [
        r'ground\s*floor',
        r'first\s*floor',
        r'second\s*floor',
        r'basement',
        r'floor\s*(\d+)',
        r'level\s*(\d+)',
        r'storey\s*(\d+)'
    ]
    
    for text_entity in text_entities:
        text = text_entity.get('text', '').lower()
        
        for pattern in level_keywords:
            match = re.search(pattern, text)
            if match:
                if 'ground' in text:
                    return 'Ground Floor'
                elif 'first' in text:
                    return 'First Floor'
                elif 'second' in text:
                    return 'Second Floor'
                elif 'basement' in text:
                    return 'Basement'
                elif match.groups():
                    floor_num = match.group(1)
                    return f'Floor {floor_num}'
    
    return 'Ground Floor'

def cluster_by_y_coordinate(nodes: List[Dict], threshold: float = 3.0) -> Dict[str, List[Dict]]:
    """Cluster elements by Y-coordinate to detect floors
    
    Args:
        nodes: List of canonical nodes
        threshold: Y-coordinate clustering threshold
    
    Returns:
        Dictionary mapping level names to nodes
    """
    if not nodes:
        return {'Ground Floor': []}
    
    # Extract Y coordinates
    y_coords = []
    for node in nodes:
        geom = node.get('geometry', {}).get('centerline', [])
        if geom:
            y_coords.append((node, geom[0][1]))
    
    if not y_coords:
        return {'Ground Floor': nodes}
    
    # Sort by Y coordinate
    y_coords.sort(key=lambda x: x[1])
    
    # Simple clustering - group by Y ranges
    clusters = []
    current_cluster = [y_coords[0]]
    
    for i in range(1, len(y_coords)):
        if abs(y_coords[i][1] - current_cluster[-1][1]) < threshold:
            current_cluster.append(y_coords[i])
        else:
            clusters.append(current_cluster)
            current_cluster = [y_coords[i]]
    
    clusters.append(current_cluster)
    
    # Assign level names
    level_map = {}
    for i, cluster in enumerate(clusters):
        level_name = f'Floor {i}' if i > 0 else 'Ground Floor'
        level_map[level_name] = [item[0] for item in cluster]
    
    return level_map

def assign_levels(nodes: List[Dict], layer2_output: Dict) -> List[Dict]:
    """Assign floor levels to all nodes
    
    Args:
        nodes: List of canonical nodes
        layer2_output: Layer 2 output with text entities
    
    Returns:
        Nodes with assigned levels
    """
    # Try to extract level from text
    text_entities = layer2_output.get('text', [])
    detected_level = extract_level_from_text(text_entities)
    
    # Check if multi-floor by Y-coordinate clustering
    level_clusters = cluster_by_y_coordinate(nodes)
    
    # If only one cluster, use detected level from text
    if len(level_clusters) == 1:
        for node in nodes:
            node['level'] = detected_level
    else:
        # Multi-floor: assign based on clusters
        for level_name, cluster_nodes in level_clusters.items():
            for node in cluster_nodes:
                node['level'] = level_name
    
    return nodes
