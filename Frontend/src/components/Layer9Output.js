export default function Layer9Output({ data }) {
  if (!data || !data.results || data.results.length === 0) {
    return (
      <div>
        <h3 className="text-xl font-bold text-brand-charcoal mb-4">Layer 9 - Supplier & Procurement</h3>
        <div className="bg-bg-section p-6 rounded-lg text-center text-text-secondary">
          No procurement data available
        </div>
      </div>
    );
  }

  return (
    <div>
      <h3 className="text-xl font-bold text-brand-charcoal mb-4">Layer 9 - Supplier & Procurement</h3>
      <p className="text-text-secondary mb-6">
        Professional RFQ and WhatsApp message generation for supplier communication with automated logging.
      </p>

      <div className="space-y-6">
        {data.results.map((item, index) => (
          <div key={index} className="bg-white border border-border-light rounded-lg p-6 shadow-sm">
            {/* Supplier & Material Info */}
            <div className="mb-4 pb-4 border-b border-border-light">
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-lg font-bold text-brand-charcoal">{item.supplier_name}</h4>
                <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {item.supplier_location?.toUpperCase() || 'N/A'}
                </span>
              </div>
              <p className="text-text-secondary text-sm mb-2">{item.material}</p>
              <div className="flex gap-4 text-sm">
                <span className="text-text-secondary">
                  Quantity: <span className="font-medium text-brand-charcoal">{item.quantity} {item.unit}</span>
                </span>
                <span className="text-text-secondary">
                  Expected Rate: <span className="font-medium text-brand-charcoal">₹{item.expected_rate?.toFixed(2)}/{item.unit}</span>
                </span>
                {item.distance_km && (
                  <span className="text-text-secondary">
                    Distance: <span className="font-medium text-brand-charcoal">{item.distance_km} km</span>
                  </span>
                )}
              </div>
            </div>

            {/* RFQ Document */}
            {item.rfq_text && (
              <div className="mb-4">
                <div className="flex items-center justify-between mb-3">
                  <h5 className="text-sm font-semibold text-brand-charcoal">📄 Request for Quotation (RFQ)</h5>
                  <button 
                    onClick={() => navigator.clipboard.writeText(item.rfq_text)}
                    className="px-3 py-1 text-xs bg-brand-orange text-white rounded hover:bg-opacity-90 transition"
                  >
                    Copy RFQ
                  </button>
                </div>
                <div className="bg-gray-50 p-4 rounded border border-gray-200 font-mono text-xs whitespace-pre-wrap max-h-64 overflow-y-auto">
                  {item.rfq_text}
                </div>
              </div>
            )}

            {/* WhatsApp Message */}
            {item.whatsapp_message && (
              <div className="mb-4">
                <div className="flex items-center justify-between mb-3">
                  <h5 className="text-sm font-semibold text-brand-charcoal">💬 WhatsApp Message</h5>
                  <div className="flex gap-2">
                    <span className="text-xs text-text-secondary">
                      {item.whatsapp_message.length} characters
                    </span>
                    <button 
                      onClick={() => navigator.clipboard.writeText(item.whatsapp_message)}
                      className="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700 transition"
                    >
                      Copy Message
                    </button>
                  </div>
                </div>
                <div className="bg-green-50 p-4 rounded border border-green-200 text-sm whitespace-pre-wrap max-h-48 overflow-y-auto">
                  {item.whatsapp_message}
                </div>
              </div>
            )}

            {/* Communication Log */}
            {item.communication_log && (
              <div className="bg-bg-section p-4 rounded">
                <h5 className="text-sm font-semibold text-brand-charcoal mb-3">📋 Communication Log</h5>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-text-secondary">Log ID: </span>
                    <span className="font-mono text-xs text-brand-charcoal">{item.communication_log.log_id}</span>
                  </div>
                  <div>
                    <span className="text-text-secondary">Timestamp: </span>
                    <span className="text-brand-charcoal">{item.communication_log.timestamp}</span>
                  </div>
                  <div>
                    <span className="text-text-secondary">Mode: </span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      item.communication_log.mode === 'RFQ' ? 'bg-blue-100 text-blue-800' :
                      item.communication_log.mode === 'WhatsApp' ? 'bg-green-100 text-green-800' :
                      'bg-purple-100 text-purple-800'
                    }`}>
                      {item.communication_log.mode}
                    </span>
                  </div>
                  <div>
                    <span className="text-text-secondary">Status: </span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      item.communication_log.status === 'Drafted' ? 'bg-yellow-100 text-yellow-800' :
                      item.communication_log.status === 'Sent' ? 'bg-blue-100 text-blue-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {item.communication_log.status}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="mt-4 flex gap-3">
              <button className="flex-1 px-4 py-2 bg-brand-orange text-white rounded hover:bg-opacity-90 transition text-sm font-medium">
                Send RFQ via Email
              </button>
              <button className="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition text-sm font-medium">
                Send via WhatsApp
              </button>
              <button className="px-4 py-2 border border-border-light text-brand-charcoal rounded hover:bg-bg-section transition text-sm font-medium">
                Mark as Sent
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="mt-6 p-4 bg-bg-section rounded-lg">
        <h4 className="text-sm font-semibold text-brand-charcoal mb-3">Procurement Summary</h4>
        <div className="grid grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-text-secondary">Total RFQs: </span>
            <span className="font-semibold text-brand-charcoal">{data.results.length}</span>
          </div>
          <div>
            <span className="text-text-secondary">Suppliers Contacted: </span>
            <span className="font-semibold text-brand-charcoal">
              {new Set(data.results.map(r => r.supplier_name)).size}
            </span>
          </div>
          <div>
            <span className="text-text-secondary">Total Value: </span>
            <span className="font-semibold text-brand-charcoal">
              ₹{data.results.reduce((sum, r) => sum + (r.quantity * r.expected_rate || 0), 0).toLocaleString('en-IN')}
            </span>
          </div>
          <div>
            <span className="text-text-secondary">Avg Distance: </span>
            <span className="font-semibold text-brand-charcoal">
              {(data.results.reduce((sum, r) => sum + (r.distance_km || 0), 0) / data.results.length).toFixed(1)} km
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
