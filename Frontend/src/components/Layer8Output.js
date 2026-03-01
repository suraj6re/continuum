export default function Layer8Output({ data }) {
  if (!data || !data.results || data.results.length === 0) {
    return (
      <div>
        <h3 className="text-xl font-bold text-brand-charcoal mb-4">Layer 8 - Budget Optimization</h3>
        <div className="bg-bg-section p-6 rounded-lg text-center text-text-secondary">
          No supplier data available
        </div>
      </div>
    );
  }

  return (
    <div>
      <h3 className="text-xl font-bold text-brand-charcoal mb-4">Layer 8 - Budget Optimization</h3>
      <p className="text-text-secondary mb-6">
        Intelligent supplier matching based on cost, distance, and lead time using weighted scoring algorithm.
      </p>

      <div className="space-y-6">
        {data.results.map((item, index) => (
          <div key={index} className="bg-white border border-border-light rounded-lg p-6 shadow-sm">
            {/* Material Information */}
            <div className="mb-4 pb-4 border-b border-border-light">
              <h4 className="text-sm font-semibold text-text-secondary mb-2">Material Required</h4>
              <p className="text-brand-charcoal font-medium">
                {item.material?.toUpperCase() || 'N/A'}
                {item.grade && ` - ${item.grade.toUpperCase()}`}
              </p>
              <div className="flex gap-4 mt-2 text-sm text-text-secondary">
                <span>Quantity: <span className="font-medium text-brand-charcoal">{item.quantity || 0}</span></span>
                <span>Unit: <span className="font-medium text-brand-charcoal">{item.unit || 'N/A'}</span></span>
              </div>
            </div>

            {/* Recommended Supplier */}
            {item.recommended_supplier && (
              <div className="mb-4 pb-4 border-b border-border-light">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-sm font-semibold text-brand-green">✓ Recommended Supplier</h4>
                  <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    BEST MATCH
                  </span>
                </div>
                <p className="text-brand-charcoal font-bold text-lg mb-3">{item.recommended_supplier}</p>
                
                <div className="grid grid-cols-3 gap-4 mb-3">
                  <div className="bg-bg-section p-3 rounded">
                    <span className="text-xs text-text-secondary block mb-1">Rate</span>
                    <span className="font-bold text-brand-charcoal">₹{item.best_rate?.toFixed(2)}/{item.unit}</span>
                  </div>
                  <div className="bg-bg-section p-3 rounded">
                    <span className="text-xs text-text-secondary block mb-1">Distance</span>
                    <span className="font-bold text-brand-charcoal">{item.best_distance} km</span>
                  </div>
                  <div className="bg-bg-section p-3 rounded">
                    <span className="text-xs text-text-secondary block mb-1">Lead Time</span>
                    <span className="font-bold text-brand-charcoal">{item.best_lead_time} days</span>
                  </div>
                </div>

                {/* Estimated Cost */}
                {item.quantity && item.best_rate && (
                  <div className="p-3 bg-green-50 border border-green-200 rounded">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-green-800">Estimated Total Cost:</span>
                      <span className="text-lg font-bold text-green-900">
                        ₹{(item.quantity * item.best_rate).toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                      </span>
                    </div>
                  </div>
                )}

                {/* Reason */}
                {item.reason && (
                  <div className="mt-3 text-xs text-text-secondary italic">
                    {item.reason}
                  </div>
                )}
              </div>
            )}

            {/* Supplier Comparison */}
            {item.comparison && item.comparison.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-brand-charcoal mb-3">
                  Supplier Comparison ({item.total_suppliers_found || item.comparison.length} found)
                </h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-bg-section">
                      <tr>
                        <th className="text-left p-2 font-semibold text-text-secondary">Supplier</th>
                        <th className="text-left p-2 font-semibold text-text-secondary">Location</th>
                        <th className="text-right p-2 font-semibold text-text-secondary">Rate</th>
                        <th className="text-right p-2 font-semibold text-text-secondary">Distance</th>
                        <th className="text-right p-2 font-semibold text-text-secondary">Lead Time</th>
                        <th className="text-center p-2 font-semibold text-text-secondary">Stock</th>
                        <th className="text-right p-2 font-semibold text-text-secondary">Score</th>
                      </tr>
                    </thead>
                    <tbody>
                      {item.comparison.map((supplier, idx) => (
                        <tr 
                          key={idx} 
                          className={`border-t border-border-light ${idx === 0 ? 'bg-green-50' : 'hover:bg-bg-section'}`}
                        >
                          <td className="p-2">
                            <div className="flex items-center gap-2">
                              {idx === 0 && <span className="text-green-600">★</span>}
                              <span className={idx === 0 ? 'font-semibold text-brand-charcoal' : 'text-brand-charcoal'}>
                                {supplier.supplier_name}
                              </span>
                            </div>
                          </td>
                          <td className="p-2 text-text-secondary capitalize">{supplier.location}</td>
                          <td className="p-2 text-right font-medium">₹{supplier.rate?.toFixed(2)}</td>
                          <td className="p-2 text-right">{supplier.distance_km} km</td>
                          <td className="p-2 text-right">{supplier.lead_time_days} days</td>
                          <td className="p-2 text-center">
                            <span className={`px-2 py-1 rounded text-xs ${
                              supplier.availability === 'in stock' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {supplier.availability}
                            </span>
                          </td>
                          <td className="p-2 text-right font-semibold">{supplier.score?.toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="mt-6 p-4 bg-bg-section rounded-lg">
        <h4 className="text-sm font-semibold text-brand-charcoal mb-3">Summary</h4>
        <div className="grid grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-text-secondary">Total Materials: </span>
            <span className="font-semibold text-brand-charcoal">{data.results.length}</span>
          </div>
          <div>
            <span className="text-text-secondary">Suppliers Found: </span>
            <span className="font-semibold text-brand-charcoal">
              {data.results.reduce((sum, r) => sum + (r.total_suppliers_found || 0), 0)}
            </span>
          </div>
          <div>
            <span className="text-text-secondary">Avg Distance: </span>
            <span className="font-semibold text-brand-charcoal">
              {(data.results.reduce((sum, r) => sum + (r.best_distance || 0), 0) / data.results.length).toFixed(1)} km
            </span>
          </div>
          <div>
            <span className="text-text-secondary">Avg Lead Time: </span>
            <span className="font-semibold text-brand-charcoal">
              {(data.results.reduce((sum, r) => sum + (r.best_lead_time || 0), 0) / data.results.length).toFixed(1)} days
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
