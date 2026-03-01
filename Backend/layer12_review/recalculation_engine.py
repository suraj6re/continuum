from typing import Dict, List, Optional
from datetime import datetime

try:
    from approval_engine import ApprovalEngine
except ImportError:
    ApprovalEngine = None

class QTOEngine:
    """
    Quantity Take-Off recalculation engine
    Recalculates volumes/areas based on updated dimensions
    """
    
    def __init__(self, element_graph: Dict):
        self.element_graph = element_graph
    
    def recalculate(self, element_ids: List[str]) -> Dict:
        """
        Recalculate quantities for modified elements
        
        Args:
            element_ids: List of element IDs to recalculate
        
        Returns:
            Summary of recalculations
        """
        updated = []
        
        for eid in element_ids:
            if eid not in self.element_graph:
                continue
            
            element = self.element_graph[eid]
            dims = element.get("dimensions", {})
            elem_type = element.get("type")
            
            old_quantity = element.get("quantity", {}).get("volume") or element.get("quantity", {}).get("area")
            
            # Calculate based on element type
            if elem_type == "Wall":
                volume = dims.get("length", 0) * dims.get("thickness", 0) * dims.get("height", 0)
                element.setdefault("quantity", {})["volume"] = round(volume, 3)
                element["quantity"]["unit"] = "m3"
                
            elif elem_type == "Slab":
                volume = dims.get("length", 0) * dims.get("width", 0) * dims.get("thickness", 0)
                element.setdefault("quantity", {})["volume"] = round(volume, 3)
                element["quantity"]["unit"] = "m3"
                
            elif elem_type == "Column":
                volume = dims.get("width", 0) * dims.get("depth", 0) * dims.get("height", 0)
                element.setdefault("quantity", {})["volume"] = round(volume, 3)
                element["quantity"]["unit"] = "m3"
                
            elif elem_type == "Beam":
                volume = dims.get("length", 0) * dims.get("width", 0) * dims.get("depth", 0)
                element.setdefault("quantity", {})["volume"] = round(volume, 3)
                element["quantity"]["unit"] = "m3"
            
            new_quantity = element.get("quantity", {}).get("volume") or element.get("quantity", {}).get("area")
            
            updated.append({
                "element_id": eid,
                "element_type": elem_type,
                "old_quantity": old_quantity,
                "new_quantity": new_quantity
            })
        
        return {
            "engine": "QTO",
            "updated_count": len(updated),
            "updates": updated
        }


class CostEngine:
    """
    Cost recalculation engine
    Recalculates costs based on updated quantities and rates
    """
    
    def __init__(self, element_graph: Dict, rate_table: Optional[Dict] = None):
        self.element_graph = element_graph
        self.rate_table = rate_table or {}
    
    def recalculate(self, element_ids: List[str]) -> Dict:
        """
        Recalculate costs for modified elements
        
        Args:
            element_ids: List of element IDs to recalculate
        
        Returns:
            Summary of recalculations
        """
        updated = []
        
        for eid in element_ids:
            if eid not in self.element_graph:
                continue
            
            element = self.element_graph[eid]
            material = element.get("material", "Unknown")
            quantity = element.get("quantity", {})
            volume = quantity.get("volume", 0)
            
            # Get rate from table or use default
            rate = self.rate_table.get(material, 0)
            
            old_cost = element.get("cost", 0)
            new_cost = round(volume * rate, 2)
            
            element["cost"] = new_cost
            element["cost_unit"] = "Rs"
            element["rate_applied"] = rate
            
            updated.append({
                "element_id": eid,
                "material": material,
                "quantity": volume,
                "rate": rate,
                "old_cost": old_cost,
                "new_cost": new_cost
            })
        
        return {
            "engine": "Cost",
            "updated_count": len(updated),
            "updates": updated
        }


class ScheduleEngine:
    """
    Schedule recalculation engine
    Recalculates durations based on updated quantities and productivity
    """
    
    def __init__(self, element_graph: Dict, productivity_table: Optional[Dict] = None):
        self.element_graph = element_graph
        self.productivity_table = productivity_table or {}
    
    def recalculate(self, element_ids: List[str]) -> Dict:
        """
        Recalculate schedule durations for modified elements
        
        Args:
            element_ids: List of element IDs to recalculate
        
        Returns:
            Summary of recalculations
        """
        updated = []
        
        for eid in element_ids:
            if eid not in self.element_graph:
                continue
            
            element = self.element_graph[eid]
            elem_type = element.get("type")
            quantity = element.get("quantity", {})
            volume = quantity.get("volume", 0)
            
            # Get productivity from table or use default
            productivity = self.productivity_table.get(elem_type, 5)  # Default: 5 m³/day
            
            old_duration = element.get("schedule_days", 0)
            new_duration = round(volume / productivity, 2) if productivity > 0 else 0
            
            element["schedule_days"] = new_duration
            element["productivity_applied"] = productivity
            
            updated.append({
                "element_id": eid,
                "element_type": elem_type,
                "quantity": volume,
                "productivity": productivity,
                "old_duration": old_duration,
                "new_duration": new_duration
            })
        
        return {
            "engine": "Schedule",
            "updated_count": len(updated),
            "updates": updated
        }


