import numpy as np
import networkx as nx
from sklearn.ensemble import IsolationForest
from typing import List, Dict, Tuple
from collections import Counter

def compute_confidence_scores(walls: List[Dict], slabs: List[Dict], columns: List[Dict],
                              doors: List[Dict], windows: List[Dict],
                              graph: nx.Graph, dimensions: List[Dict]) -> Dict:
    """Compute confidence scores using adaptive weighting and calibration
    
    Args:
        walls: Walls with materials
        slabs: Slabs with materials
        columns: Columns with materials
        doors: Detected doors
        windows: Detected windows
        graph: Relationship graph
        dimensions: Parsed dimensions
    
    Returns:
        Dict with confidence scores and flagged elements
    """
    all_elements = walls + slabs + columns + doors + windows
    
    if not all_elements:
        return {
            'element_confidence': {},
            'flagged_elements': [],
            'statistics': {
                'total_elements': 0,
                'average_confidence': 0,
                'flagged_count': 0
            }
        }
    
    # Step 9.1: Compute feature scores for each element
    element_features = _compute_element_features(all_elements, graph, dimensions)
    
    # Step 9.2: Learn feature importance (adaptive weighting)
    feature_weights = _learn_feature_weights(element_features)
    
    # Step 9.3: Compute raw confidence scores
    element_confidence = _compute_raw_confidence(element_features, feature_weights)
    
    # Step 9.4: Calibrate confidence distribution
    review_threshold = _calibrate_threshold(element_confidence)
    
    # Step 9.5: Detect anomalies
    anomalies = _detect_anomalies(element_features, all_elements)
    
    # Step 9.6: Apply graph smoothing
    if graph:
        element_confidence = _apply_graph_smoothing(element_confidence, graph, iterations=2)
    
    # Step 9.7: Flag elements for review
    flagged_elements = _flag_elements_for_review(element_confidence, review_threshold, anomalies)
    
    # Step 9.8: Compute statistics
    statistics = _compute_confidence_statistics(element_confidence, flagged_elements)
    
    return {
        'element_confidence': element_confidence,
        'flagged_elements': flagged_elements,
        'review_threshold': review_threshold,
        'feature_weights': feature_weights,
        'statistics': statistics
    }

def _compute_element_features(elements: List[Dict], graph: nx.Graph,
                              dimensions: List[Dict]) -> Dict[str, Dict]:
    """Compute feature scores for each element"""
    features = {}
    
    for element in elements:
        element_id = element['id']
        element_type = element.get('type', 'unknown')
        
        # Feature 1: Geometry clarity
        geometry_score = _compute_geometry_score(element, element_type)
        
        # Feature 2: Text linkage (for doors/windows)
        text_score = _compute_text_linkage_score(element, element_type)
        
        # Feature 3: Material confidence
        material_score = element.get('material_confidence', 0.5)
        
        # Feature 4: Topology consistency
        topology_score = _compute_topology_score(element, graph)
        
        features[element_id] = {
            'geometry': geometry_score,
            'text_linkage': text_score,
            'material': material_score,
            'topology': topology_score
        }
    
    return features

def _compute_geometry_score(element: Dict, element_type: str) -> float:
    """Compute geometry clarity score"""
    
    # For walls: based on pairing confidence
    if element_type == 'wall':
        # If wall has thickness close to learned value, high score
        thickness = element.get('thickness', 0)
        if thickness > 0:
            return 0.9  # Paired walls have high geometry confidence
        return 0.5
    
    # For columns: based on shape regularity
    elif element_type == 'column':
        rectangularity = element.get('rectangularity', 0)
        compactness = element.get('compactness', 0)
        return max(rectangularity, compactness)
    
    # For slabs: based on compactness
    elif element_type == 'slab':
        compactness = element.get('compactness', 0)
        return max(compactness, 0.7)
    
    # For doors/windows: based on attachment
    elif element_type in ['door', 'window']:
        # If has linked wall, high score
        if element.get('linked_wall'):
            return 0.85
        return 0.4
    
    return 0.5

def _compute_text_linkage_score(element: Dict, element_type: str) -> float:
    """Compute text linkage success score"""
    
    if element_type in ['door', 'window']:
        # Check if has schedule data
        if element.get('schedule_data'):
            return 0.9
        # Check if has code
        elif element.get('code'):
            return 0.6
        return 0.3
    
    # Other elements don't rely on text linkage
    return 0.5

def _compute_topology_score(element: Dict, graph: nx.Graph) -> float:
    """Compute topology consistency score"""
    
    if not graph or element['id'] not in graph:
        return 0.5
    
    # Check degree (number of connections)
    degree = graph.degree(element['id'])
    
    # Check if in main connected component
    if nx.is_connected(graph):
        in_main_component = True
    else:
        components = list(nx.connected_components(graph))
        largest_component = max(components, key=len)
        in_main_component = element['id'] in largest_component
    
    # Compute score
    score = 0.5
    
    if degree > 0:
        score += 0.2
    
    if in_main_component:
        score += 0.3
    
    return min(score, 1.0)

