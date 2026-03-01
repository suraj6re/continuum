from typing import Dict, List, Optional
from datetime import datetime
from change_log import ChangeLogger

class OverrideEngine:
    """
    Controlled mutation layer for Human-in-the-Loop review.
    
    Allows users to:
    - Override dimensions
    - Override material
    - Mark as manually verified
    - Upgrade confidence to human-verified
    
    Does NOT:
    - Recompute QTO (Step 3)
    - Recompute cost (Step 3)
    - Recompute schedule (Step 3)
    
    Core principle: AI suggests, Human corrects, System records safely.
    """
    
    def __init__(self, element_graph: Dict, change_logger: Optional[ChangeLogger] = None):
        """
        Initialize override engine with element graph and change logger
        
        Args:
            element_graph: Structured element data from previous layers
            change_logger: Optional ChangeLogger instance for enterprise logging
        """
        self.element_graph = element_graph
        self.audit_log = []  # Kept for backward compatibility
        self.change_logger = change_logger  # Enterprise-grade logger
    
    def override_dimension(self, element_id: str, field: str, new_value: float, user: str = "system") -> Dict:
        """
        Override a specific dimension field with validation and audit trail
        
        Args:
            element_id: Element identifier
            field: Dimension field (length, thickness, height, width, depth)
            new_value: New dimension value
            user: User making the change (for audit)
        
        Returns:
            Result with old/new values or error
        """
        # Validate element exists
        if element_id not in self.element_graph:
            return {"error": "Element not found", "element_id": element_id}
        
        element = self.element_graph[element_id]
        
        # Validate dimensions exist
        if "dimensions" not in element:
            return {"error": "No dimensions found for this element"}
        
        # Validate field exists
        if field not in element["dimensions"]:
            return {
                "error": f"Invalid dimension field: {field}",
                "available_fields": list(element["dimensions"].keys())
            }
        
        # Validate value is positive
        if new_value <= 0:
            return {"error": "Dimension value must be positive", "value": new_value}
        
        # Store old value for audit
        old_value = element["dimensions"][field]
        
        # Create audit entry (backward compatibility)
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "element_id": element_id,
            "field": field,
            "old_value": old_value,
            "new_value": new_value,
            "user": user,
            "action": "dimension_override"
        }
        self.audit_log.append(audit_entry)
        
        # Log to enterprise change logger if available
        if self.change_logger:
            self.change_logger.log_change(
                element_id=element_id,
                field=field,
                old_value=old_value,
                new_value=new_value,
                edited_by=user,
                action="dimension_override",
                metadata={
                    "element_type": element.get("type"),
                    "confidence_before": element.get("confidence", 0)
                }
            )
        
        # Update dimension
        element["dimensions"][field] = new_value
        
        # Mark manual override
        element["manual_override"] = True
        element["confidence"] = 1.0  # Human verified
        element["needs_recalculation"] = True
        element["last_modified"] = datetime.now().isoformat()
        element["modified_by"] = user
        
        return {
            "message": "Dimension overridden successfully",
            "element_id": element_id,
            "element_type": element.get("type"),
            "field_updated": field,
            "old_value": old_value,
            "new_value": new_value,
            "confidence_upgraded": True,
            "needs_recalculation": True
        }
    
    def override_material(self, element_id: str, new_material: str, user: str = "system") -> Dict:
        """
        Override element material
        
        Args:
            element_id: Element identifier
            new_material: New material specification
            user: User making the change
        
        Returns:
            Result with old/new material or error
        """
        if element_id not in self.element_graph:
            return {"error": "Element not found"}
        
        element = self.element_graph[element_id]
        old_material = element.get("material", "Unknown")
        
        # Create audit entry (backward compatibility)
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "element_id": element_id,
            "field": "material",
            "old_value": old_material,
            "new_value": new_material,
            "user": user,
            "action": "material_override"
        }
        self.audit_log.append(audit_entry)
        
        # Log to enterprise change logger if available
        if self.change_logger:
            self.change_logger.log_change(
                element_id=element_id,
                field="material",
                old_value=old_material,
                new_value=new_material,
                edited_by=user,
                action="material_override",
                metadata={"element_type": element.get("type")}
            )
        
        # Update material
        element["material"] = new_material
        element["manual_override"] = True
        element["confidence"] = 1.0
        element["needs_recalculation"] = True
        element["last_modified"] = datetime.now().isoformat()
        element["modified_by"] = user
        
        return {
            "message": "Material overridden successfully",
            "element_id": element_id,
            "old_material": old_material,
            "new_material": new_material,
            "needs_recalculation": True
        }
    
    def bulk_override_dimensions(self, overrides: List[Dict], user: str = "system") -> Dict:
        """
        Override multiple dimensions at once
        
        Args:
            overrides: List of {element_id, field, new_value}
            user: User making changes
        
        Returns:
            Summary of successful and failed overrides
        """
        results = {"successful": [], "failed": []}
        
        for override in overrides:
            element_id = override.get("element_id")
            field = override.get("field")
            new_value = override.get("new_value")
            
            if not all([element_id, field, new_value is not None]):
                results["failed"].append({
                    "override": override,
                    "error": "Missing required fields"
                })
                continue
            
            result = self.override_dimension(element_id, field, new_value, user)
            
            if "error" in result:
                results["failed"].append({"override": override, "error": result["error"]})
            else:
                results["successful"].append(result)
        
        return {
            "total": len(overrides),
            "successful_count": len(results["successful"]),
            "failed_count": len(results["failed"]),
            "results": results
        }
    
    def mark_as_verified(self, element_id: str, user: str = "system") -> Dict:
        """
        Mark element as human-verified without changing dimensions
        
        Args:
            element_id: Element identifier
            user: User verifying
        
        Returns:
            Verification result
        """
        if element_id not in self.element_graph:
            return {"error": "Element not found"}
        
        element = self.element_graph[element_id]
        
        # Create audit entry (backward compatibility)
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "element_id": element_id,
            "action": "verified",
            "user": user
        }
        self.audit_log.append(audit_entry)
        
        # Log to enterprise change logger if available
        if self.change_logger:
            self.change_logger.log_change(
                element_id=element_id,
                field="verification_status",
                old_value="unverified",
                new_value="verified",
                edited_by=user,
                action="verified",
                metadata={"element_type": element.get("type")}
            )
        
        # Mark as verified
        element["confidence"] = 1.0
        element["human_verified"] = True
        element["verified_by"] = user
        element["verified_at"] = datetime.now().isoformat()
        
        return {
            "message": "Element marked as verified",
            "element_id": element_id,
            "confidence": 1.0,
            "verified_by": user
        }
    
    def revert_override(self, element_id: str, user: str = "system") -> Dict:
        """
        Revert element to AI-extracted values (if audit trail exists)
        
        Args:
            element_id: Element identifier
            user: User reverting
        
        Returns:
            Revert result
        """
        if element_id not in self.element_graph:
            return {"error": "Element not found"}
        
        # Find audit entries for this element
        element_audits = [a for a in self.audit_log if a.get("element_id") == element_id]
        
        if not element_audits:
            return {"error": "No audit trail found for this element"}
        
        element = self.element_graph[element_id]
        reverted_fields = []
        
        # Revert each overridden field
        for audit in reversed(element_audits):
            if audit.get("action") in ["dimension_override", "material_override"]:
                field = audit.get("field")
                old_value = audit.get("old_value")
                
                if field == "material":
                    element["material"] = old_value
                elif "dimensions" in element and field in element["dimensions"]:
                    element["dimensions"][field] = old_value
                
                reverted_fields.append(field)
        
        # Reset flags
        element["manual_override"] = False
        element["needs_recalculation"] = True
        element["last_modified"] = datetime.now().isoformat()
        element["modified_by"] = user
        
        # Log revert action
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "element_id": element_id,
            "action": "revert",
            "reverted_fields": reverted_fields,
            "user": user
        })
        
        return {
            "message": "Element reverted to AI-extracted values",
            "element_id": element_id,
            "reverted_fields": reverted_fields,
            "needs_recalculation": True
        }
    
    def get_audit_log(self, element_id: Optional[str] = None) -> List[Dict]:
        """
        Get audit log for all elements or specific element
        
        Args:
            element_id: Optional element filter
        
        Returns:
            List of audit entries
        """
        if element_id:
            return [a for a in self.audit_log if a.get("element_id") == element_id]
        return self.audit_log
    
    def get_elements_needing_recalculation(self) -> List[str]:
        """
        Get list of element IDs that need recalculation
        
        Returns:
            List of element IDs
        """
        return [
            elem_id
            for elem_id, elem_data in self.element_graph.items()
            if elem_data.get("needs_recalculation", False)
        ]
    
    def get_override_summary(self) -> Dict:
        """
        Get summary of all overrides
        
        Returns:
            Summary statistics
        """
        total_overrides = len(self.audit_log)
        by_action = {}
        by_user = {}
        elements_modified = set()
        
        for audit in self.audit_log:
            action = audit.get("action", "unknown")
            user = audit.get("user", "unknown")
            element_id = audit.get("element_id")
            
            by_action[action] = by_action.get(action, 0) + 1
            by_user[user] = by_user.get(user, 0) + 1
            if element_id:
                elements_modified.add(element_id)
        
        return {
            "total_overrides": total_overrides,
            "by_action": by_action,
            "by_user": by_user,
            "elements_modified": len(elements_modified),
            "elements_needing_recalc": len(self.get_elements_needing_recalculation())
        }
