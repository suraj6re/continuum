"""Layer 4 Pipeline: Complete QTO Pipeline with Validation Metrics"""
from typing import Dict, List, Optional
from app.ai.layer4_validator import validate_node, validate_graph
from app.ai.layer4_normalizer import normalize_node
from app.ai.layer4_preprocessor import preprocess_node
from app.ai.layer4_measurement_engine import compute_element_measurements
from app.ai.layer4_reinforcement_engine import estimate_reinforcement
from app.ai.layer4_aggregation_engine import aggregate_materials
from app.ai.layer4_confidence_engine import propagate_confidence
from app.ai.layer4_metrics_engine import compute_validation_metrics

def run_layer4_step1(layer3_output: Dict, default_height: float = 3.0) -> Dict:
    """Run Layer 4 Step 1: Validate, normalize, and preprocess graph
    
    Args:
        layer3_output: Output from Layer 3 with elements and relationships
        default_height: Default height for walls/columns (meters)
    
    Returns:
        Cleaned and validated graph ready for QTO
    """
    # Step 1A: Validate graph structure
    validation_report = validate_graph(layer3_output)
    
    if not validation_report["valid"]:
        return {
            "success": False,
            "error": "Graph validation failed",
            "validation_report": validation_report,
            "elements": [],
            "relationships": []
        }
    
    # Extract elements
    elements = layer3_output.get("elements", [])
    relationships = layer3_output.get("relationships", [])
    
    # Process each element
    processed_elements = []
    errors = []
    
    for i, element in enumerate(elements):
        try:
            # Step 1A: Validate
            valid, error = validate_node(element)
            
            if not valid:
                errors.append({
                    "index": i,
                    "id": element.get("id", "unknown"),
                    "type": element.get("type", "unknown"),
                    "error": error
                })
                continue
            
            # Step 1B: Normalize
            element = normalize_node(element, default_height)
            
            # Step 1C: Preprocess
            element = preprocess_node(element)
            
            processed_elements.append(element)
            
        except Exception as e:
            errors.append({
                "index": i,
                "id": element.get("id", "unknown"),
                "type": element.get("type", "unknown"),
                "error": f"Processing error: {str(e)}"
            })
    
    # Compute statistics
    measurable_count = sum(1 for e in processed_elements if e.get("is_measurable", False))
    high_quality_count = sum(1 for e in processed_elements if e.get("quality_score", 0) >= 0.7)
    requires_review_count = sum(1 for e in processed_elements if e.get("requires_review", False))
    
    statistics = {
        "total_input": len(elements),
        "total_processed": len(processed_elements),
        "total_errors": len(errors),
        "measurable_elements": measurable_count,
        "high_quality_elements": high_quality_count,
        "requires_review": requires_review_count,
        "success_rate": len(processed_elements) / len(elements) if elements else 0
    }
    
    return {
        "success": True,
        "elements": processed_elements,
        "relationships": relationships,
        "errors": errors,
        "statistics": statistics,
        "validation_report": validation_report
    }

def get_measurable_elements(processed_output: Dict) -> List[Dict]:
    """Filter only measurable elements from processed output
    
    Args:
        processed_output: Output from run_layer4_step1
    
    Returns:
        List of measurable elements only
    """
    if not processed_output.get("success"):
        return []
    
    elements = processed_output.get("elements", [])
    return [e for e in elements if e.get("is_measurable", False)]

def get_elements_by_type(processed_output: Dict, element_type: str) -> List[Dict]:
    """Get all elements of a specific type
    
    Args:
        processed_output: Output from run_layer4_step1
        element_type: Type to filter (Wall, Slab, Column, Door, Window)
    
    Returns:
        List of elements of specified type
    """
    if not processed_output.get("success"):
        return []
    
    elements = processed_output.get("elements", [])
    return [e for e in elements if e.get("type") == element_type]

def run_layer4_step2(step1_output: Dict, include_secondary: bool = False) -> Dict:
    """Run Layer 4 Step 2: Element-Level Measurement Calculation
    
    Args:
        step1_output: Output from run_layer4_step1
        include_secondary: Include secondary measurements (plaster, paint)
    
    Returns:
        Measurement results
    """
    return compute_element_measurements(step1_output, include_secondary)

def run_layer4_stepB(step2_output: Dict, project_config: Optional[Dict] = None) -> Dict:
    """Run Layer 4 Step B: Reinforcement Estimation
    
    Args:
        step2_output: Output from run_layer4_step2
        project_config: Optional project-specific reinforcement ratios
    
    Returns:
        Reinforcement estimation results
    """
    return estimate_reinforcement(step2_output, project_config)

