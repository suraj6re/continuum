from typing import Dict, List, Optional

class ApprovalEngine:
    """
    Approval Status Engine - Final governance lock for QTO items
    
    Core principle: Only approved items can be finalized/exported
    
    Status flow:
    - "Pending" (default after recalculation)
    - "Approved" (explicitly approved by user)
    - "Rejected" (flagged as incorrect)
    - "Needs Review" (requires additional review)
    
    Key logic:
    - Any override → auto-mark as "Pending"
    - User must explicitly approve
    - Only "Approved" items are exportable
    """
    
    ALLOWED_STATUSES = ["Pending", "Approved", "Rejected", "Needs Review"]
    
    def __init__(self, qto_summary: Dict):
        """
        Initialize approval engine with QTO summary
        
        Args:
            qto_summary: QTO summary with items and their data
        """
        self.qto_summary = qto_summary
        self._ensure_status_fields()
    
    def _ensure_status_fields(self):
        """Ensure all QTO items have status field"""
        for item_name, data in self.qto_summary.items():
            if isinstance(data, dict) and "status" not in data:
                data["status"] = "Pending"
    
    def set_status(self, item_name: str, status: str) -> Dict:
        """
        Set approval status for a QTO item
        
        Args:
            item_name: QTO item name
            status: New status (Pending/Approved/Rejected/Needs Review)
        
        Returns:
            Result with message or error
        """
        if item_name not in self.qto_summary:
            return {"error": "QTO item not found", "item": item_name}
        
        if status not in self.ALLOWED_STATUSES:
            return {
                "error": "Invalid status",
                "provided": status,
                "allowed": self.ALLOWED_STATUSES
            }
        
        self.qto_summary[item_name]["status"] = status
        
        return {
            "message": "Status updated",
            "item": item_name,
            "new_status": status
        }
    
    def approve_item(self, item_name: str) -> Dict:
        """
        Approve a QTO item (shortcut for set_status)
        
        Args:
            item_name: QTO item name
        
        Returns:
            Result with message or error
        """
        return self.set_status(item_name, "Approved")
    
    def reject_item(self, item_name: str) -> Dict:
        """
        Reject a QTO item (shortcut for set_status)
        
        Args:
            item_name: QTO item name
        
        Returns:
            Result with message or error
        """
        return self.set_status(item_name, "Rejected")
    
    def mark_needs_review(self, item_name: str) -> Dict:
        """
        Mark QTO item as needing review (shortcut for set_status)
        
        Args:
            item_name: QTO item name
        
        Returns:
            Result with message or error
        """
        return self.set_status(item_name, "Needs Review")
    
    def bulk_approve(self, item_names: List[str]) -> Dict:
        """
        Approve multiple QTO items at once
        
        Args:
            item_names: List of QTO item names
        
        Returns:
            Summary of successful and failed approvals
        """
        results = {"successful": [], "failed": []}
        
        for item_name in item_names:
            result = self.approve_item(item_name)
            
            if "error" in result:
                results["failed"].append({"item": item_name, "error": result["error"]})
            else:
                results["successful"].append(item_name)
        
        return {
            "total": len(item_names),
            "successful_count": len(results["successful"]),
            "failed_count": len(results["failed"]),
            "results": results
        }
    
    def get_unapproved_items(self) -> Dict:
        """
        Get all items that are not approved
        
        Returns:
            Dictionary of unapproved items with their data
        """
        return {
            item: data
            for item, data in self.qto_summary.items()
            if isinstance(data, dict) and data.get("status") != "Approved"
        }
    
    def get_items_by_status(self, status: str) -> Dict:
        """
        Get all items with a specific status
        
        Args:
            status: Status to filter by
        
        Returns:
            Dictionary of items with the specified status
        """
        if status not in self.ALLOWED_STATUSES:
            return {"error": "Invalid status", "allowed": self.ALLOWED_STATUSES}
        
        return {
            item: data
            for item, data in self.qto_summary.items()
            if isinstance(data, dict) and data.get("status") == status
        }
    
    def get_approval_summary(self) -> Dict:
        """
        Get summary of approval statuses
        
        Returns:
            Summary with counts by status
        """
        summary = {status: 0 for status in self.ALLOWED_STATUSES}
        total = 0
        
        for data in self.qto_summary.values():
            if isinstance(data, dict):
                status = data.get("status", "Pending")
                summary[status] = summary.get(status, 0) + 1
                total += 1
        
        return {
            "total_items": total,
            "by_status": summary,
            "approved_count": summary["Approved"],
            "unapproved_count": total - summary["Approved"],
            "ready_for_export": summary["Approved"] == total
        }
    
    def can_export(self) -> Dict:
        """
        Check if QTO can be exported (all items approved)
        
        Returns:
            Export readiness status
        """
        unapproved = self.get_unapproved_items()
        
        if unapproved:
            return {
                "can_export": False,
                "reason": "Unapproved items exist",
                "unapproved_count": len(unapproved),
                "unapproved_items": list(unapproved.keys())
            }
        
        return {
            "can_export": True,
            "message": "All items approved - ready for export"
        }
    
    def mark_pending_after_recalculation(self, item_names: List[str]) -> Dict:
        """
        Mark items as pending after recalculation
        Called automatically when items are recalculated
        
        Args:
            item_names: List of recalculated item names
        
        Returns:
            Summary of items marked as pending
        """
        marked = []
        
        for item_name in item_names:
            if item_name in self.qto_summary:
                self.qto_summary[item_name]["status"] = "Pending"
                marked.append(item_name)
        
        return {
            "message": "Items marked as pending after recalculation",
            "count": len(marked),
            "items": marked
        }
