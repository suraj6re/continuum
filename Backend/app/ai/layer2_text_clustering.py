import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import DBSCAN
from typing import List, Dict, Tuple

def cluster_text_dbscan(text_entities: List[Dict]) -> Tuple[np.ndarray, Dict]:
    """Cluster text entities using DBSCAN with automatic eps selection
    
    Args:
        text_entities: List of text dicts with 'position' key
    
    Returns:
        Tuple of (labels, params) where labels are cluster IDs and params are used values
    """
    if len(text_entities) < 4:
        return np.array([-1] * len(text_entities)), {'eps': 0, 'min_samples': 4}
    
    # Extract coordinates
    text_coords = np.array([t['position'] for t in text_entities])
    
    # Step 2A: Choose k
    min_samples = 4
    k = min_samples - 1
    
    # Step 2B: Compute k-distance
    nbrs = NearestNeighbors(n_neighbors=k+1, algorithm='auto').fit(text_coords)
    distances, _ = nbrs.kneighbors(text_coords)
    k_distances = distances[:, k]
    
    # Step 2C: Find elbow
    k_distances_sorted = np.sort(k_distances)
    diffs = np.diff(k_distances_sorted)
    eps_index = np.argmax(diffs)
    eps = k_distances_sorted[eps_index]
    
    # Step 2D: Run DBSCAN
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(text_coords)
    
    return labels, {'eps': eps, 'min_samples': min_samples}
