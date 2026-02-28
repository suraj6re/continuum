import networkx as nx
import numpy as np
from shapely.geometry import Point, LineString, Polygon
from shapely.strtree import STRtree
from sklearn.cluster import DBSCAN
from typing import List, Dict, Tuple

def build_relationship_graph(walls: List[Dict], slabs: List[Dict], columns: List[Dict],
                             doors: List[Dict], windows: List[Dict]) -> Dict:
    """Build relationship graph using adaptive tolerance and geometric validation
    
    Args:
        walls: Detected walls
        slabs: Detected slabs
        columns: Detected columns
        doors: Detected doors
        windows: Detected windows
    
    Returns:
        Dict with graph and relationships
    """
    # Step 7.1: Initialize graph
    G = nx.Graph()
    
    # Add nodes
    for wall in walls:
        G.add_node(wall['id'], type='wall', data=wall)
    
    for slab in slabs:
        G.add_node(slab['id'], type='slab', data=slab)
    
    for column in columns:
        G.add_node(column['id'], type='column', data=column)
    
    for door in doors:
        G.add_node(door['id'], type='door', data=door)
    
    for window in windows:
        G.add_node(window['id'], type='window', data=window)
    
    # Step 7.2: Learn adaptive tolerance
    tolerance = _learn_adaptive_tolerance(walls)
    
    # Step 7.3: Build spatial indexes
    wall_index = _build_wall_index(walls)
    slab_index = _build_slab_index(slabs)
    
    # Step 7.4: Door ↔ Wall relationships
    door_wall_edges = _link_doors_to_walls(doors, wall_index, tolerance)
    for edge in door_wall_edges:
        G.add_edge(edge['from'], edge['to'], **edge['attributes'])
    
    # Step 7.5: Window ↔ Wall relationships
    window_wall_edges = _link_windows_to_walls(windows, wall_index, tolerance)
    for edge in window_wall_edges:
        G.add_edge(edge['from'], edge['to'], **edge['attributes'])
    
    # Step 7.6: Column ↔ Slab relationships
    column_slab_edges = _link_columns_to_slabs(columns, slab_index)
    for edge in column_slab_edges:
        G.add_edge(edge['from'], edge['to'], **edge['attributes'])
    
    # Step 7.7: Wall ↔ Wall intersections (junctions)
    wall_wall_edges = _detect_wall_junctions(walls, tolerance)
    for edge in wall_wall_edges:
        G.add_edge(edge['from'], edge['to'], **edge['attributes'])
    
    # Step 7.8: Validate structural consistency
    validation = _validate_graph_consistency(G, doors, columns)
    
    # Step 7.9: Export relationships
    relationships = _export_relationships(G)
    
    return {
        'graph': G,
        'relationships': relationships,
        'statistics': {
            'nodes': G.number_of_nodes(),
            'edges': G.number_of_edges(),
            'door_wall_links': len(door_wall_edges),
            'window_wall_links': len(window_wall_edges),
            'column_slab_links': len(column_slab_edges),
            'wall_junctions': len(wall_wall_edges),
            'connected_components': nx.number_connected_components(G)
        },
        'validation': validation,
        'tolerance': tolerance
    }

def _learn_adaptive_tolerance(walls: List[Dict]) -> float:
    """Learn adaptive tolerance from wall geometry"""
    if not walls:
        return 0.1  # Fallback
    
    lengths = [w.get('length', 1.0) for w in walls]
    median_length = np.median(lengths)
    
    # Tolerance = 1% of median wall length
    tolerance = median_length * 0.01
    
    # Clamp to reasonable range
    return max(0.05, min(tolerance, 0.5))

def _build_wall_index(walls: List[Dict]) -> Dict:
    """Build spatial index for walls"""
    geometries = []
    metadata = []
    
    for wall in walls:
        centerline = wall.get('centerline', [])
        if len(centerline) >= 2:
            line = LineString(centerline)
            geometries.append(line)
            metadata.append({
                'id': wall['id'],
                'geometry': line
            })
    
    tree = STRtree(geometries) if geometries else None
    
    return {
        'tree': tree,
        'metadata': metadata,
        'geometries': geometries
    }

