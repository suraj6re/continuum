export default function HumanReviewOutput({ data }) {
  const allLayers = data || {};

  return (
    <div>
      <h3 className="text-xl font-bold text-brand-charcoal mb-4">Human Review & Approval</h3>
      <p className="text-text-secondary mb-6">
        Review and approve AI-generated results before finalizing the project analysis.
      </p>

      {/* Summary Cards */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-white border border-border-light rounded-lg p-4 shadow-sm">
          <div className="text-2xl font-bold text-brand-charcoal">{allLayers.total_items || 0}</div>
          <div className="text-sm text-text-secondary">Total Items</div>
        </div>
        <div className="bg-white border border-border-light rounded-lg p-4 shadow-sm">
          <div className="text-2xl font-bold text-green-600">{allLayers.approved || 0}</div>
          <div className="text-sm text-text-secondary">Approved</div>
        </div>
        <div className="bg-white border border-border-light rounded-lg p-4 shadow-sm">
          <div className="text-2xl font-bold text-yellow-600">{allLayers.pending || 0}</div>
          <div className="text-sm text-text-secondary">Pending Review</div>
        </div>
        <div className="bg-white border border-border-light rounded-lg p-4 shadow-sm">
          <div className="text-2xl font-bold text-red-600">{allLayers.flagged || 0}</div>
          <div className="text-sm text-text-secondary">Flagged</div>
        </div>
      </div>

      {/* Review Sections */}
      <div className="space-y-6">
        {/* QTO Review */}
        <div className="bg-white border border-border-light rounded-lg p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-semibold text-brand-charcoal">Quantity Take-Off (QTO)</h4>
            <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
              ✓ Approved
            </span>
          </div>
          <div className="space-y-3">
            {(allLayers.qto_items || [
              { item: "RCC M25 Concrete", quantity: "50.5 m³", confidence: "98%", status: "approved" },
              { item: "Steel Fe500", quantity: "2500 kg", confidence: "95%", status: "approved" },
              { item: "Brick Masonry", quantity: "150 m²", confidence: "92%", status: "approved" }
            ]).map((item, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-bg-section rounded">
                <div className="flex-1">
                  <p className="font-medium text-brand-charcoal">{item.item}</p>
                  <p className="text-sm text-text-secondary">Quantity: {item.quantity} • Confidence: {item.confidence}</p>
                </div>
                <div className="flex gap-2">
                  <button className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700">
                    ✓ Approve
                  </button>
                  <button className="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700">
                    ✗ Reject
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Cost Mapping Review */}
        <div className="bg-white border border-border-light rounded-lg p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-semibold text-brand-charcoal">Cost Mapping</h4>
            <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">
              ⚠ Needs Review
            </span>
          </div>
          <div className="space-y-3">
            {(allLayers.cost_items || [
              { item: "RCC M25", mapped_cost: "₹7,200/m³", confidence: "high", status: "pending" },
              { item: "Steel Fe500", mapped_cost: "₹65/kg", confidence: "high", status: "pending" },
              { item: "Brick Masonry", mapped_cost: "₹850/m²", confidence: "medium", status: "flagged" }
            ]).map((item, idx) => (
              <div key={idx} className={`flex items-center justify-between p-3 rounded ${
                item.status === 'flagged' ? 'bg-yellow-50 border border-yellow-200' : 'bg-bg-section'
              }`}>
                <div className="flex-1">
                  <p className="font-medium text-brand-charcoal">{item.item}</p>
                  <p className="text-sm text-text-secondary">
                    Mapped Cost: {item.mapped_cost} • Confidence: {item.confidence}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700">
                    ✓ Approve
                  </button>
                  <button className="px-3 py-1 bg-yellow-600 text-white rounded text-sm hover:bg-yellow-700">
                    ✎ Edit
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Supplier Selection Review */}
        <div className="bg-white border border-border-light rounded-lg p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-semibold text-brand-charcoal">Supplier Selection</h4>
            <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
              ⏳ Pending
            </span>
          </div>
          <div className="space-y-3">
            {(allLayers.suppliers || [
              { material: "Steel Fe500", supplier: "Iron Works", rate: "₹64/kg", distance: "8 km", status: "pending" },
              { material: "Concrete M25", supplier: "Concrete Plus", rate: "₹7,150/m³", distance: "15 km", status: "pending" }
            ]).map((item, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-bg-section rounded">
                <div className="flex-1">
                  <p className="font-medium text-brand-charcoal">{item.material} → {item.supplier}</p>
                  <p className="text-sm text-text-secondary">Rate: {item.rate} • Distance: {item.distance}</p>
                </div>
                <div className="flex gap-2">
                  <button className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700">
                    ✓ Approve
                  </button>
                  <button className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700">
                    ↻ Change
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Schedule Review */}
        <div className="bg-white border border-border-light rounded-lg p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-semibold text-brand-charcoal">Project Schedule</h4>
            <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
              ✓ Approved
            </span>
          </div>
          <div className="p-4 bg-bg-section rounded">
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-text-secondary">Total Duration: </span>
                <span className="font-semibold text-brand-charcoal">6.5 days</span>
              </div>
              <div>
                <span className="text-text-secondary">Critical Tasks: </span>
                <span className="font-semibold text-brand-charcoal">3</span>
              </div>
              <div>
                <span className="text-text-secondary">Total Tasks: </span>
                <span className="font-semibold text-brand-charcoal">3</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="mt-6 flex justify-end gap-4">
        <button className="px-6 py-2 border border-border-light rounded-lg text-brand-charcoal hover:bg-bg-section">
          Request Changes
        </button>
        <button className="px-6 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700">
          Save Draft
        </button>
        <button className="px-6 py-2 bg-brand-green text-white rounded-lg hover:bg-green-700">
          Approve All & Continue
        </button>
      </div>

      {/* Comments Section */}
      <div className="mt-6 bg-white border border-border-light rounded-lg p-6 shadow-sm">
        <h4 className="text-lg font-semibold text-brand-charcoal mb-4">Review Comments</h4>
        <textarea
          className="w-full p-3 border border-border-light rounded-lg text-sm"
          rows="4"
          placeholder="Add any comments or notes about this review..."
        ></textarea>
        <button className="mt-2 px-4 py-2 bg-brand-orange text-white rounded-lg hover:bg-orange-600">
          Add Comment
        </button>
      </div>
    </div>
  );
}
