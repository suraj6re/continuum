from typing import Dict, Optional

class DashboardAPI:
    """
    Unified Summary Endpoint - Read-only aggregation layer
    
    Principles:
    - Does NOT compute anything
    - Does NOT modify data
    - Only aggregates from engines
    - Fast (<100ms)
    - Presentation-ready
    """
    
    def __init__(
        self,
        qto_engine=None,
        cost_engine=None,
        schedule_engine=None,
        approval_engine=None,
        risk_engine=None,
        confidence_engine=None
    ):
        self.qto_engine = qto_engine
        self.cost_engine = cost_engine
        self.schedule_engine = schedule_engine
        self.approval_engine = approval_engine
        self.risk_engine = risk_engine
        self.confidence_engine = confidence_engine
    
    def get_dashboard_data(self) -> Dict:
        """
        Unified summary endpoint.
        Aggregates data from all engines.
        Read-only operation.
        
        Returns:
            Consolidated dashboard data
        """
        # Get approval summary first (needed for export status)
        approval_summary = self._get_approval_data()
        export_ready = approval_summary.get("ready_for_export", False)
        
        return {
            "summary": {
                "total_items": approval_summary.get("total_items", 0),
                "approved_count": approval_summary.get("approved_count", 0),
                "unapproved_count": approval_summary.get("unapproved_count", 0),
                "export_ready": export_ready
            },
            "qto": self._get_qto_data(),
            "cost": self._get_cost_data(),
            "schedule": self._get_schedule_data(),
            "risk": self._get_risk_data(),
            "confidence": self._get_confidence_data(),
            "export_status": {
                "can_export": export_ready,
                "reason": None if export_ready else "Unapproved items exist"
            }
        }
    
    def _get_qto_data(self) -> Dict:
        """Get QTO summary from QTO engine"""
        if self.qto_engine and hasattr(self.qto_engine, 'get_summary'):
            return self.qto_engine.get_summary()
        return {}
    
    def _get_cost_data(self) -> Dict:
        """Get cost summary from cost engine"""
        if self.cost_engine and hasattr(self.cost_engine, 'get_summary'):
            return self.cost_engine.get_summary()
        return {"total_cost": 0, "item_wise": {}}
    
    def _get_schedule_data(self) -> Dict:
        """Get schedule summary from schedule engine"""
        if self.schedule_engine and hasattr(self.schedule_engine, 'get_summary'):
            return self.schedule_engine.get_summary()
        return {"total_duration": 0, "critical_path": [], "tasks": []}
    
    def _get_approval_data(self) -> Dict:
        """Get approval summary from approval engine"""
        if self.approval_engine and hasattr(self.approval_engine, 'get_approval_summary'):
            return self.approval_engine.get_approval_summary()
        return {
            "total_items": 0,
            "approved_count": 0,
            "unapproved_count": 0,
            "ready_for_export": False
        }
    
    def _get_risk_data(self) -> Dict:
        """Get risk summary from risk engine"""
        if self.risk_engine and hasattr(self.risk_engine, 'get_summary'):
            return self.risk_engine.get_summary()
        return {
            "high_risk_items": 0,
            "confidence_score": 0.0,
            "uncertainty": "N/A"
        }
    
    def _get_confidence_data(self) -> Dict:
        """Get confidence summary from confidence engine"""
        if self.confidence_engine and hasattr(self.confidence_engine, 'get_summary'):
            return self.confidence_engine.get_summary()
        return {
            "average": 0.0,
            "low_confidence_elements": 0
        }