def _build_slab_index(slabs: List[Dict]) -> Dict:
    """Build spatial index for slabs"""
    geometries = []
    metadata = []
    
    for slab in slabs:
        polygon_coords = slab.get('polygon', [])
        if len(polygon_coords) >= 3:
            poly = Polygon(polygon_coords)
            geometries.append(poly)
            metadata.append({
                'id': slab['id'],
                'geometry': poly
            })
    
    tree = STRtree(geometries) if geometries else None
    
    return {
        'tree': tree,
        'metadata': metadata,
        'geometries': geometries
    }

def _link_doors_to_walls(doors: List[Dict], wall_index: Dict, tolerance: float) -> List[Dict]:
    """Link doors to walls using projection validation"""
    edges = []
    
    tree = wall_index.get('tree')
    metadata = wall_index.get('metadata', [])
    
    if not tree or not metadata:
        return edges
    
    for door in doors:
        position = door.get('position', [0, 0])
        door_point = Point(position)
        
        # Query nearby walls
        search_buffer = tolerance * 3
        nearby_indices = tree.query(door_point.buffer(search_buffer))
        
        best_wall = None
        min_distance = float('inf')
        
        for idx in nearby_indices:
            if idx >= len(metadata):
                continue
            
            wall_meta = metadata[idx]
            wall_line = wall_meta['geometry']
            
            # Project door point onto wall
            projected_point = wall_line.interpolate(wall_line.project(door_point))
            distance = door_point.distance(projected_point)
            
            # Check if projection is within wall segment
            projection_param = wall_line.project(door_point, normalized=True)
            if 0 <= projection_param <= 1 and distance < min_distance:
                min_distance = distance
                best_wall = wall_meta['id']
        
        if best_wall and min_distance < tolerance * 2:
            edges.append({
                'from': door['id'],
                'to': best_wall,
                'attributes': {
                    'type': 'attached_to',
                    'distance': min_distance,
                    'confidence': 1.0 - (min_distance / (tolerance * 2))
                }
            })
    
    return edges

def _link_windows_to_walls(windows: List[Dict], wall_index: Dict, tolerance: float) -> List[Dict]:
    """Link windows to walls (same logic as doors)"""
    edges = []
    
    tree = wall_index.get('tree')
    metadata = wall_index.get('metadata', [])
    
    if not tree or not metadata:
        return edges
    
    for window in windows:
        position = window.get('position', [0, 0])
        window_point = Point(position)
        
        search_buffer = tolerance * 3
        nearby_indices = tree.query(window_point.buffer(search_buffer))
        
        best_wall = None
        min_distance = float('inf')
        
        for idx in nearby_indices:
            if idx >= len(metadata):
                continue
            
            wall_meta = metadata[idx]
            wall_line = wall_meta['geometry']
            
            projected_point = wall_line.interpolate(wall_line.project(window_point))
            distance = window_point.distance(projected_point)
            
            projection_param = wall_line.project(window_point, normalized=True)
            if 0 <= projection_param <= 1 and distance < min_distance:
                min_distance = distance
                best_wall = wall_meta['id']
        
        if best_wall and min_distance < tolerance * 2:
            edges.append({
                'from': window['id'],
                'to': best_wall,
                'attributes': {
                    'type': 'attached_to',
                    'distance': min_distance,
                    'confidence': 1.0 - (min_distance / (tolerance * 2))
                }
            })
    
    return edges

def _link_columns_to_slabs(columns: List[Dict], slab_index: Dict) -> List[Dict]:
    """Link columns to slabs using containment"""
    edges = []
    
    tree = slab_index.get('tree')
    metadata = slab_index.get('metadata', [])
    
    if not tree or not metadata:
        return edges
    
    for column in columns:
        centroid = column.get('centroid', [0, 0])
        col_point = Point(centroid)
        
        # Query containing slabs
        containing_indices = tree.query(col_point)
        
        for idx in containing_indices:
            if idx >= len(metadata):
                continue
            
            slab_meta = metadata[idx]
            slab_poly = slab_meta['geometry']
            
            if slab_poly.contains(col_point):
                edges.append({
                    'from': column['id'],
                    'to': slab_meta['id'],
                    'attributes': {
                        'type': 'inside',
                        'confidence': 1.0
                    }
                })
                break  # Column can only be in one slab
    
    return edges

