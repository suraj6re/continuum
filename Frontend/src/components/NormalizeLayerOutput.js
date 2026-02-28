import Badge from './Badge';

export default function NormalizeLayerOutput({ data }) {
  if (!data) {
    return (
      <div className="mt-6 p-8 bg-bg-section rounded-lg text-center">
        <p className="text-text-secondary">No Layer 1 data available</p>
      </div>
    );
  }

  const isRaster = data.pipeline_type === 'raster';
  const isVector = data.pipeline_type === 'vector';

  return (
    <div className="mt-6 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold text-brand-charcoal">Layer 1 — File Normalization Output</h3>
        <Badge variant="success">{data.pipeline_type?.toUpperCase()}</Badge>
      </div>

      {isRaster && (
        <>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white p-4 rounded-lg border border-border-warm">
              <p className="text-sm text-text-secondary mb-1">File Type</p>
              <p className="text-lg font-semibold text-brand-charcoal">{data.file_type || 'Raster Image'}</p>
            </div>
            <div className="bg-white p-4 rounded-lg border border-border-warm">
              <p className="text-sm text-text-secondary mb-1">Detected Scale</p>
              <p className="text-lg font-semibold text-brand-charcoal">{data.detected_scale || 'N/A'}</p>
            </div>
            <div className="bg-white p-4 rounded-lg border border-border-warm">
              <p className="text-sm text-text-secondary mb-1">Pixel-to-Meter Ratio</p>
              <p className="text-lg font-semibold text-brand-charcoal">{data.pixel_to_meter_ratio?.toFixed(4) || 'N/A'}</p>
            </div>
            <div className="bg-white p-4 rounded-lg border border-border-warm">
              <p className="text-sm text-text-secondary mb-1">Bounding Box</p>
              <p className="text-sm font-mono text-brand-charcoal">
                {data.bounding_box ? `[${data.bounding_box.min_x}, ${data.bounding_box.min_y}] - [${data.bounding_box.max_x}, ${data.bounding_box.max_y}]` : 'N/A'}
              </p>
            </div>
          </div>

          {data.processed_images && (
            <div className="bg-white p-6 rounded-lg border border-border-warm">
              <h4 className="font-semibold text-brand-charcoal mb-4">Processed Images</h4>
              <div className="grid grid-cols-3 gap-4">
                {Object.entries(data.processed_images).map(([key, value]) => (
                  <div key={key} className="text-center">
                    <div className="bg-bg-section rounded-lg p-4 mb-2 h-32 flex items-center justify-center">
                      <span className="text-text-muted text-sm">Image: {key}</span>
                    </div>
                    <p className="text-sm font-medium text-brand-charcoal capitalize">{key.replace('_', ' ')}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {isVector && (
        <>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-lg border border-border-warm">
              <p className="text-sm text-text-secondary mb-1">Units</p>
              <p className="text-lg font-semibold text-brand-charcoal">{data.units?.unit || 'N/A'}</p>
            </div>
            <div className="bg-white p-4 rounded-lg border border-border-warm">
              <p className="text-sm text-text-secondary mb-1">Scale Factor</p>
              <p className="text-lg font-semibold text-brand-charcoal">{data.units?.scale || 'N/A'}</p>
            </div>
            <div className="bg-white p-4 rounded-lg border border-border-warm">
              <p className="text-sm text-text-secondary mb-1">Bounding Box</p>
              <p className="text-xs font-mono text-brand-charcoal">
                {data.bounding_box ? `[${data.bounding_box.min_x?.toFixed(2)}, ${data.bounding_box.min_y?.toFixed(2)}] - [${data.bounding_box.max_x?.toFixed(2)}, ${data.bounding_box.max_y?.toFixed(2)}]` : 'N/A'}
              </p>
            </div>
          </div>

          {data.entity_count && (
            <div className="bg-white p-6 rounded-lg border border-border-warm">
              <h4 className="font-semibold text-brand-charcoal mb-4">Entity Count Summary</h4>
              <div className="grid grid-cols-4 gap-4">
                {Object.entries(data.entity_count).map(([type, count]) => (
                  <div key={type} className="text-center p-4 bg-bg-section rounded-lg">
                    <p className="text-3xl font-bold text-brand-orange">{count}</p>
                    <p className="text-sm text-text-secondary mt-1">{type}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {data.layers && data.layers.length > 0 && (
            <div className="bg-white p-6 rounded-lg border border-border-warm">
              <h4 className="font-semibold text-brand-charcoal mb-4">Layer List ({data.layers.length})</h4>
              <div className="flex flex-wrap gap-2">
                {data.layers.map((layer, idx) => (
                  <Badge key={idx} variant="info">{layer}</Badge>
                ))}
              </div>
            </div>
          )}

          {data.text && data.text.length > 0 && (
            <div className="bg-white p-6 rounded-lg border border-border-warm">
              <h4 className="font-semibold text-brand-charcoal mb-4">Text Entities ({data.text.length})</h4>
              <div className="max-h-64 overflow-y-auto space-y-2">
                {data.text.slice(0, 10).map((textItem, idx) => (
                  <div key={idx} className="p-3 bg-bg-section rounded-lg">
                    <p className="font-medium text-brand-charcoal">{textItem.text}</p>
                    <p className="text-xs text-text-secondary mt-1">
                      Position: [{textItem.position[0]?.toFixed(2)}, {textItem.position[1]?.toFixed(2)}] • Layer: {textItem.layer}
                    </p>
                  </div>
                ))}
                {data.text.length > 10 && (
                  <p className="text-sm text-text-secondary text-center pt-2">... and {data.text.length - 10} more</p>
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
