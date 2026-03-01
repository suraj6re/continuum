import { useState, useEffect } from 'react';
import Card from '../components/Card';
import Badge from '../components/Badge';
import { getAllDrawings } from '../services/api';

export default function Overview() {
  const [currentDrawing, setCurrentDrawing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState([
    { label: 'File Size', value: '--', change: '--'},
    { label: 'File Type', value: '--', change: '--'},
    { label: 'Processing Status', value: '--', change: '--'},
    { label: 'Confidence', value: '--', change: '--'},
  ]);

  useEffect(() => {
    loadCurrentDrawing();
  }, []);

  const loadCurrentDrawing = async () => {
    try {
      const response = await getAllDrawings();
      const drawingsData = response.data || [];
      
      // Get the most recently uploaded file (current file)
      if (drawingsData.length > 0) {
        const latestDrawing = drawingsData[0]; // Assuming API returns sorted by upload date desc
        setCurrentDrawing(latestDrawing);
        
        // Calculate stats for current file only
        const fileSize = (latestDrawing.file_size / 1024 / 1024).toFixed(2) + ' MB';
        const fileType = latestDrawing.file_type || 'Unknown';
        const status = latestDrawing.status === 'processed' ? 'Completed' : 
                      latestDrawing.status === 'processing' ? 'Processing' : 'Error';
        
        // Get confidence from Layer 5 data
        const confidence = latestDrawing.layer5_data?.summary?.avg_confidence 
          ? Math.round(latestDrawing.layer5_data.summary.avg_confidence * 100) + '%'
          : '--';
        
        setStats([
          { label: 'File Size', value: fileSize, change: '--'},
          { label: 'File Type', value: fileType, change: '--'},
          { label: 'Processing Status', value: status, change: '--'},
          { label: 'Confidence', value: confidence, change: '--'},
        ]);
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Failed to load current drawing:', err);
      setLoading(false);
    }
  };

  const fileDetails = currentDrawing ? [
    { label: 'Filename', value: currentDrawing.original_filename || currentDrawing.filename },
    { label: 'Uploaded', value: new Date(currentDrawing.uploaded_at).toLocaleString() },
    { label: 'Pipeline Type', value: currentDrawing.pipeline_type || '--' },
    { label: 'Entity Count', value: currentDrawing.entity_count || '--' },
    { label: 'Layer 2 Processed', value: currentDrawing.layer2_processed ? 'Yes' : 'No' },
    { label: 'Layer 3 Processed', value: currentDrawing.layer3_processed ? 'Yes' : 'No' },
    { label: 'Layer 4 Processed', value: currentDrawing.layer4_processed ? 'Yes' : 'No' },
    { label: 'Layer 5 Processed', value: currentDrawing.layer5_processed ? 'Yes' : 'No' },
  ] : [];

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-brand-charcoal mb-2">Overview</h1>
        <p className="text-text-secondary">Current file analysis dashboard</p>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-orange mx-auto"></div>
          <p className="text-text-secondary mt-4">Loading current file...</p>
        </div>
      ) : currentDrawing ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {stats.map((stat, idx) => (
              <Card key={idx}>
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-text-secondary text-sm mb-1">{stat.label}</p>
                    <p className="text-3xl font-bold text-brand-charcoal">{stat.value}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          <Card title="Current File Details">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {fileDetails.map((detail, idx) => (
                <div key={idx} className="flex justify-between items-center p-3 bg-bg-section rounded-lg">
                  <span className="text-text-secondary text-sm">{detail.label}</span>
                  <span className="font-semibold text-brand-charcoal">{detail.value}</span>
                </div>
              ))}
            </div>
          </Card>

          {currentDrawing.layer5_data && (
            <Card title="Layer 5 Summary" className="mt-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-bg-section rounded-lg">
                  <p className="text-text-secondary text-sm mb-1">Total Elements</p>
                  <p className="text-2xl font-bold text-brand-charcoal">
                    {currentDrawing.layer5_data.summary?.total_elements || 0}
                  </p>
                </div>
                <div className="p-4 bg-bg-section rounded-lg">
                  <p className="text-text-secondary text-sm mb-1">Total Relationships</p>
                  <p className="text-2xl font-bold text-brand-charcoal">
                    {currentDrawing.layer5_data.summary?.total_relationships || 0}
                  </p>
                </div>
                <div className="p-4 bg-bg-section rounded-lg">
                  <p className="text-text-secondary text-sm mb-1">Validation Status</p>
                  <Badge variant={currentDrawing.layer5_data.summary?.valid ? 'success' : 'error'}>
                    {currentDrawing.layer5_data.summary?.valid ? 'Valid' : 'Invalid'}
                  </Badge>
                </div>
              </div>
            </Card>
          )}
        </>
      ) : (
        <Card>
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📁</div>
            <h3 className="text-xl font-semibold text-brand-charcoal mb-2">No File Uploaded</h3>
            <p className="text-text-secondary">Upload a drawing to see its analysis</p>
          </div>
        </Card>
      )}
    </div>
  );
}
