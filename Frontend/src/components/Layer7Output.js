export default function Layer8Output({ data }) {
  if (!data || !data.results || data.results.length === 0) {
    return (
      <div>
        <h3 className="text-xl font-bold text-brand-charcoal mb-4">Layer 8 - Cost & Risk Engine</h3>
        <div className="bg-bg-section p-6 rounded-lg text-center text-text-secondary">
          No cost mapping data available
        </div>
      </div>
    );
  }

  return (
    <div>
      <h3 className="text-xl font-bold text-brand-charcoal mb-4">Layer 8 - Cost & Risk Engine</h3>
      <p className="text-text-secondary mb-6">
        AI-powered cost matching that aligns QTO items with standardized cost book entries using semantic understanding and ML re-ranking.
      </p>

      <div className="space-y-6">
        {data.results.map((item, index) => (
          <div key={index} className="bg-white border border-border-light rounded-lg p-6 shadow-sm">
            {/* Query Information */}
            <div className="mb-4 pb-4 border-b border-border-light">
              <h4 className="text-sm font-semibold text-text-secondary mb-2">QTO Item</h4>
              <p className="text-brand-charcoal font-medium">{item.query?.description || 'N/A'}</p>
              <div className="flex gap-4 mt-2 text-sm text-text-secondary">
                <span>Quantity: <span className="font-medium text-brand-charcoal">{item.query?.quantity || 0}</span></span>
                <span>Unit: <span className="font-medium text-brand-charcoal">{item.query?.unit || 'N/A'}</span></span>
              </div>
            </div>

            {/* Best Match */}
            {item.best_match && (
              <div className="mb-4 pb-4 border-b border-border-light">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-sm font-semibold text-brand-green">✓ Best Match</h4>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    item.best_match.confidence === 'high' ? 'bg-green-100 text-green-800' :
                    item.best_match.confidence === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {item.best_match.confidence?.toUpperCase()} CONFIDENCE
                  </span>
                </div>
                <p className="text-brand-charcoal font-medium mb-2">{item.best_match.description}</p>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-text-secondary">Rate: </span>
                    <span className="font-semibold text-brand-charcoal">₹{item.best_match.rate?.toFixed(2)}/{item.best_match.unit}</span>
                  </div>
                  <div>
                    <span className="text-text-secondary">ML Probability: </span>
                    <span className="font-semibold text-brand-charcoal">{(item.best_match.ml_probability * 100).toFixed(1)}%</span>
                  </div>
                </div>

                {/* Cost Mapping */}
                {item.best_match.cost_mapping && (
                  <div className="mt-3 p-3 bg-bg-section rounded">
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <span className="text-text-secondary">Mapped Cost: </span>
                        <span className="font-bold text-brand-green">₹{item.best_match.cost_mapping.mapped_cost?.toFixed(2)}</span>
                      </div>
                      <div>
                        <span className="text-text-secondary">Total: </span>
                        <span className="font-bold text-brand-charcoal">₹{item.best_match.cost_mapping.total_cost?.toFixed(2)}</span>
                      </div>
                      {item.best_match.cost_mapping.conversion_factor && (
                        <div className="col-span-2">
                          <span className="text-text-secondary">Conversion: </span>
                          <span className="text-xs text-brand-charcoal">{item.best_match.cost_mapping.conversion_note}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Match Details */}
                <div className="mt-3 flex gap-2 flex-wrap">
                  {item.best_match.match_details?.grade_matched && (
                    <span className="px-2 py-1 bg-green-50 text-green-700 text-xs rounded">✓ Grade Match</span>
                  )}
                  {item.best_match.match_details?.unit_matched && (
                    <span className="px-2 py-1 bg-green-50 text-green-700 text-xs rounded">✓ Unit Match</span>
                  )}
                  {item.best_match.match_details?.component_matched && (
                    <span className="px-2 py-1 bg-green-50 text-green-700 text-xs rounded">✓ Component Match</span>
                  )}
                  <span className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded">
                    Semantic: {(item.best_match.match_details?.semantic_score * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            )}

            {/* Alternative Matches */}
            {item.top_matches && item.top_matches.length > 1 && (
              <div>
                <h4 className="text-sm font-semibold text-text-secondary mb-3">Alternative Matches</h4>
                <div className="space-y-2">
                  {item.top_matches.slice(1).map((match, idx) => (
                    <div key={idx} className="p-3 bg-bg-section rounded text-sm">
                      <div className="flex justify-between items-start mb-1">
                        <p className="text-brand-charcoal font-medium flex-1">{match.description}</p>
                        <span className="text-text-secondary ml-2">₹{match.rate?.toFixed(2)}/{match.unit}</span>
                      </div>
                      <div className="flex gap-3 text-xs text-text-secondary">
                        <span>Probability: {(match.ml_probability * 100).toFixed(1)}%</span>
                        <span className={match.cost_mapping?.can_map ? 'text-green-600' : 'text-red-600'}>
                          {match.cost_mapping?.can_map ? '✓ Can Map' : '✗ Cannot Map'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Needs Review Warning */}
            {item.needs_review && (
              <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded flex items-start gap-2">
                <span className="text-yellow-600">⚠️</span>
                <div className="text-sm text-yellow-800">
                  <strong>Review Required:</strong> Low confidence match or unit mismatch detected. Please verify the cost mapping manually.
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="mt-6 p-4 bg-bg-section rounded-lg">
        <h4 className="text-sm font-semibold text-brand-charcoal mb-3">Summary</h4>
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <span className="text-text-secondary">Total Items: </span>
            <span className="font-semibold text-brand-charcoal">{data.results.length}</span>
          </div>
          <div>
            <span className="text-text-secondary">High Confidence: </span>
            <span className="font-semibold text-green-600">
              {data.results.filter(r => r.best_match?.confidence === 'high').length}
            </span>
          </div>
          <div>
            <span className="text-text-secondary">Needs Review: </span>
            <span className="font-semibold text-yellow-600">
              {data.results.filter(r => r.needs_review).length}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
