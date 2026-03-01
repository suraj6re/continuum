import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadDrawing = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/api/upload/drawing', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const getAllDrawings = async () => {
  const response = await api.get('/api/upload/drawings');
  return response.data;
};

export const getDrawing = async (drawingId) => {
  const response = await api.get(`/api/upload/drawing/${drawingId}`);
  return response.data;
};

export const getLayer2Data = async (drawingId) => {
  const response = await api.get(`/api/upload/drawing/${drawingId}/layer2`);
  return response.data;
};

export const getLayer3Data = async (drawingId) => {
  const response = await api.get(`/api/upload/drawing/${drawingId}/layer3`);
  return response.data;
};

export const getLayer4Data = async (drawingId) => {
  const response = await api.get(`/api/upload/drawing/${drawingId}/layer4`);
  return response.data;
};

export const getLayer5Data = async (drawingId) => {
  const response = await api.get(`/api/upload/drawing/${drawingId}/layer5`);
  return response.data;
};

export const getLayer6Data = async (drawingId) => {
  const response = await api.get(`/api/upload/drawing/${drawingId}/layer6`);
  return response.data;
};

export default api;