class RecalculationEngine:
    """
    Orchestrates controlled cascade recalculation
    
    Core principle: User-triggered, not automatic
    
    Flow:
    1. Identify modified elements
    2. Recalculate QTO
    3. Recalculate Cost
    4. Recalculate Schedule
    5. Mark QTO items as "Pending" (requires re-approval)
    6. Clear recalculation flags
    """
    
    def __init__(
        self,
        element_graph: Dict,
        qto_engine: Optional[QTOEngine] = None,
        cost_engine: Optional[CostEngine] = None,
        schedule_engine: Optional[ScheduleEngine] = None,
        approval_engine: Optional['ApprovalEngine'] = None
    ):
        """
        Initialize recalculation orchestrator
        
        Args:
            element_graph: Element data structure
            qto_engine: QTO recalculation engine
            cost_engine: Cost recalculation engine
            schedule_engine: Schedule recalculation engine
            approval_engine: Approval engine for marking items as pending
        """
        self.element_graph = element_graph
        self.qto_engine = qto_engine or QTOEngine(element_graph)
        self.cost_engine = cost_engine
        self.schedule_engine = schedule_engine
        self.approval_engine = approval_engine
    
    def get_elements_needing_recalculation(self) -> List[str]:
        """
        Get list of elements flagged for recalculation
        
        Returns:
            List of element IDs
        """
        return [
            eid for eid, el in self.element_graph.items()
            if el.get("needs_recalculation", False)
        ]
    
    def trigger_recalculation(self, user: str = "system") -> Dict:
        """
        Orchestrate controlled cascade recalculation
        
        Args:
            user: User triggering recalculation
        
        Returns:
            Summary of all recalculations
        """
        modified_elements = self.get_elements_needing_recalculation()
        
        if not modified_elements:
            return {
                "message": "No elements need recalculation",
                "modified_elements": [],
                "qto_updates": 0,
                "cost_updates": 0,
                "schedule_updates": 0
            }
        
        results = {
            "message": "Recalculation triggered",
            "triggered_by": user,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "modified_elements": modified_elements,
            "qto_result": None,
            "cost_result": None,
            "schedule_result": None
        }
        
        # Step 1: Recalculate Quantities
        qto_result = self.qto_engine.recalculate(modified_elements)
        results["qto_result"] = qto_result
        
        # Step 2: Recalculate Cost (if engine available)
        if self.cost_engine:
            cost_result = self.cost_engine.recalculate(modified_elements)
            results["cost_result"] = cost_result
        
        # Step 3: Recalculate Schedule (if engine available)
        if self.schedule_engine:
            schedule_result = self.schedule_engine.recalculate(modified_elements)
            results["schedule_result"] = schedule_result
        
        # Step 4: Mark QTO items as "Pending" (requires re-approval)
        if self.approval_engine:
            # Extract QTO item names from modified elements
            qto_items = []
            for eid in modified_elements:
                if eid in self.element_graph:
                    elem_type = self.element_graph[eid].get("type", "Unknown")
                    material = self.element_graph[eid].get("material", "Unknown")
                    qto_item_name = f"{material} in {elem_type}"
                    qto_items.append(qto_item_name)
            
            if qto_items:
                approval_result = self.approval_engine.mark_pending_after_recalculation(qto_items)
                results["approval_result"] = approval_result
        
        # Step 5: Clear recalculation flags
        for eid in modified_elements:
            if eid in self.element_graph:
                self.element_graph[eid]["needs_recalculation"] = False
                self.element_graph[eid]["last_recalculated"] = datetime.utcnow().isoformat() + "Z"
                self.element_graph[eid]["recalculated_by"] = user
        
        return results
    
    def preview_recalculation(self) -> Dict:
        """
        Preview what would be recalculated without actually doing it
        
        Returns:
            Preview of pending recalculations
        """
        modified_elements = self.get_elements_needing_recalculation()
        
        if not modified_elements:
            return {
                "message": "No elements need recalculation",
                "elements": []
            }
        
        preview = []
        for eid in modified_elements:
            element = self.element_graph[eid]
            preview.append({
                "element_id": eid,
                "element_type": element.get("type"),
                "current_quantity": element.get("quantity", {}).get("volume"),
                "current_cost": element.get("cost"),
                "current_schedule": element.get("schedule_days"),
                "will_recalculate": ["QTO", "Cost", "Schedule"]
            })
        
        return {
            "message": "Recalculation preview",
            "elements_to_update": len(modified_elements),
            "preview": preview
        }
    
    def get_recalculation_summary(self) -> Dict:
        """
        Get summary of recalculation status
        
        Returns:
            Summary statistics
        """
        total = len(self.element_graph)
        needs_recalc = len(self.get_elements_needing_recalculation())
        recalculated = sum(
            1 for el in self.element_graph.values()
            if "last_recalculated" in el
        )
        
        return {
            "total_elements": total,
            "needs_recalculation": needs_recalc,
            "previously_recalculated": recalculated,
            "up_to_date": total - needs_recalc
        }
