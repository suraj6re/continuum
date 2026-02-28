import { useState, useEffect } from 'react';
import Badge from './Badge';

export default function Layer3OutputModal({ drawingId, onClose }) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('elements');

  useEffect(() => {
    fetchLayer3Output();
  }, [drawingId]);

  const fetchLayer3Output = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/analysis/drawing/${drawingId}`);
      const result = await response.json();
      
      if (result.success) {
        setData(result.data.layer3_output);
      } else {
        setError('Failed to load analysis');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getTypeColor = (type) => {
    const colors = {
      'Wall': 'bg-blue-100 text-blue-800',
      'Slab': 'bg-green-100 text-green-800',
      'Column': 'bg-purple-100 text-purple-800',
      'Door': 'bg-yellow-100 text-yellow-800',
      'Window': 'bg-cyan-100 text-cyan-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  const getConfidenceBadge = (confidence) => {
    if (confidence >= 0.8) return <Badge variant="success">{(confidence * 100).toFixed(0)}%</Badge>;
    if (confidence >= 0.6) return <Badge variant="warning">{(confidence * 100).toFixed(0)}%</Badge>;
    return <Badge variant="danger">{(confidence * 100).toFixed(0)}%</Badge>;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div className="p-6 border-b border-border-warm flex justify-between items-center">
          <h2 className="text-2xl font-bold text-brand-charcoal">Structural Analysis Results</h2>
          <button onClick={onClose} className="text-text-secondary hover:text-brand-charcoal text-2xl">&times;</button>
        </div>

        {loading && (
          <div className="flex-1 flex items-center justify-center p-12">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-orange mx-auto mb-4"></div>
              <p className="text-text-secondary">Analyzing drawing...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="flex-1 flex items-center justify-center p-12">
            <div className="text-center">
              <p className="text-red-600 mb-4">{error}</p>
              <button onClick={onClose} className="px-4 py-2 bg-brand-orange text-white rounded-lg">Close</button>
            </div>
          </div>
        )}

        {data && (
          <>
            <div className="p-6 bg-bg-section border-b border-border-warm">
              <div className="grid grid-cols-5 gap-4">
                <div className="text-center">
                  <div className="text-3xl font-bold text-brand-charcoal">{data.summary.total_walls}</div>
                  <div className="text-sm text-text-secondary">Walls</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-brand-charcoal">{data.summary.total_slabs}</div>
                  <div className="text-sm text-text-secondary">Slabs</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-brand-charcoal">{data.summary.total_columns}</div>
                  <div className="text-sm text-text-secondary">Columns</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-brand-charcoal">{data.summary.total_doors}</div>
                  <div className="text-sm text-text-secondary">Doors</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-brand-charcoal">{data.summary.total_windows}</div>
                  <div className="text-sm text-text-secondary">Windows</div>
                </div>
              </div>
              <div className="mt-4 flex justify-center space-x-6">
                <div className="text-center">
                  <span className="text-sm text-text-secondary">Avg Confidence: </span>
                  <span className="font-semibold text-brand-charcoal">{(data.summary.avg_confidence * 100).toFixed(0)}%</span>
                </div>
                <div className="text-center">
                  <span className="text-sm text-text-secondary">Flagged: </span>
                  <span className="font-semibold text-brand-charcoal">{data.summary.flagged_count}</span>
                </div>
              </div>
            </div>

            <div className="border-b border-border-warm">
              <div className="flex space-x-1 p-2">
                <button onClick={() => setActiveTab('elements')} className={`px-4 py-2 rounded-lg ${activeTab === 'elements' ? 'bg-brand-orange text-white' : 'text-text-secondary hover:bg-bg-section'}`}>
                  Elements ({data.elements.length})
                </button>
                <button onClick={() => setActiveTab('relationships')} className={`px-4 py-2 rounded-lg ${activeTab === 'relationships' ? 'bg-brand-orange text-white' : 'text-text-secondary hover:bg-bg-section'}`}>
                  Relationships ({data.relationships.length})
                </button>
                {data.flagged_for_review?.length > 0 && (
                  <button onClick={() => setActiveTab('flagged')} className={`px-4 py-2 rounded-lg ${activeTab === 'flagged' ? 'bg-brand-orange text-white' : 'text-text-secondary hover:bg-bg-section'}`}>
                    Flagged ({data.flagged_for_review.length})
                  </button>
                )}
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              {activeTab === 'elements' && (
                <div className="space-y-3">
                  {data.elements.map((elem) => (
                    <div key={elem.id} className="p-4 bg-bg-section rounded-lg border border-border-warm">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-3">
                          <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getTypeColor(elem.type)}`}>
                            {elem.type}
                          </span>
                          <span className="text-sm text-text-secondary">{elem.id}</span>
                        </div>
                        {getConfidenceBadge(elem.confidence)}
                      </div>
                      <div className="grid grid-cols-4 gap-4 text-sm">
                        {elem.length && <div><span className="text-text-secondary">Length:</span> <span className="font-semibold">{elem.length}m</span></div>}
                        {elem.thickness && <div><span className="text-text-secondary">Thickness:</span> <span className="font-semibold">{elem.thickness}m</span></div>}
                        {elem.width && <div><span className="text-text-secondary">Width:</span> <span className="font-semibold">{elem.width}m</span></div>}
                        {elem.height && <div><span className="text-text-secondary">Height:</span> <span className="font-semibold">{elem.height}m</span></div>}
                        {elem.area && <div><span className="text-text-secondary">Area:</span> <span className="font-semibold">{elem.area}m²</span></div>}
                        {elem.material && <div><span className="text-text-secondary">Material:</span> <span className="font-semibold">{elem.material}</span></div>}
                        {elem.code && <div><span className="text-text-secondary">Code:</span> <span className="font-semibold">{elem.code}</span></div>}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {activeTab === 'relationships' && (
                <div className="space-y-2">
                  {data.relationships.map((rel, idx) => (
                    <div key={idx} className="p-3 bg-bg-section rounded-lg border border-border-warm flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <span className="text-sm font-mono text-brand-charcoal">{rel.source}</span>
                        <span className="text-brand-orange">→</span>
                        <span className="text-sm font-mono text-brand-charcoal">{rel.target}</span>
                      </div>
                      <Badge>{rel.type}</Badge>
                    </div>
                  ))}
                </div>
              )}

              {activeTab === 'flagged' && data.flagged_for_review && (
                <div className="space-y-3">
                  {data.flagged_for_review.map((item) => (
                    <div key={item.element_id} className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-mono text-sm">{item.element_id}</span>
                        <Badge variant="warning">{(item.confidence * 100).toFixed(0)}%</Badge>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {item.reasons.map((reason, idx) => (
                          <span key={idx} className="px-2 py-1 bg-yellow-200 text-yellow-800 rounded text-xs">
                            {reason.replace(/_/g, ' ')}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
