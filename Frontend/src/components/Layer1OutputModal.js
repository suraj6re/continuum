import { useState } from 'react';
import Button from './Button';
import Badge from './Badge';

export default function Layer1OutputModal({ drawingId, onClose }) {
  const [layer1Data, setLayer1Data] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('summary');

  useState(() => {
    fetchLayer1Output();
  }, [drawingId]);

  const fetchLayer1Output = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/upload/drawing/${drawingId}`);
      const result = await response.json();
      
      if (result.success) {
        setLayer1Data(result.data);
      } else {
        setError('Failed to load Layer 1 output');
      }
    } catch (err) {
      setError('Error fetching data: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const renderSummary = () => (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-bg-section p-4 rounded-lg">
          <p className="text-sm text-text-secondary mb-1">Pipeline Type</p>
          <p className="text-xl font-bold text-brand-charcoal">{layer1Data.pipeline_type || 'N/A'}</p>
        </div>
        <div className="bg-bg-section p-4 rounded-lg">
          <p className="text-sm text-text-secondary mb-1">Processing Status</p>
          <Badge variant={layer1Data.processed ? 'success' : 'warning'}>
            {layer1Data.processed ? 'Processed' : 'Processing'}
          </Badge>
        </div>
      </div>

      {layer1Data.entity_count && (
        <div className="bg-bg-section p-4 rounded-lg">
          <h4 className="font-semibold text-brand-charcoal mb-3">Entity Count</h4>
          <div className="grid grid-cols-3 gap-3">
            {Object.entries(layer1Data.entity_count).map(([type, count]) => (
              <div key={type} className="text-center p-2 bg-white rounded">
                <p className="text-2xl font-bold text-brand-orange">{count}</p>
                <p className="text-xs text-text-secondary">{type}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {layer1Data.bounding_box && (
        <div className="bg-bg-section p-4 rounded-lg">
          <h4 className="font-semibold text-brand-charcoal mb-3">Bounding Box</h4>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div><span className="text-text-secondary">Min X:</span> <span className="font-mono">{layer1Data.bounding_box.min_x?.toFixed(2)}</span></div>
            <div><span className="text-text-secondary">Max X:</span> <span className="font-mono">{layer1Data.bounding_box.max_x?.toFixed(2)}</span></div>
            <div><span className="text-text-secondary">Min Y:</span> <span className="font-mono">{layer1Data.bounding_box.min_y?.toFixed(2)}</span></div>
            <div><span className="text-text-secondary">Max Y:</span> <span className="font-mono">{layer1Data.bounding_box.max_y?.toFixed(2)}</span></div>
          </div>
        </div>
      )}

      {layer1Data.units && (
        <div className="bg-bg-section p-4 rounded-lg">
          <h4 className="font-semibold text-brand-charcoal mb-3">Units</h4>
          <div className="space-y-2 text-sm">
            <div><span className="text-text-secondary">Unit:</span> <span className="font-semibold">{layer1Data.units.unit}</span></div>
            <div><span className="text-text-secondary">Scale:</span> <span className="font-mono">{layer1Data.units.scale}</span></div>
          </div>
        </div>
      )}

      {layer1Data.layers && layer1Data.layers.length > 0 && (
        <div className="bg-bg-section p-4 rounded-lg">
          <h4 className="font-semibold text-brand-charcoal mb-3">Layers ({layer1Data.layers.length})</h4>
          <div className="flex flex-wrap gap-2">
            {layer1Data.layers.map((layer, idx) => (
              <Badge key={idx} variant="info">{layer}</Badge>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderText = () => (
    <div className="space-y-3">
      {layer1Data.text && layer1Data.text.length > 0 ? (
        <>
          <p className="text-sm text-text-secondary mb-3">Found {layer1Data.text.length} text entities</p>
          <div className="max-h-96 overflow-y-auto space-y-2">
            {layer1Data.text.map((textItem, idx) => (
              <div key={idx} className="bg-bg-section p-3 rounded-lg">
                <p className="font-semibold text-brand-charcoal mb-1">{textItem.text}</p>
                <div className="flex items-center space-x-4 text-xs text-text-secondary">
                  <span>Position: [{textItem.position[0]?.toFixed(2)}, {textItem.position[1]?.toFixed(2)}]</span>
                  <span>•</span>
                  <span>Layer: {textItem.layer}</span>
                </div>
              </div>
            ))}
          </div>
        </>
      ) : (
        <p className="text-center text-text-secondary py-8">No text entities found</p>
      )}
    </div>
  );

  const renderScale = () => (
    <div className="space-y-3">
      {layer1Data.scale_candidates && layer1Data.scale_candidates.length > 0 ? (
        <>
          <p className="text-sm text-text-secondary mb-3">Found {layer1Data.scale_candidates.length} scale candidate(s)</p>
          <div className="space-y-3">
            {layer1Data.scale_candidates.map((scale, idx) => (
              <div key={idx} className="bg-bg-section p-4 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <p className="font-semibold text-brand-charcoal">{scale.text}</p>
                  <Badge variant="success">{scale.parsed_value}</Badge>
                </div>
                <div className="text-xs text-text-secondary space-y-1">
                  <div>Position: [{scale.position[0]?.toFixed(2)}, {scale.position[1]?.toFixed(2)}]</div>
                  <div>Layer: {scale.layer}</div>
                </div>
              </div>
            ))}
          </div>
        </>
      ) : (
        <p className="text-center text-text-secondary py-8">No scale information detected</p>
      )}
    </div>
  );

  const renderGeometry = () => (
    <div className="space-y-3">
      {layer1Data.geometry ? (
        <div className="max-h-96 overflow-y-auto">
          {Object.entries(layer1Data.geometry).map(([type, entities]) => (
            <div key={type} className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold text-brand-charcoal">{type}</h4>
                <Badge variant="info">{entities.length} entities</Badge>
              </div>
              <div className="bg-bg-section p-3 rounded-lg">
                <pre className="text-xs overflow-x-auto">
                  {JSON.stringify(entities.slice(0, 3), null, 2)}
                </pre>
                {entities.length > 3 && (
                  <p className="text-xs text-text-secondary mt-2">... and {entities.length - 3} more</p>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-center text-text-secondary py-8">No geometry data available</p>
      )}
    </div>
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border-warm">
          <div>
            <h2 className="text-2xl font-bold text-brand-charcoal">Layer 1 Output</h2>
            <p className="text-sm text-text-secondary mt-1">Normalized Drawing Data</p>
          </div>
          <button
            onClick={onClose}
            className="text-text-secondary hover:text-brand-charcoal text-2xl font-bold w-8 h-8 flex items-center justify-center"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden flex flex-col">
          {loading ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-orange mx-auto mb-4"></div>
                <p className="text-text-secondary">Loading Layer 1 output...</p>
              </div>
            </div>
          ) : error ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <div className="text-6xl mb-4 text-red-600">✗</div>
                <p className="text-red-600">{error}</p>
              </div>
            </div>
          ) : (
            <>
              {/* Tabs */}
              <div className="flex border-b border-border-warm px-6">
                {['summary', 'text', 'scale', 'geometry'].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-4 py-3 font-semibold capitalize transition-colors ${
                      activeTab === tab
                        ? 'text-brand-orange border-b-2 border-brand-orange'
                        : 'text-text-secondary hover:text-brand-charcoal'
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              {/* Tab Content */}
              <div className="flex-1 overflow-y-auto p-6">
                {activeTab === 'summary' && renderSummary()}
                {activeTab === 'text' && renderText()}
                {activeTab === 'scale' && renderScale()}
                {activeTab === 'geometry' && renderGeometry()}
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end space-x-3 p-6 border-t border-border-warm">
          {layer1Data?.intermediate_json && (
            <Button variant="outline" onClick={() => window.open(layer1Data.intermediate_json, '_blank')}>
              Download JSON
            </Button>
          )}
          <Button onClick={onClose}>Close</Button>
        </div>
      </div>
    </div>
  );
}
