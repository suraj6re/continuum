from typing import Dict, Optional, List

class ElementViewer:
    """
    Read-only element inspection API for Human-in-the-Loop review.
    
    Provides transparent visibility into:
    - Extracted dimensions
    - QTO formulas
    - Confidence scores
    - Source traceability
    - Manual override status
    
    No modifications, no recalculations - pure retrieval.
    """
    
    def __init__(self, element_graph: Dict):
        """
        Initialize viewer with element graph from previous layers
        
        Args:
            element_graph: Structured element data from Layer 3-6
        """
        self.element_graph = element_graph
    
    def get_element_details(self, element_id: str) -> Dict:
        """
        Returns complete structured details of an element for review
        
        Args:
            element_id: Unique identifier (e.g., "W12", "S5", "C3")
        
        Returns:
            Dictionary with all element details or error
        """
        if element_id not in self.element_graph:
            return {
                "error": "Element not found",
                "element_id": element_id,
                "available_elements": list(self.element_graph.keys())[:10]
            }
        
        element = self.element_graph[element_id]
        
        return {
            "element_id": element_id,
            "element_type": element.get("type"),
            "dimensions": element.get("dimensions", {}),
            "material": element.get("material"),
            "quantity": element.get("quantity", {}),
            "confidence": element.get("confidence"),
            "source": element.get("source"),
            "manual_override": element.get("manual_override", False),
            "metadata": {
                "layer": element.get("layer"),
                "level": element.get("level"),
                "drawing_reference": element.get("drawing_reference")
            }
        }
    
    def get_elements_by_type(self, element_type: str) -> List[Dict]:
        """
        Get all elements of a specific type
        
        Args:
            element_type: Type filter (e.g., "Wall", "Slab", "Column")
        
        Returns:
            List of element summaries
        """
        results = []
        for elem_id, elem_data in self.element_graph.items():
            if elem_data.get("type") == element_type:
                results.append({
                    "element_id": elem_id,
                    "element_type": element_type,
                    "confidence": elem_data.get("confidence"),
                    "manual_override": elem_data.get("manual_override", False)
                })
        return results
    
    def get_low_confidence_elements(self, threshold: float = 0.7) -> List[Dict]:
        """
        Get elements below confidence threshold for review priority
        
        Args:
            threshold: Confidence threshold (default: 0.7)
        
        Returns:
            List of low-confidence elements
        """
        results = []
        for elem_id, elem_data in self.element_graph.items():
            confidence = elem_data.get("confidence", 1.0)
            if confidence < threshold:
                results.append({
                    "element_id": elem_id,
                    "element_type": elem_data.get("type"),
                    "confidence": confidence,
                    "requires_review": True
                })
        return sorted(results, key=lambda x: x["confidence"])
    
    def get_element_formula(self, element_id: str) -> Dict:
        """
        Get detailed formula breakdown for an element
        
        Args:
            element_id: Element identifier
        
        Returns:
            Formula details with calculation steps
        """
        if element_id not in self.element_graph:
            return {"error": "Element not found"}
        
        element = self.element_graph[element_id]
        quantity = element.get("quantity", {})
        dimensions = element.get("dimensions", {})
        
        return {
            "element_id": element_id,
            "formula": quantity.get("formula", "N/A"),
            "calculation": quantity.get("calculation", "N/A"),
            "result": quantity.get("volume") or quantity.get("area") or quantity.get("length"),
            "unit": quantity.get("unit", "N/A"),
            "dimensions_used": dimensions,
            "explainable": True
        }
    
    def get_all_elements_summary(self) -> Dict:
        """
        Get summary statistics of all elements
        
        Returns:
            Summary with counts and statistics
        """
        total = len(self.element_graph)
        by_type = {}
        low_confidence = 0
        manual_overrides = 0
        
        for elem_data in self.element_graph.values():
            elem_type = elem_data.get("type", "Unknown")
            by_type[elem_type] = by_type.get(elem_type, 0) + 1
            
            if elem_data.get("confidence", 1.0) < 0.7:
                low_confidence += 1
            
            if elem_data.get("manual_override", False):
                manual_overrides += 1
        
        return {
            "total_elements": total,
            "by_type": by_type,
            "low_confidence_count": low_confidence,
            "manual_overrides_count": manual_overrides,
            "review_required": low_confidence > 0
        }
    
    def search_elements(self, query: Dict) -> List[Dict]:
        """
        Search elements by multiple criteria
        
        Args:
            query: Search criteria (type, material, confidence_min, etc.)
        
        Returns:
            List of matching elements
        """
        results = []
        
        for elem_id, elem_data in self.element_graph.items():
            match = True
            
            if "type" in query and elem_data.get("type") != query["type"]:
                match = False
            
            if "material" in query and elem_data.get("material") != query["material"]:
                match = False
            
            if "confidence_min" in query:
                if elem_data.get("confidence", 0) < query["confidence_min"]:
                    match = False
            
            if "manual_override" in query:
                if elem_data.get("manual_override", False) != query["manual_override"]:
                    match = False
            
            if match:
                results.append({
                    "element_id": elem_id,
                    "element_type": elem_data.get("type"),
                    "material": elem_data.get("material"),
                    "confidence": elem_data.get("confidence")
                })
        
        return results
