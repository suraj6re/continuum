"""Layer 4 Step 1C: QTO Eligibility Preprocessing"""
from typing import Dict

# Confidence thresholds
MIN_CONFIDENCE_THRESHOLD = 0.4  # Below this, element is not measurable
GOOD_CONFIDENCE_THRESHOLD = 0.7  # Above this, high quality measurement

def mark_measurable(node: Dict, min_confidence: float = MIN_CONFIDENCE_THRESHOLD) -> Dict:
    """Mark if element is eligible for quantity takeoff
    
    Args:
        node: Element node
        min_confidence: Minimum confidence threshold
    
    Returns:
        Node with measurability flags
    """
    confidence = node.get("confidence", 0.5)
    
    # Determine if measurable
    if confidence < min_confidence:
        node["is_measurable"] = False
        node["measurement_basis"] = "rejected_low_confidence"
    else:
        node["is_measurable"] = True
        
        # Determine measurement basis
        if confidence >= GOOD_CONFIDENCE_THRESHOLD:
            node["measurement_basis"] = "geometry_high_confidence"
        else:
            node["measurement_basis"] = "geometry_medium_confidence"
    
    return node

def compute_quality_score(node: Dict) -> float:
    """Compute overall quality score for measurement
    
    Args:
        node: Element node
    
    Returns:
        Quality score (0-1)
    """
    confidence = node.get("confidence", 0.5)
    
    # Check if dimensions are from defaults
    has_defaults = any(
        node.get(f"{field}_source") == "default" 
        for field in ["height", "width", "thickness", "area"]
    )
    
    # Penalize if using defaults
    if has_defaults:
        quality = confidence * 0.8
    else:
        quality = confidence
    
    return quality

def add_metadata(node: Dict) -> Dict:
    """Add preprocessing metadata to node
    
    Args:
        node: Element node
    
    Returns:
        Node with metadata
    """
    node = mark_measurable(node)
    node["quality_score"] = compute_quality_score(node)
    
    # Add flags for QTO processing
    node["requires_review"] = node["confidence"] < GOOD_CONFIDENCE_THRESHOLD
    node["has_defaults"] = any(
        node.get(f"{field}_source") == "default" 
        for field in ["height", "width", "thickness", "area", "material"]
    )
    
    return node

def preprocess_node(node: Dict) -> Dict:
    """Apply all preprocessing to a node
    
    Args:
        node: Element node
    
    Returns:
        Preprocessed node ready for QTO
    """
    return add_metadata(node)
