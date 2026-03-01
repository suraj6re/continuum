import { useState, useEffect } from 'react';
import Card from '../components/Card';
import Badge from '../components/Badge';
import { getAllDrawings } from '../services/api';

export default function Overview() {
  const [drawings, setDrawings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState([
    { label: 'Active Projects', value: '0', change: '--'},
    { label: 'Total Drawings', value: '0', change: '--'},
    { label: 'Processed Files', value: '0', change: '--'},
    { label: 'Avg Confidence', value: '--', change: '--'},
  ]);

  useEffect(() => {
    loadDrawings();
  }, []);

  const loadDrawings = async () => {
    try {
      const response = await getAllDrawings();
      const drawingsData = response.data || [];
      setDrawings(drawingsData);
      
      // Calculate real stats
      const totalDrawings = drawingsData.length;
      const processedDrawings = drawingsData.filter(d => d.processed).length;
      const processingDrawings = drawingsData.filter(d => d.status === 'processing').length;
      
      // Calculate average confidence from Layer 5 data
      let totalConfidence = 0;
      let confidenceCount = 0;
      drawingsData.forEach(drawing => {
        if (drawing.layer5_data && drawing.layer5_data.summary && drawing.layer5_data.summary.avg_confidence) {
          totalConfidence += drawing.layer5_data.summary.avg_confidence;
          confidenceCount++;
        }
      });
      const avgConfidence = confidenceCount > 0 ? (totalConfidence / confidenceCount).toFixed(0) : '--';
      
      setStats([
        { label: 'Active Projects', value: processingDrawings.toString(), change: '--'},
        { label: 'Total Drawings', value: totalDrawings.toString(), change: '--'},
        { label: 'Processed Files', value: processedDrawings.toString(), change: `${totalDrawings > 0 ? ((processedDrawings/totalDrawings)*100).toFixed(0) : 0}%`},
        { label: 'Avg Confidence', value: avgConfidence !== '--' ? `${avgConfidence}%` : '--', change: '--'},
      ]);
      
      setLoading(false);
    } catch (err) {
      console.error('Failed to load drawings:', err);
      setLoading(false);
    }
  };

  const recentProjects = drawings.slice(0, 5).map(drawing => ({
    name: drawing.original_filename || drawing.filename,
    status: drawing.status === 'processed' ? 'Completed' : drawing.status === 'processing' ? 'In Progress' : 'Error',
    confidence: drawing.layer5_data?.summary?.avg_confidence ? Math.round(drawing.layer5_data.summary.avg_confidence * 100) : '--',
    date: new Date(drawing.uploaded_at).toLocaleDateString(),
    id: drawing.id
  }));

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-brand-charcoal mb-2">Overview</h1>
        <p className="text-text-secondary">Your construction intelligence dashboard</p>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-orange mx-auto"></div>
          <p className="text-text-secondary mt-4">Loading dashboard...</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {stats.map((stat, idx) => (
              <Card key={idx}>
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-text-secondary text-sm mb-1">{stat.label}</p>
                    <p className="text-3xl font-bold text-brand-charcoal">{stat.value}</p>
                    <p className="text-emerald-600 text-sm mt-1">{stat.change}</p>
                  </div>
                  <div className="text-3xl">{stat.icon}</div>
                </div>
              </Card>
            ))}
          </div>

          {recentProjects.length > 0 ? (
            <Card title="Recent Drawings">
              <div className="space-y-4">
                {recentProjects.map((project, idx) => (
                  <div key={idx} className="flex items-center justify-between p-4 bg-bg-section rounded-lg">
                    <div className="flex-1">
                      <h4 className="font-semibold text-brand-charcoal">{project.name}</h4>
                      <p className="text-sm text-text-secondary">{project.date}</p>
                    </div>
                    <div className="flex items-center space-x-4">
                      <Badge variant={project.status === 'Completed' ? 'success' : project.status === 'In Progress' ? 'warning' : 'error'}>
                        {project.status}
                      </Badge>
                      <div className="text-right">
                        <p className="text-sm text-text-secondary">Confidence</p>
                        <p className="font-semibold text-brand-orange">{project.confidence !== '--' ? `${project.confidence}%` : '--'}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          ) : (
            <Card title="Recent Drawings">
              <div className="text-center py-12">
                <div className="text-6xl mb-4">📁</div>
                <h3 className="text-xl font-semibold text-brand-charcoal mb-2">No Drawings Yet</h3>
                <p className="text-text-secondary">Upload your first drawing to get started</p>
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
