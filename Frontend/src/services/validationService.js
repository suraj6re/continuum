const API_BASE_URL = 'http://localhost:8000';

export const fetchValidationData = async (drawingId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/upload/drawing/${drawingId}/layer6`);
    if (!response.ok) throw new Error('Backend not available');
    const result = await response.json();
    if (result.success && result.data) {
      return result.data;
    }
    throw new Error('Invalid response');
  } catch (error) {
    console.error('Failed to fetch validation data:', error);
    return null;
  }
};
