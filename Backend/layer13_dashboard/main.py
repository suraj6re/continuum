from fastapi import FastAPI
from fastapi.responses import FileResponse
from dashboard_api import DashboardAPI
from report_generator import ReportGenerator
from compliance_generator import ComplianceGenerator
import os

app = FastAPI(title="Layer 13 - Dashboard API (Step 1)")

# Mock engines for demonstration
class MockQTOEngine:
    def get_summary(self):
        return {
            "Concrete in Slab": {
                "quantity": 12.45,
                "unit": "m3",
                "status": "Pending"
            },
            "Brickwork": {
                "quantity": 8.23,
                "unit": "m3",
                "status": "Approved"
            },
            "RCC in Column": {
                "quantity": 5.67,
                "unit": "m3",
                "status": "Approved"
            }
        }

class MockCostEngine:
    def get_summary(self):
        return {
            "total_cost": 456000,
            "item_wise": {
                "Concrete in Slab": 85600,
                "Brickwork": 34200,
                "RCC in Column": 42000,
                "Steel Reinforcement": 294200
            },
            "floor_wise": {
                "Ground Floor": 250000,
                "First Floor": 206000
            }
        }

class MockScheduleEngine:
    def get_summary(self):
        return {
            "total_duration": 48,
            "critical_path": ["Foundation", "Slab", "Columns", "Roof"],
            "tasks": [
                {"name": "Foundation", "duration": 12, "status": "completed"},
                {"name": "Slab", "duration": 15, "status": "in_progress"},
                {"name": "Columns", "duration": 10, "status": "pending"},
                {"name": "Roof", "duration": 11, "status": "pending"}
            ]
        }

class MockApprovalEngine:
    def get_approval_summary(self):
        return {
            "total_items": 4,
            "by_status": {
                "Pending": 1,
                "Approved": 2,
                "Rejected": 0,
                "Needs Review": 1
            },
            "approved_count": 2,
            "unapproved_count": 2,
            "ready_for_export": False
        }

class MockRiskEngine:
    def get_summary(self):
        return {
            "high_risk_items": 3,
            "confidence_score": 0.87,
            "uncertainty": "±4%",
            "risk_factors": [
                {"item": "Concrete in Slab", "risk": "Medium", "reason": "Pending approval"},
                {"item": "Steel Reinforcement", "risk": "High", "reason": "Low confidence"}
            ]
        }

class MockConfidenceEngine:
    def get_summary(self):
        return {
            "average": 0.89,
            "low_confidence_elements": 2,
            "by_type": {
                "Wall": 0.92,
                "Slab": 0.88,
                "Column": 0.85,
                "Beam": 0.91
            }
        }

# Initialize dashboard API with mock engines
dashboard_api = DashboardAPI(
    qto_engine=MockQTOEngine(),
    cost_engine=MockCostEngine(),
    schedule_engine=MockScheduleEngine(),
    approval_engine=MockApprovalEngine(),
    risk_engine=MockRiskEngine(),
    confidence_engine=MockConfidenceEngine()
)

@app.get("/")
def root():
    return {
        "message": "Layer 13 - Dashboard API (Complete)",
        "description": "Unified summary, PDF export, and compliance certificates",
        "endpoints": {
            "/dashboard": "Get consolidated dashboard data",
            "/export/pdf": "Generate PDF compliance report",
            "/export/compliance": "Generate ISO-compliant certificate",
            "/health": "Health check"
        },
        "compliance": {
            "standards": ["ISO 19650-2:2018"],
            "formats": ["Government submission ready", "Audit trail enabled"]
        },
        "principles": [
            "Read-only aggregation",
            "No computation",
            "No data modification",
            "Fast (<100ms)",
            "Presentation-ready",
            "Compliance-grade exports",
            "ISO-aligned certification"
        ]
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "layer": 13,
        "step": 1,
        "engines_loaded": {
            "qto": dashboard_api.qto_engine is not None,
            "cost": dashboard_api.cost_engine is not None,
            "schedule": dashboard_api.schedule_engine is not None,
            "approval": dashboard_api.approval_engine is not None,
            "risk": dashboard_api.risk_engine is not None,
            "confidence": dashboard_api.confidence_engine is not None
        }
    }

@app.get("/dashboard")
def dashboard():
    """
    Unified dashboard endpoint.
    
    Returns consolidated data from all engines:
    - Summary (approval status, export readiness)
    - QTO data
    - Cost breakdown
    - Schedule information
    - Risk assessment
    - Confidence metrics
    - Export status
    """
    return dashboard_api.get_dashboard_data()

@app.post("/export/pdf")
def export_pdf():
    """
    Generate PDF compliance report.
    
    Returns:
        File download response with generated PDF
    """
    # Get dashboard data
    dashboard_data = dashboard_api.get_dashboard_data()
    
    # Generate PDF
    generator = ReportGenerator(dashboard_data)
    file_path = "project_compliance_report.pdf"
    generator.generate_pdf(file_path)
    
    # Return file for download
    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename="project_compliance_report.pdf"
    )

@app.post("/export/compliance")
def export_compliance_certificate():
    """
    Generate ISO-compliant compliance certificate.
    Aligned with ISO 19650 and government submission formats.
    
    Returns:
        File download response with compliance certificate
    """
    # Get dashboard data
    dashboard_data = dashboard_api.get_dashboard_data()
    
    # Project info (in production, load from database)
    project_info = {
        "name": "Sample Construction Project",
        "certifier": "Chief Engineer",
        "certifier_title": "Senior Project Engineer",
        "organization": "Construction Management Ltd."
    }
    
    # Generate compliance certificate
    generator = ComplianceGenerator(dashboard_data, project_info)
    file_path = "compliance_certificate.pdf"
    generator.generate_compliance_certificate(file_path)
    
    # Return file for download
    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename="compliance_certificate.pdf"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
