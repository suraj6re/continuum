import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const fetchQTOData = async (drawingId) => {
  const response = await axios.get(`${API_BASE_URL}/api/upload/drawing/${drawingId}/layer4`);
  
  if (!response.data.success) {
    throw new Error('Failed to fetch QTO data');
  }

  const layer4Data = response.data.data;
  
  // Transform to expected format
  return {
    project_id: drawingId,
    summary: {
      total_elements: layer4Data.measurements?.length || 0,
      average_confidence: layer4Data.statistics?.measurements?.quality?.average_confidence || 0,
      high_confidence: layer4Data.measurements?.filter(m => m.confidence >= 0.95).length || 0,
      needs_review: layer4Data.measurements?.filter(m => m.confidence < 0.90).length || 0
    },
    elements: (layer4Data.measurements || []).map(m => ({
      id: m.element_id,
      name: `${m.type}`,
      quantity: m.measurements?.volume || m.measurements?.area || m.measurements?.count || 0,
      unit: m.measurements?.volume ? 'm³' : m.measurements?.area ? 'm²' : 'count',
      category: m.type,
      confidence: m.confidence || 0
    }))
  };
};

export const exportQTOToCSV = (elements) => {
  const headers = ['Element', 'Quantity', 'Unit', 'Category', 'Confidence'];
  const rows = elements.map(e => [
    e.name,
    e.quantity,
    e.unit,
    e.category,
    (e.confidence * 100).toFixed(1) + '%'
  ]);
  
  const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `qto_export_${Date.now()}.csv`;
  a.click();
  URL.revokeObjectURL(url);
};

export const exportQTOToJSON = (data) => {
  const json = JSON.stringify(data, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `qto_export_${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
};
