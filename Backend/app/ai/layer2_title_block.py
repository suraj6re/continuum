import numpy as np
from typing import List, Dict, Tuple, Optional
import re

# Title block keywords
TITLE_BLOCK_KEYWORDS = [
    'title', 'drawing', 'project', 'scale', 'date', 'drawn', 'checked',
    'approved', 'sheet', 'revision', 'dwg', 'no', 'number', 'client',
    'architect', 'engineer', 'designer'
]

# Scale pattern regex
SCALE_PATTERN = re.compile(
    r"(?:scale\W*)?(\d+)\s*[:/]\s*(\d+)",
    flags=re.IGNORECASE
)

def identify_title_block(text_entities: List[Dict], labels: np.ndarray) -> Optional[Dict]:
    """Identify title block cluster from DBSCAN results
    
    Args:
        text_entities: List of text dicts with 'text' and 'position'
        labels: Cluster labels from DBSCAN
    
    Returns:
        Dict with title_block info or None
    """
    if len(text_entities) == 0:
        return None
    
    # Get unique cluster IDs (exclude noise -1)
    unique_labels = set(labels.tolist())
    cluster_ids = [l for l in unique_labels if l != -1]
    
    if len(cluster_ids) == 0:
        return None
    
    # Score each cluster
    cluster_scores = []
    for cluster_id in cluster_ids:
        cluster_indices = np.where(labels == cluster_id)[0]
        cluster_texts = [text_entities[i] for i in cluster_indices]
        
        score = _score_cluster_for_title_block(cluster_texts)
        cluster_scores.append({
            'cluster_id': int(cluster_id),
            'score': score,
            'text_count': len(cluster_texts),
            'texts': cluster_texts,
            'indices': [int(i) for i in cluster_indices]
        })
    
    # Sort by score
    cluster_scores.sort(key=lambda x: x['score'], reverse=True)
    
    # Best cluster is likely title block
    if cluster_scores[0]['score'] > 0:
        best_cluster = cluster_scores[0]
        
        # Extract metadata
        metadata = extract_metadata(best_cluster['texts'])
        
        # Extract scale
        scale_info = extract_scale(best_cluster['texts'])
        
        # Compute bounding box
        positions = [t['position'] for t in best_cluster['texts']]
        bbox = _compute_bbox(positions)
        
        return {
            'cluster_id': best_cluster['cluster_id'],
            'score': best_cluster['score'],
            'text_count': best_cluster['text_count'],
            'bounding_box': bbox,
            'metadata': metadata,
            'scale_info': scale_info,
            'all_clusters': cluster_scores
        }
    
    return None

def _score_cluster_for_title_block(texts: List[Dict]) -> int:
    """Score a cluster based on title block keywords
    
    Args:
        texts: List of text dicts
    
    Returns:
        Score (higher = more likely title block)
    """
    score = 0
    
    for text_dict in texts:
        text = text_dict.get('text', '').lower()
        
        # Check for keywords
        for keyword in TITLE_BLOCK_KEYWORDS:
            if keyword in text:
                score += 1
        
        # Bonus for common patterns
        if re.search(r'scale\s*[:=]?\s*1\s*[:\/]\s*\d+', text, re.IGNORECASE):
            score += 2
        if re.search(r'sheet\s*[:=]?\s*\d+', text, re.IGNORECASE):
            score += 2
        if re.search(r'date\s*[:=]?\s*\d', text, re.IGNORECASE):
            score += 2
        if re.search(r'dwg\s*[:=]?\s*no', text, re.IGNORECASE):
            score += 2
    
    return score

def extract_metadata(texts: List[Dict]) -> Dict[str, str]:
    """Extract key-value pairs from title block texts
    
    Args:
        texts: List of text dicts from title block cluster
    
    Returns:
        Dict of extracted metadata
    """
    metadata = {}
    
    for text_dict in texts:
        text = text_dict.get('text', '').strip()
        
        # Try to extract key-value pairs
        # Pattern: "Key: Value" or "Key = Value"
        match = re.match(r'^([^:=]+)\s*[:=]\s*(.+)$', text)
        if match:
            key = match.group(1).strip().lower()
            value = match.group(2).strip()
            metadata[key] = value
        else:
            # Store as raw text with index
            metadata[f'text_{len(metadata)}'] = text
    
    return metadata

def extract_scale(texts: List[Dict]) -> Dict:
    """Extract scale information from title block texts
    
    Args:
        texts: List of text dicts from title block cluster
    
    Returns:
        Dict with scale info or needs_manual_override flag
    """
    for text_dict in texts:
        text = text_dict.get('text', '').strip()
        
        # Search for scale pattern
        match = SCALE_PATTERN.search(text)
        if match:
            numerator = int(match.group(1))
            denominator = int(match.group(2))
            
            return {
                'type': 'ratio',
                'numerator': numerator,
                'denominator': denominator,
                'ratio': numerator / denominator,
                'raw_text': text,
                'status': 'found'
            }
    
    # No scale found
    return {
        'status': 'missing_scale',
        'needs_manual_override': True
    }

def _compute_bbox(positions: List[List[float]]) -> Dict:
    """Compute bounding box from positions
    
    Args:
        positions: List of [x, y] coordinates
    
    Returns:
        Dict with min_x, min_y, max_x, max_y
    """
    if not positions:
        return {'min_x': 0, 'min_y': 0, 'max_x': 0, 'max_y': 0}
    
    xs = [p[0] for p in positions]
    ys = [p[1] for p in positions]
    
    return {
        'min_x': min(xs),
        'min_y': min(ys),
        'max_x': max(xs),
        'max_y': max(ys)
    }
