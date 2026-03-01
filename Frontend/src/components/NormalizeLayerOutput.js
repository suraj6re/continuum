import Badge from './Badge';
import { useState, useEffect } from 'react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export default function NormalizeLayerOutput({ data }) {
  const [preprocessedImageUrl, setPreprocessedImageUrl] = useState(null);
  const [showImage, setShowImage] = useState(false);

  useEffect(() => {
    // Check if this is a raster image with preprocessing
    if (data && data.id && data.preprocessed_image_path) {
      setPreprocessedImageUrl(`${API_BASE_URL}/api/upload/drawing/${data.id}/preprocessed-image`);
      setShowImage(true);
    } else {
      setShowImage(false);
    }
  }, [data]);

  if (!data) {
    return (
      <div className="mt-6 p-8 bg-bg-section rounded-lg text-center">
        <p className="text-text-secondary">No Layer 1 data available</p>
      </div>
    );
  }

  return (
    <div className="mt-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-brand-charcoal">Layer 1 — File Normalization Output</h3>
        <Badge variant="success">{data.pipeline_type?.toUpperCase() || 'PROCESSED'}</Badge>
      </div>

      {showImage && preprocessedImageUrl && (
        <div className="bg-white rounded-lg border border-border-warm p-4 mb-4">
          <h4 className="text-lg font-semibold text-brand-charcoal mb-3">Preprocessed Image</h4>
          <div className="flex justify-center bg-gray-50 p-4 rounded">
            <img 
              src={preprocessedImageUrl} 
              alt="Preprocessed drawing" 
              className="max-w-full h-auto border border-gray-300 rounded"
              style={{ maxHeight: '600px' }}
            />
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg border border-border-warm p-4">
        <h4 className="text-lg font-semibold text-brand-charcoal mb-3">Raw Data</h4>
        <pre className="text-xs overflow-auto max-h-[600px] bg-gray-50 p-4 rounded">
          {JSON.stringify(data, null, 2)}
        </pre>
      </div>
    </div>
  );
}