def _detect_wall_junctions(walls: List[Dict], tolerance: float) -> List[Dict]:
    """Detect wall-wall intersections using endpoint clustering"""
    edges = []
    
    if len(walls) < 2:
        return edges
    
    # Extract all endpoints
    endpoints = []
    endpoint_wall_map = []
    
    for wall in walls:
        centerline = wall.get('centerline', [])
        if len(centerline) >= 2:
            start = centerline[0]
            end = centerline[-1]
            
            endpoints.append(start)
            endpoint_wall_map.append((wall['id'], 'start'))
            
            endpoints.append(end)
            endpoint_wall_map.append((wall['id'], 'end'))
    
    if len(endpoints) < 2:
        return edges
    
    # Cluster endpoints using DBSCAN
    endpoints_array = np.array(endpoints)
    clustering = DBSCAN(eps=tolerance, min_samples=2).fit(endpoints_array)
    
    labels = clustering.labels_
    
    # For each cluster (junction), connect walls
    unique_labels = set(labels)
    
    for label in unique_labels:
        if label == -1:  # Noise
            continue
        
        # Get walls in this junction
        cluster_indices = np.where(labels == label)[0]
        cluster_walls = [endpoint_wall_map[i][0] for i in cluster_indices]
        
        # Create edges between walls in same junction
        unique_walls = list(set(cluster_walls))
        for i in range(len(unique_walls)):
            for j in range(i + 1, len(unique_walls)):
                edges.append({
                    'from': unique_walls[i],
                    'to': unique_walls[j],
                    'attributes': {
                        'type': 'intersects',
                        'junction_id': int(label),
                        'confidence': 1.0
                    }
                })
    
    return edges

def _validate_graph_consistency(G: nx.Graph, doors: List[Dict], columns: List[Dict]) -> Dict:
    """Validate structural consistency of graph"""
    validation = {
        'valid': True,
        'warnings': []
    }
    
    # Check: Each door should attach to exactly one wall
    for door in doors:
        door_id = door['id']
        if door_id in G:
            neighbors = list(G.neighbors(door_id))
            wall_neighbors = [n for n in neighbors if G.nodes[n]['type'] == 'wall']
            
            if len(wall_neighbors) == 0:
                validation['warnings'].append(f"Door {door_id} not attached to any wall")
            elif len(wall_neighbors) > 1:
                validation['warnings'].append(f"Door {door_id} attached to multiple walls")
    
    # Check: Each column should be inside exactly one slab
    for column in columns:
        column_id = column['id']
        if column_id in G:
            neighbors = list(G.neighbors(column_id))
            slab_neighbors = [n for n in neighbors if G.nodes[n]['type'] == 'slab']
            
            if len(slab_neighbors) == 0:
                validation['warnings'].append(f"Column {column_id} not inside any slab")
            elif len(slab_neighbors) > 1:
                validation['warnings'].append(f"Column {column_id} inside multiple slabs")
    
    # Check: Graph connectivity
    num_components = nx.number_connected_components(G)
    if num_components > 1:
        validation['warnings'].append(f"Graph has {num_components} disconnected components")
    
    validation['valid'] = len(validation['warnings']) == 0
    
    return validation

def _export_relationships(G: nx.Graph) -> List[Dict]:
    """Export relationships from graph"""
    relationships = []
    
    for u, v, data in G.edges(data=True):
        relationships.append({
            'from': u,
            'from_type': G.nodes[u]['type'],
            'to': v,
            'to_type': G.nodes[v]['type'],
            'relationship_type': data.get('type', 'unknown'),
            'confidence': data.get('confidence', 1.0),
            'distance': data.get('distance'),
            'junction_id': data.get('junction_id')
        })
    
    return relationships