def run_layer4_stepC(step2_output: Dict, stepB_output: Optional[Dict] = None,
                     group_by_fields: Optional[List[str]] = None,
                     work_category_map: Optional[Dict] = None) -> Dict:
    """Run Layer 4 Step C: Material-Based Aggregation
    
    Args:
        step2_output: Output from run_layer4_step2
        stepB_output: Optional output from run_layer4_stepB
        group_by_fields: Fields to group by (default: ["material"])
        work_category_map: Optional work category mapping
    
    Returns:
        Aggregated quantities by material/group
    """
    return aggregate_materials(step2_output, stepB_output, group_by_fields, work_category_map)

def run_layer4_stepD(stepC_output: Dict, step2_output: Dict, 
                     stepB_output: Optional[Dict] = None) -> Dict:
    """Run Layer 4 Step D: Confidence Propagation
    
    Args:
        stepC_output: Output from run_layer4_stepC
        step2_output: Output from run_layer4_step2 (for element data)
        stepB_output: Optional output from run_layer4_stepB
    
    Returns:
        Aggregation with confidence scores
    """
    return propagate_confidence(stepC_output, step2_output, stepB_output)

def run_layer4_stepE(step2_output: Dict, stepB_output: Optional[Dict] = None) -> Dict:
    """Run Layer 4 Step E: Validation Metrics Computation
    
    Args:
        step2_output: Output from run_layer4_step2
        stepB_output: Optional output from run_layer4_stepB
    
    Returns:
        Validation metrics for Layer 5
    """
    return compute_validation_metrics(step2_output, stepB_output)

def run_layer4_pipeline(layer3_output: Dict, default_height: float = 3.0,
                        include_secondary: bool = False,
                        include_reinforcement: bool = True,
                        include_aggregation: bool = True,
                        include_confidence: bool = True,
                        include_validation_metrics: bool = True,
                        reinforcement_config: Optional[Dict] = None,
                        group_by_fields: Optional[List[str]] = None,
                        work_category_map: Optional[Dict] = None) -> Dict:
    """Run complete Layer 4 pipeline (All Steps)
    
    Args:
        layer3_output: Output from Layer 3
        default_height: Default height for walls/columns
        include_secondary: Include secondary measurements
        include_reinforcement: Include reinforcement estimation
        include_aggregation: Include material aggregation
        include_confidence: Include confidence propagation
        include_validation_metrics: Include validation metrics
        reinforcement_config: Optional project-specific reinforcement ratios
        group_by_fields: Fields to group by for aggregation
        work_category_map: Optional work category mapping
    
    Returns:
        Complete Layer 4 output with all steps
    """
    # Step 1: Validate and normalize
    step1_result = run_layer4_step1(layer3_output, default_height)
    
    if not step1_result["success"]:
        return step1_result
    
    # Step 2: Calculate measurements
    step2_result = run_layer4_step2(step1_result, include_secondary)
    
    if not step2_result["success"]:
        return {
            "success": False,
            "step1": step1_result,
            "step2": step2_result
        }
    
    # Step B: Reinforcement estimation (optional)
    stepB_result = None
    if include_reinforcement:
        stepB_result = run_layer4_stepB(step2_result, reinforcement_config)
    
    # Step C: Material aggregation (optional)
    stepC_result = None
    if include_aggregation:
        stepC_result = run_layer4_stepC(step2_result, stepB_result, 
                                        group_by_fields, work_category_map)
    
    # Step D: Confidence propagation (optional)
    stepD_result = None
    if include_confidence and stepC_result:
        stepD_result = run_layer4_stepD(stepC_result, step2_result, stepB_result)
    
    # Step E: Validation metrics (optional)
    stepE_result = None
    if include_validation_metrics:
        stepE_result = run_layer4_stepE(step2_result, stepB_result)
    
    # Use confidence-enhanced aggregation if available
    final_aggregation = stepD_result if stepD_result else stepC_result
    
    # Combine results
    return {
        "success": True,
        "step1": {
            "statistics": step1_result["statistics"],
            "errors": step1_result["errors"]
        },
        "step2": step2_result,
        "stepB": stepB_result,
        "stepC": stepC_result,
        "stepD": stepD_result,
        "stepE": stepE_result,
        "measurements": step2_result.get("element_measurements", []),
        "reinforcement": stepB_result.get("reinforcement_estimation", []) if stepB_result else [],
        "aggregation": final_aggregation.get("aggregation", {}) if final_aggregation else {},
        "validation_metrics": stepE_result.get("metrics", {}) if stepE_result else {},
        "statistics": {
            "measurements": step2_result.get("statistics", {}),
            "reinforcement": stepB_result.get("statistics", {}) if stepB_result else {},
            "aggregation": final_aggregation.get("summary", {}) if final_aggregation else {},
            "validation_metrics": stepE_result.get("summary", {}) if stepE_result else {}
        }
    }