def _learn_feature_weights(element_features: Dict[str, Dict]) -> Dict[str, float]:
    """Learn feature importance using variance-based weighting"""
    
    if not element_features:
        return {'geometry': 0.4, 'text_linkage': 0.3, 'material': 0.2, 'topology': 0.1}
    
    # Extract feature values
    feature_names = ['geometry', 'text_linkage', 'material', 'topology']
    feature_values = {name: [] for name in feature_names}
    
    for features in element_features.values():
        for name in feature_names:
            feature_values[name].append(features.get(name, 0.5))
    
    # Compute variance for each feature
    variances = {}
    for name in feature_names:
        values = feature_values[name]
        if len(values) > 1:
            variances[name] = np.var(values)
        else:
            variances[name] = 0.1
    
    # Normalize to get weights
    total_variance = sum(variances.values())
    
    if total_variance > 0:
        weights = {name: var / total_variance for name, var in variances.items()}
    else:
        # Fallback to equal weights
        weights = {name: 1.0 / len(feature_names) for name in feature_names}
    
    return weights

def _compute_raw_confidence(element_features: Dict[str, Dict],
                            feature_weights: Dict[str, float]) -> Dict[str, Dict]:
    """Compute raw confidence scores"""
    
    confidence = {}
    
    for element_id, features in element_features.items():
        # Weighted sum
        overall = sum(features.get(name, 0.5) * weight 
                     for name, weight in feature_weights.items())
        
        confidence[element_id] = {
            'overall': overall,
            'geometry': features.get('geometry', 0.5),
            'text_linkage': features.get('text_linkage', 0.5),
            'material': features.get('material', 0.5),
            'topology': features.get('topology', 0.5)
        }
    
    return confidence

def _calibrate_threshold(element_confidence: Dict[str, Dict]) -> float:
    """Calibrate review threshold based on distribution"""
    
    if not element_confidence:
        return 0.6
    
    overall_scores = [conf['overall'] for conf in element_confidence.values()]
    
    mean_conf = np.mean(overall_scores)
    std_conf = np.std(overall_scores)
    
    # Threshold = mean - 1 standard deviation
    threshold = mean_conf - std_conf
    
    # Clamp to reasonable range
    return max(0.3, min(threshold, 0.7))

def _detect_anomalies(element_features: Dict[str, Dict],
                     elements: List[Dict]) -> List[str]:
    """Detect anomalous elements using IsolationForest"""
    
    if len(element_features) < 5:
        return []
    
    # Build feature matrix
    feature_names = ['geometry', 'text_linkage', 'material', 'topology']
    feature_matrix = []
    element_ids = []
    
    for element_id, features in element_features.items():
        feature_vector = [features.get(name, 0.5) for name in feature_names]
        feature_matrix.append(feature_vector)
        element_ids.append(element_id)
    
    feature_matrix = np.array(feature_matrix)
    
    # Detect anomalies
    try:
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        predictions = iso_forest.fit_predict(feature_matrix)
        
        # -1 indicates anomaly
        anomalies = [element_ids[i] for i, pred in enumerate(predictions) if pred == -1]
        return anomalies
    except:
        return []

def _apply_graph_smoothing(element_confidence: Dict[str, Dict],
                           graph: nx.Graph, iterations: int = 2) -> Dict[str, Dict]:
    """Apply graph-based confidence smoothing"""
    
    if not graph:
        return element_confidence
    
    for _ in range(iterations):
        new_confidence = {}
        
        for node_id in element_confidence:
            if node_id not in graph:
                new_confidence[node_id] = element_confidence[node_id]
                continue
            
            # Get neighbor confidences
            neighbors = list(graph.neighbors(node_id))
            neighbor_confs = [element_confidence[n]['overall'] 
                            for n in neighbors if n in element_confidence]
            
            if neighbor_confs:
                neighbor_avg = np.mean(neighbor_confs)
                # Smooth: 80% self, 20% neighbors
                smoothed = 0.8 * element_confidence[node_id]['overall'] + 0.2 * neighbor_avg
            else:
                smoothed = element_confidence[node_id]['overall']
            
            new_confidence[node_id] = {
                **element_confidence[node_id],
                'overall': smoothed
            }
        
        element_confidence = new_confidence
    
    return element_confidence

def _flag_elements_for_review(element_confidence: Dict[str, Dict],
                              threshold: float, anomalies: List[str]) -> List[Dict]:
    """Flag elements that need review"""
    
    flagged = []
    
    for element_id, conf in element_confidence.items():
        reasons = []
        needs_review = False
        
        # Check overall confidence
        if conf['overall'] < threshold:
            reasons.append('low_overall_confidence')
            needs_review = True
        
        # Check individual features
        if conf['geometry'] < 0.5:
            reasons.append('low_geometry_score')
            needs_review = True
        
        if conf['topology'] < 0.4:
            reasons.append('weak_topology')
            needs_review = True
        
        # Check if anomaly
        if element_id in anomalies:
            reasons.append('detected_anomaly')
            needs_review = True
        
        if needs_review:
            flagged.append({
                'element_id': element_id,
                'confidence': conf['overall'],
                'reasons': reasons
            })
    
    return flagged

def _compute_confidence_statistics(element_confidence: Dict[str, Dict],
                                   flagged_elements: List[Dict]) -> Dict:
    """Compute confidence statistics"""
    
    if not element_confidence:
        return {
            'total_elements': 0,
            'average_confidence': 0,
            'min_confidence': 0,
            'max_confidence': 0,
            'flagged_count': 0,
            'flagged_percentage': 0
        }
    
    overall_scores = [conf['overall'] for conf in element_confidence.values()]
    
    return {
        'total_elements': len(element_confidence),
        'average_confidence': float(np.mean(overall_scores)),
        'min_confidence': float(np.min(overall_scores)),
        'max_confidence': float(np.max(overall_scores)),
        'std_confidence': float(np.std(overall_scores)),
        'flagged_count': len(flagged_elements),
        'flagged_percentage': len(flagged_elements) / len(element_confidence) * 100 if element_confidence else 0
    }
