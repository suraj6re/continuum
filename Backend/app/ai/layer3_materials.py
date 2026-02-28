import numpy as np
from difflib import get_close_matches
from sklearn.cluster import DBSCAN
from collections import Counter
from typing import List, Dict, Optional
import networkx as nx

def assign_materials(walls: List[Dict], slabs: List[Dict], columns: List[Dict],
                     legend_dictionary: Dict, schedules: Dict, 
                     graph: nx.Graph) -> Dict:
    """Assign materials using evidence-based scoring system
    
    Args:
        walls: Detected walls
        slabs: Detected slabs
        columns: Detected columns
        legend_dictionary: Legend from Layer 2
        schedules: Schedule tables from Layer 2
        graph: Relationship graph from Step 7
    
    Returns:
        Dict with material assignments and statistics
    """
    # Step 8.1: Build material catalog
    material_catalog = _build_material_catalog(legend_dictionary, schedules, walls, slabs, columns)
    
    # Step 8.2: Assign materials to walls
    walls_with_materials = _assign_wall_materials(walls, material_catalog, legend_dictionary, 
                                                   schedules, graph)
    
    # Step 8.3: Assign materials to slabs
    slabs_with_materials = _assign_slab_materials(slabs, material_catalog, legend_dictionary,
                                                   schedules, graph)
    
    # Step 8.4: Assign materials to columns
    columns_with_materials = _assign_column_materials(columns, material_catalog, legend_dictionary,
                                                      schedules, graph)
    
    # Step 8.5: Compute statistics
    statistics = _compute_material_statistics(walls_with_materials, slabs_with_materials,
                                              columns_with_materials)
    
    return {
        'walls': walls_with_materials,
        'slabs': slabs_with_materials,
        'columns': columns_with_materials,
        'material_catalog': material_catalog,
        'statistics': statistics
    }

def _build_material_catalog(legend_dict: Dict, schedules: Dict,
                            walls: List[Dict], slabs: List[Dict], 
                            columns: List[Dict]) -> List[str]:
    """Build normalized material catalog from all sources"""
    materials = set()
    
    # From legend
    for material in legend_dict.values():
        materials.add(_normalize_material(material))
    
    # From schedules
    for schedule_data in schedules.values():
        for row in schedule_data.get('data', []):
            for value in row.values():
                # Check if value contains material keywords
                value_str = str(value).lower()
                if any(kw in value_str for kw in ['brick', 'concrete', 'rcc', 'glass', 'wood', 'steel']):
                    materials.add(_normalize_material(value_str))
    
    # From layer names
    for element in walls + slabs + columns:
        layer = element.get('layer', '')
        tokens = _tokenize_layer_name(layer)
        for token in tokens:
            if len(token) > 3:  # Filter short tokens
                materials.add(_normalize_material(token))
    
    # Filter and return
    material_list = [m for m in materials if m and len(m) > 2]
    
    # Add common fallbacks if catalog is empty
    if not material_list:
        material_list = ['brick', 'concrete', 'rcc', 'glass', 'wood', 'steel']
    
    return material_list

def _normalize_material(text: str) -> str:
    """Normalize material name"""
    return text.strip().lower().replace('_', ' ')

def _tokenize_layer_name(layer_name: str) -> List[str]:
    """Tokenize layer name"""
    import re
    # Split by common delimiters
    tokens = re.split(r'[_\-\s]+', layer_name.lower())
    return [t for t in tokens if t]

def _assign_wall_materials(walls: List[Dict], material_catalog: List[str],
                           legend_dict: Dict, schedules: Dict,
                           graph: nx.Graph) -> List[Dict]:
    """Assign materials to walls using evidence scoring"""
    
    # Learn thickness clusters
    thickness_material_map = _learn_thickness_clusters(walls, material_catalog, legend_dict)
    
    for wall in walls:
        material_scores = {m: 0.0 for m in material_catalog}
        evidence_sources = []
        
        # Evidence 1: Legend dictionary (weight: 5)
        # Note: Walls don't typically have hatch patterns in our current model
        # This would be used if hatch pattern data is available
        
        # Evidence 2: Layer name semantic parsing (weight: 3)
        layer = wall.get('layer', '')
        layer_tokens = _tokenize_layer_name(layer)
        for token in layer_tokens:
            matches = get_close_matches(token, material_catalog, n=1, cutoff=0.6)
            if matches:
                material_scores[matches[0]] += 3.0
                evidence_sources.append('layer_semantic')
        
        # Evidence 3: Thickness clustering (weight: 2)
        thickness = wall.get('thickness', 0)
        if thickness in thickness_material_map:
            material = thickness_material_map[thickness]
            if material in material_scores:
                material_scores[material] += 2.0
                evidence_sources.append('thickness_cluster')
        
        # Evidence 4: Graph propagation (weight: 1)
        if graph and wall['id'] in graph:
            neighbors = list(graph.neighbors(wall['id']))
            for neighbor_id in neighbors:
                neighbor_data = graph.nodes[neighbor_id].get('data', {})
                neighbor_material = neighbor_data.get('material')
                if neighbor_material and neighbor_material in material_scores:
                    material_scores[neighbor_material] += 1.0
                    evidence_sources.append('graph_propagation')
        
        # Normalize and assign
        total_score = sum(material_scores.values())
        if total_score > 0:
            confidences = {m: score / total_score for m, score in material_scores.items()}
            best_material = max(material_scores, key=material_scores.get)
            confidence = confidences[best_material]
        else:
            # Fallback: most common material
            best_material = _get_fallback_material(walls, 'brick')
            confidence = 0.3
            evidence_sources.append('fallback')
        
        wall['material'] = best_material
        wall['material_confidence'] = confidence
        wall['material_evidence'] = list(set(evidence_sources))
    
    return walls

