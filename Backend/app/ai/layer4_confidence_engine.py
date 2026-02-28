"""Layer 4 Step D2: Confidence Propagation Engine"""
from typing import Dict, List, Optional
from app.ai.layer4_confidence_weight_resolver import resolve_primary_metric

def propagate_confidence(aggregation_result: Dict, 
                        measurement_output: Dict,
                        reinforcement_output: Optional[Dict] = None) -> Dict:
    """Propagate element-level confidence to aggregated items using weighted average
    
    Formula: weighted_confidence = Σ(ci × qi) / Σ(qi)
    Where:
        ci = element confidence
        qi = element contribution quantity
    
    Args:
        aggregation_result: Output from Layer 4 Step C
        measurement_output: Output from Layer 4 Step 2 (for element data)
        reinforcement_output: Optional output from Layer 4 Step B
    
    Returns:
        Aggregation with confidence scores added
    """
    if not aggregation_result.get("success"):
        return aggregation_result
    
    # Build element lookup
    element_lookup = _build_element_lookup(measurement_output, reinforcement_output)
    
    # Process each aggregated group
    aggregation = aggregation_result.get("aggregation", {})
    result_with_confidence = {}
    
    for group_key, aggregated_item in aggregation.items():
        # Get elements in this group
        element_ids = aggregated_item.get("element_ids", [])
        
        if not element_ids:
            aggregated_item["confidence"] = None
            aggregated_item["confidence_trace"] = {
                "method": "no_elements",
                "element_count": 0
            }
            result_with_confidence[group_key] = aggregated_item
            continue
        
        # Resolve primary metric for weighting
        primary_metric = resolve_primary_metric(aggregated_item)
        
        if not primary_metric:
            aggregated_item["confidence"] = None
            aggregated_item["confidence_trace"] = {
                "method": "no_valid_metric",
                "element_count": len(element_ids)
            }
            result_with_confidence[group_key] = aggregated_item
            continue
        
        # Compute weighted confidence
        weighted_sum = 0.0
        total_weight = 0.0
        valid_elements = 0
        
        for element_id in element_ids:
            element_data = element_lookup.get(element_id)
            
            if not element_data:
                continue
            
            # Get element confidence
            element_conf = element_data.get("confidence")
            if element_conf is None:
                continue
            
            # Get element contribution for primary metric
            contribution = element_data.get("quantities", {}).get(primary_metric, 0)
            
            if contribution <= 0:
                continue
            
            # Add to weighted sum
            weighted_sum += element_conf * contribution
            total_weight += contribution
            valid_elements += 1
        
        # Calculate final confidence
        if total_weight > 0:
            final_confidence = weighted_sum / total_weight
        else:
            final_confidence = None
        
        # Add confidence and trace
        aggregated_item["confidence"] = round(final_confidence, 4) if final_confidence is not None else None
        aggregated_item["confidence_trace"] = {
            "method": "weighted_average",
            "metric_used": primary_metric,
            "element_count": len(element_ids),
            "valid_elements": valid_elements,
            "total_weight": round(total_weight, 4)
        }
        
        result_with_confidence[group_key] = aggregated_item
    
    # Update result
    updated_result = aggregation_result.copy()
    updated_result["aggregation"] = result_with_confidence
    
    # Update summary with confidence stats
    confidence_stats = _compute_confidence_statistics(result_with_confidence)
    updated_result["summary"]["confidence"] = confidence_stats
    
    return updated_result

def _build_element_lookup(measurement_output: Dict, 
                         reinforcement_output: Optional[Dict]) -> Dict:
    """Build lookup table for element data
    
    Args:
        measurement_output: Measurement results
        reinforcement_output: Optional reinforcement results
    
    Returns:
        Dict mapping element_id to element data
    """
    lookup = {}
    
    # Add measurement data
    for element in measurement_output.get("element_measurements", []):
        element_id = element.get("element_id")
        if element_id:
            lookup[element_id] = {
                "confidence": element.get("confidence"),
                "quality_score": element.get("quality_score"),
                "quantities": element.get("measurements", {}).copy()
            }
    
    # Add reinforcement data
    if reinforcement_output and reinforcement_output.get("success"):
        for element in reinforcement_output.get("reinforcement_estimation", []):
            element_id = element.get("element_id")
            if element_id and element_id in lookup:
                # Add steel_kg to quantities
                steel_kg = element.get("reinforcement", {}).get("steel_kg", 0)
                lookup[element_id]["quantities"]["steel_kg"] = steel_kg
    
    return lookup

def _compute_confidence_statistics(aggregation_with_confidence: Dict) -> Dict:
    """Compute confidence statistics across all groups
    
    Args:
        aggregation_with_confidence: Aggregation with confidence scores
    
    Returns:
        Confidence statistics
    """
    confidences = []
    methods_used = {}
    metrics_used = {}
    
    for group_data in aggregation_with_confidence.values():
        conf = group_data.get("confidence")
        if conf is not None:
            confidences.append(conf)
        
        trace = group_data.get("confidence_trace", {})
        method = trace.get("method", "unknown")
        metric = trace.get("metric_used", "unknown")
        
        methods_used[method] = methods_used.get(method, 0) + 1
        if metric != "unknown":
            metrics_used[metric] = metrics_used.get(metric, 0) + 1
    
    if confidences:
        avg_confidence = sum(confidences) / len(confidences)
        min_confidence = min(confidences)
        max_confidence = max(confidences)
    else:
        avg_confidence = None
        min_confidence = None
        max_confidence = None
    
    return {
        "average_confidence": round(avg_confidence, 4) if avg_confidence is not None else None,
        "min_confidence": round(min_confidence, 4) if min_confidence is not None else None,
        "max_confidence": round(max_confidence, 4) if max_confidence is not None else None,
        "groups_with_confidence": len(confidences),
        "methods_used": methods_used,
        "metrics_used": metrics_used
    }

def get_low_confidence_groups(aggregation_result: Dict, threshold: float = 0.6) -> List[Dict]:
    """Get groups with confidence below threshold
    
    Args:
        aggregation_result: Aggregation with confidence
        threshold: Confidence threshold
    
    Returns:
        List of low confidence groups
    """
    low_confidence = []
    
    aggregation = aggregation_result.get("aggregation", {})
    
    for group_key, data in aggregation.items():
        conf = data.get("confidence")
        if conf is not None and conf < threshold:
            low_confidence.append({
                "group_key": group_key,
                "confidence": conf,
                "element_count": data.get("element_count", 0),
                "quantities": data.get("quantities", {})
            })
    
    return low_confidence

def get_confidence_by_work_category(aggregation_result: Dict) -> Dict:
    """Get average confidence by work category
    
    Args:
        aggregation_result: Aggregation with confidence
    
    Returns:
        Dict mapping work category to average confidence
    """
    category_confidences = {}
    
    aggregation = aggregation_result.get("aggregation", {})
    
    for data in aggregation.values():
        category = data.get("work_category", "Uncategorized")
        conf = data.get("confidence")
        
        if conf is not None:
            if category not in category_confidences:
                category_confidences[category] = []
            category_confidences[category].append(conf)
    
    # Compute averages
    return {
        category: round(sum(confs) / len(confs), 4)
        for category, confs in category_confidences.items()
    }
