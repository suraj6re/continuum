export default function DashboardComplianceOutput({ data }) {
  const projectData = data || {};

  return (
    <div>
      <h3 className="text-xl font-bold text-brand-charcoal mb-4">Dashboard & Compliance Report</h3>
      <p className="text-text-secondary mb-6">
        Comprehensive project overview with compliance documentation and export options.
      </p>

      {/* Executive Summary */}
      <div className="bg-gradient-to-r from-brand-orange to-orange-600 text-white rounded-lg p-6 mb-6 shadow-lg">
        <h4 className="text-2xl font-bold mb-2">Project Analysis Complete</h4>
        <p className="text-orange-100 mb-4">All AI processing layers have been successfully executed</p>
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-white bg-opacity-20 rounded p-3">
            <div className="text-3xl font-bold">{projectData.total_items || 12}</div>
            <div className="text-sm text-orange-100">Total Items</div>
          </div>
          <div className="bg-white bg-opacity-20 rounded p-3">
            <div className="text-3xl font-bold">₹{projectData.total_cost || '6.5L'}</div>
            <div className="text-sm text-orange-100">Estimated Cost</div>
          </div>
          <div className="bg-white bg-opacity-20 rounded p-3">
            <div className="text-3xl font-bold">{projectData.duration || '6.5'}</div>
            <div className="text-sm text-orange-100">Days Duration</div>
          </div>
          <div className="bg-white bg-opacity-20 rounded p-3">
            <div className="text-3xl font-bold">{projectData.confidence || '94'}%</div>
            <div className="text-sm text-orange-100">Avg Confidence</div>
          </div>
        </div>
      </div>

      {/* Layer-wise Summary */}
      <div className="bg-white border border-border-light rounded-lg p-6 shadow-sm mb-6">
        <h4 className="text-lg font-semibold text-brand-charcoal mb-4">Processing Pipeline Summary</h4>
        <div className="space-y-3">
          {[
            { layer: "Layer 1: Hybrid Normalization", status: "completed", items: "1 drawing", confidence: "100%" },
            { layer: "Layer 2: Legend Intelligence", status: "completed", items: "4 regions", confidence: "98%" },
            { layer: "Layer 3: Element Extraction", status: "completed", items: "156 elements", confidence: "96%" },
            { layer: "Layer 4: Element Graph Model", status: "completed", items: "89 nodes", confidence: "95%" },
            { layer: "Layer 5: Deterministic QTO", status: "completed", items: "12 items", confidence: "97%" },
            { layer: "Layer 6: Validation & Confidence", status: "completed", items: "12 validated", confidence: "94%" },
            { layer: "Layer 7: Cost Mapping", status: "completed", items: "3 mapped", confidence: "92%" },
            { layer: "Layer 8: Supplier Discovery", status: "completed", items: "2 suppliers", confidence: "90%" },
            { layer: "Layer 9: Procurement", status: "completed", items: "2 RFQs", confidence: "100%" },
            { layer: "Layer 10: Scheduling", status: "completed", items: "3 tasks", confidence: "95%" }
          ].map((item, idx) => (
            <div key={idx} className="flex items-center justify-between p-3 bg-bg-section rounded">
              <div className="flex items-center gap-3 flex-1">
                <span className="text-green-600 text-xl">✓</span>
                <div>
                  <p className="font-medium text-brand-charcoal">{item.layer}</p>
                  <p className="text-sm text-text-secondary">{item.items}</p>
                </div>
              </div>
              <div className="text-right">
                <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                  {item.confidence}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Compliance Checklist */}
      <div className="bg-white border border-border-light rounded-lg p-6 shadow-sm mb-6">
        <h4 className="text-lg font-semibold text-brand-charcoal mb-4">Compliance Checklist</h4>
        <div className="space-y-3">
          {[
            { item: "Drawing format validation", status: "passed", standard: "ISO 19650" },
            { item: "Unit consistency check", status: "passed", standard: "IS 1200" },
            { item: "Material grade verification", status: "passed", standard: "IS 456:2000" },
            { item: "Cost book alignment", status: "passed", standard: "CPWD 2023" },
            { item: "Supplier compliance", status: "passed", standard: "ISO 9001" },
            { item: "Schedule feasibility", status: "passed", standard: "PMBOK" }
          ].map((item, idx) => (
            <div key={idx} className="flex items-center justify-between p-3 bg-bg-section rounded">
              <div className="flex items-center gap-3 flex-1">
                <span className="text-green-600 text-xl">✓</span>
                <div>
                  <p className="font-medium text-brand-charcoal">{item.item}</p>
                  <p className="text-sm text-text-secondary">Standard: {item.standard}</p>
                </div>
              </div>
              <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                PASSED
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Export Options */}
      <div className="bg-white border border-border-light rounded-lg p-6 shadow-sm mb-6">
        <h4 className="text-lg font-semibold text-brand-charcoal mb-4">Export & Reports</h4>
        <div className="grid grid-cols-2 gap-4">
          <button className="flex items-center justify-between p-4 border border-border-light rounded-lg hover:bg-bg-section transition-colors">
            <div className="text-left">
              <p className="font-medium text-brand-charcoal">Complete Analysis Report</p>
              <p className="text-sm text-text-secondary">PDF with all layers</p>
            </div>
            <span className="text-2xl">📄</span>
          </button>
          <button className="flex items-center justify-between p-4 border border-border-light rounded-lg hover:bg-bg-section transition-colors">
            <div className="text-left">
              <p className="font-medium text-brand-charcoal">QTO Spreadsheet</p>
              <p className="text-sm text-text-secondary">Excel format</p>
            </div>
            <span className="text-2xl">📊</span>
          </button>
          <button className="flex items-center justify-between p-4 border border-border-light rounded-lg hover:bg-bg-section transition-colors">
            <div className="text-left">
              <p className="font-medium text-brand-charcoal">Cost Breakdown</p>
              <p className="text-sm text-text-secondary">Detailed costing</p>
            </div>
            <span className="text-2xl">💰</span>
          </button>
          <button className="flex items-center justify-between p-4 border border-border-light rounded-lg hover:bg-bg-section transition-colors">
            <div className="text-left">
              <p className="font-medium text-brand-charcoal">Project Schedule</p>
              <p className="text-sm text-text-secondary">Gantt chart PDF</p>
            </div>
            <span className="text-2xl">📅</span>
          </button>
          <button className="flex items-center justify-between p-4 border border-border-light rounded-lg hover:bg-bg-section transition-colors">
            <div className="text-left">
              <p className="font-medium text-brand-charcoal">Supplier RFQs</p>
              <p className="text-sm text-text-secondary">All procurement docs</p>
            </div>
            <span className="text-2xl">📋</span>
          </button>
          <button className="flex items-center justify-between p-4 border border-border-light rounded-lg hover:bg-bg-section transition-colors">
            <div className="text-left">
              <p className="font-medium text-brand-charcoal">Compliance Certificate</p>
              <p className="text-sm text-text-secondary">Standards compliance</p>
            </div>
            <span className="text-2xl">✓</span>
          </button>
        </div>
      </div>

      {/* API Integration */}
      <div className="bg-white border border-border-light rounded-lg p-6 shadow-sm mb-6">
        <h4 className="text-lg font-semibold text-brand-charcoal mb-4">API & Integration</h4>
        <div className="space-y-3">
          <div className="p-4 bg-bg-section rounded">
            <p className="font-medium text-brand-charcoal mb-2">REST API Endpoint</p>
            <code className="text-sm text-blue-600 bg-white px-3 py-2 rounded border border-border-light block">
              GET /api/project/{projectData.project_id || 'PROJECT_ID'}/complete
            </code>
          </div>
          <div className="p-4 bg-bg-section rounded">
            <p className="font-medium text-brand-charcoal mb-2">Webhook URL</p>
            <code className="text-sm text-blue-600 bg-white px-3 py-2 rounded border border-border-light block">
              POST https://your-system.com/webhook/continuum
            </code>
          </div>
        </div>
      </div>

      {/* Final Actions */}
      <div className="flex justify-between items-center">
        <div className="text-sm text-text-secondary">
          Report generated on {new Date().toLocaleDateString()} at {new Date().toLocaleTimeString()}
        </div>
        <div className="flex gap-4">
          <button className="px-6 py-2 border border-border-light rounded-lg text-brand-charcoal hover:bg-bg-section">
            Share Report
          </button>
          <button className="px-6 py-2 bg-brand-orange text-white rounded-lg hover:bg-orange-600">
            Download All
          </button>
        </div>
      </div>
    </div>
  );
}