def _assign_slab_materials(slabs: List[Dict], material_catalog: List[str],
                           legend_dict: Dict, schedules: Dict,
                           graph: nx.Graph) -> List[Dict]:
    """Assign materials to slabs"""
    
    for slab in slabs:
        material_scores = {m: 0.0 for m in material_catalog}
        evidence_sources = []
        
        # Evidence 1: Layer name
        layer = slab.get('layer', '')
        layer_tokens = _tokenize_layer_name(layer)
        for token in layer_tokens:
            matches = get_close_matches(token, material_catalog, n=1, cutoff=0.6)
            if matches:
                material_scores[matches[0]] += 3.0
                evidence_sources.append('layer_semantic')
        
        # Evidence 2: Default slab material (RCC/Concrete)
        for material in material_catalog:
            if 'concrete' in material or 'rcc' in material:
                material_scores[material] += 2.0
                evidence_sources.append('type_heuristic')
        
        # Normalize and assign
        total_score = sum(material_scores.values())
        if total_score > 0:
            confidences = {m: score / total_score for m, score in material_scores.items()}
            best_material = max(material_scores, key=material_scores.get)
            confidence = confidences[best_material]
        else:
            best_material = _get_fallback_material(slabs, 'concrete')
            confidence = 0.3
            evidence_sources.append('fallback')
        
        slab['material'] = best_material
        slab['material_confidence'] = confidence
        slab['material_evidence'] = list(set(evidence_sources))
    
    return slabs

def _assign_column_materials(columns: List[Dict], material_catalog: List[str],
                             legend_dict: Dict, schedules: Dict,
                             graph: nx.Graph) -> List[Dict]:
    """Assign materials to columns"""
    
    for column in columns:
        material_scores = {m: 0.0 for m in material_catalog}
        evidence_sources = []
        
        # Evidence 1: Layer name
        layer = column.get('layer', '')
        layer_tokens = _tokenize_layer_name(layer)
        for token in layer_tokens:
            matches = get_close_matches(token, material_catalog, n=1, cutoff=0.6)
            if matches:
                material_scores[matches[0]] += 3.0
                evidence_sources.append('layer_semantic')
        
        # Evidence 2: Graph propagation from slab
        if graph and column['id'] in graph:
            neighbors = list(graph.neighbors(column['id']))
            for neighbor_id in neighbors:
                neighbor_node = graph.nodes[neighbor_id]
                if neighbor_node.get('type') == 'slab':
                    neighbor_data = neighbor_node.get('data', {})
                    neighbor_material = neighbor_data.get('material')
                    if neighbor_material and neighbor_material in material_scores:
                        material_scores[neighbor_material] += 2.0
                        evidence_sources.append('graph_propagation')
        
        # Evidence 3: Default column material (RCC/Concrete)
        for material in material_catalog:
            if 'concrete' in material or 'rcc' in material:
                material_scores[material] += 1.0
                evidence_sources.append('type_heuristic')
        
        # Normalize and assign
        total_score = sum(material_scores.values())
        if total_score > 0:
            confidences = {m: score / total_score for m, score in material_scores.items()}
            best_material = max(material_scores, key=material_scores.get)
            confidence = confidences[best_material]
        else:
            best_material = _get_fallback_material(columns, 'concrete')
            confidence = 0.3
            evidence_sources.append('fallback')
        
        column['material'] = best_material
        column['material_confidence'] = confidence
        column['material_evidence'] = list(set(evidence_sources))
    
    return columns

def _learn_thickness_clusters(walls: List[Dict], material_catalog: List[str],
                              legend_dict: Dict) -> Dict[float, str]:
    """Learn thickness-to-material mapping using clustering"""
    if len(walls) < 3:
        return {}
    
    # Extract thicknesses
    thicknesses = [w.get('thickness', 0) for w in walls if w.get('thickness', 0) > 0]
    
    if len(thicknesses) < 3:
        return {}
    
    # Cluster thicknesses
    thickness_array = np.array(thicknesses).reshape(-1, 1)
    clustering = DBSCAN(eps=0.05, min_samples=2).fit(thickness_array)
    
    labels = clustering.labels_
    
    # Map clusters to materials (simplified - would use legend/layer info in real implementation)
    thickness_material_map = {}
    
    # For now, return empty - full implementation would analyze layer names per cluster
    return thickness_material_map

def _get_fallback_material(elements: List[Dict], default: str) -> str:
    """Get fallback material (most common or default)"""
    materials = [e.get('material') for e in elements if e.get('material')]
    
    if materials:
        counter = Counter(materials)
        return counter.most_common(1)[0][0]
    
    return default

def _compute_material_statistics(walls: List[Dict], slabs: List[Dict],
                                 columns: List[Dict]) -> Dict:
    """Compute material assignment statistics"""
    all_elements = walls + slabs + columns
    
    material_counts = Counter([e.get('material', 'unknown') for e in all_elements])
    
    avg_confidence = np.mean([e.get('material_confidence', 0) for e in all_elements]) if all_elements else 0
    
    evidence_sources = []
    for e in all_elements:
        evidence_sources.extend(e.get('material_evidence', []))
    
    evidence_counts = Counter(evidence_sources)
    
    return {
        'total_elements': len(all_elements),
        'material_distribution': dict(material_counts),
        'average_confidence': float(avg_confidence),
        'evidence_source_usage': dict(evidence_counts),
        'walls_with_material': sum(1 for w in walls if w.get('material')),
        'slabs_with_material': sum(1 for s in slabs if s.get('material')),
        'columns_with_material': sum(1 for c in columns if c.get('material'))
    }
