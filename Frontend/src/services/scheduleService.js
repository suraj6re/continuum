const API_BASE_URL = 'http://localhost:8000';

export const fetchScheduleData = async (drawingId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/upload/drawing/${drawingId}/layer10`);
    if (!response.ok) throw new Error('Backend not available');
    const result = await response.json();
    if (result.success && result.data) {
      return result.data;
    }
    throw new Error('Invalid response');
  } catch (error) {
    console.error('Failed to fetch schedule data:', error);
    return null;
  }
};
