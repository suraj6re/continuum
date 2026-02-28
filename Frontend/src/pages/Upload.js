import { useState, useEffect } from 'react';
import Card from '../components/Card';
import UploadZone from '../components/UploadZone';
import Stepper from '../components/Stepper';
import Badge from '../components/Badge';
import Button from '../components/Button';
import PreviewModal from '../components/PreviewModal';
import Layer1OutputModal from '../components/Layer1OutputModal';
import { uploadDrawing, getAllDrawings } from '../services/api';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export default function Upload() {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [currentUpload, setCurrentUpload] = useState(null);
  const [uploadedFileData, setUploadedFileData] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState(null);
  const [showUploadZone, setShowUploadZone] = useState(true);
  const [showPreview, setShowPreview] = useState(false);
  const [previewFile, setPreviewFile] = useState(null);
  const [showLayer1Output, setShowLayer1Output] = useState(false);
  const [selectedDrawingId, setSelectedDrawingId] = useState(null);

  const steps = ['Upload', 'Normalize', 'Extract', 'Parse', 'QTO', 'Validate', 'Complete'];

  useEffect(() => {
    loadUploadedFiles();
  }, []);

  const loadUploadedFiles = async () => {
    try {
      const response = await getAllDrawings();
      setUploadedFiles(response.data || []);
    } catch (err) {
      console.error('Failed to load files:', err);
    }
  };

  const getFileIcon = (fileType) => {
    const icons = {
      'PDF': '📄',
      'PNG': '🖼️',
      'JPG': '🖼️',
      'JPEG': '🖼️',
      'DWG': '📐',
      'DXF': '📐',
      'CAD': '📐'
    };
    return icons[fileType] || '📄';
  };

  const getFileType = (filename) => {
    const ext = filename.split('.').pop().toUpperCase();
    return ext;
  };

  const handleFileSelect = async (selectedFile) => {
    const fileType = getFileType(selectedFile.name);
    const previewUrl = URL.createObjectURL(selectedFile);
    
    const fileData = {
      name: selectedFile.name,
      size: selectedFile.size,
      type: fileType,
      previewUrl: previewUrl
    };
    
    setUploadedFileData(fileData);
    setCurrentUpload({ name: selectedFile.name, size: selectedFile.size });
    setAnalyzing(true);
    setCurrentStep(0);
    setError(null);
    setShowUploadZone(false);
    
    try {
      const response = await uploadDrawing(selectedFile);
      
      const interval = setInterval(() => {
        setCurrentStep(prev => {
          if (prev >= steps.length - 1) {
            clearInterval(interval);
            setAnalyzing(false);
            setCurrentUpload(null);
            loadUploadedFiles();
            return prev;
          }
          return prev + 1;
        });
      }, 800);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
      setAnalyzing(false);
      setCurrentUpload(null);
      setShowUploadZone(true);
      URL.revokeObjectURL(previewUrl);
      setUploadedFileData(null);
    }
  };

  const handleStepClick = () => {
    if (uploadedFileData) {
      setPreviewFile(uploadedFileData);
      setShowPreview(true);
    }
  };

  const handleViewPreviousFile = (file) => {
    const fileUrl = `${API_BASE_URL}/uploads/${file.filename}`;
    
    console.log('Opening preview for:', file.filename);
    console.log('Original filename:', file.original_filename);
    console.log('File URL:', fileUrl);
    
    const fileData = {
      name: file.original_filename || file.filename,
      size: file.file_size,
      type: file.file_type,
      previewUrl: fileUrl
    };
    
    setPreviewFile(fileData);
    setShowPreview(true);
  };

  const handleViewLayer1Output = (file) => {
    setSelectedDrawingId(file.id);
    setShowLayer1Output(true);
  };

  const handleCloseLayer1Output = () => {
    setShowLayer1Output(false);
    setSelectedDrawingId(null);
  };

  const handleClosePreview = () => {
    setShowPreview(false);
    if (previewFile && previewFile.previewUrl && previewFile.previewUrl.startsWith('blob:')) {
      URL.revokeObjectURL(previewFile.previewUrl);
    }
    setPreviewFile(null);
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-brand-charcoal mb-2">Upload Drawing</h1>
        <p className="text-text-secondary">Upload construction drawings for AI-powered analysis</p>
      </div>

      {error && (
        <Card>
          <div className="text-center py-8">
            <div className="text-6xl mb-4 text-red-600">✗</div>
            <h3 className="text-2xl font-bold text-red-600 mb-2">Upload Failed</h3>
            <p className="text-text-secondary mb-6">{error}</p>
            <Button onClick={() => { setError(null); setShowUploadZone(true); }}>Try Again</Button>
          </div>
        </Card>
      )}

      {showUploadZone ? (
        <Card>
          <UploadZone onFileSelect={handleFileSelect} />
        </Card>
      ) : (
        <Card title="Analysis Progress">
          <Stepper steps={steps} currentStep={currentStep} onStepClick={handleStepClick} />
          
          {currentUpload && currentStep === 0 && (
            <div className="mt-6 pt-6 border-t border-border-warm">
              <h4 className="text-sm font-semibold text-text-secondary mb-3">Uploaded Files</h4>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-4 bg-bg-section rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-brand-orange rounded-lg flex items-center justify-center text-white text-2xl">
                      📄
                    </div>
                    <div>
                      <p className="font-semibold text-brand-charcoal">{currentUpload.name}</p>
                      <p className="text-sm text-text-secondary">{(currentUpload.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                  </div>
                  <Badge variant="warning">Processing</Badge>
                </div>
              </div>
            </div>
          )}

          {!analyzing && (
            <div className="mt-6 text-center">
              <div className="text-6xl mb-4">✓</div>
              <h3 className="text-2xl font-bold text-brand-charcoal mb-2">Analysis Complete</h3>
              <p className="text-text-secondary mb-6">Drawing processed successfully</p>
              <div className="flex justify-center space-x-4">
                <Button onClick={() => setShowUploadZone(true)}>Upload Another</Button>
                <Button variant="outline">View Results</Button>
              </div>
            </div>
          )}
        </Card>
      )}

      {uploadedFiles.length > 0 && showUploadZone && (
        <Card title={`Previously Uploaded Files (${uploadedFiles.length})`} className="mt-6">
          <div className="space-y-3">
            {uploadedFiles.map((file) => (
              <div key={file.id} className="flex items-center justify-between p-4 bg-bg-section rounded-lg hover:shadow-md transition-shadow">
                <div className="flex items-center space-x-4 flex-1">
                  <div className="w-12 h-12 bg-brand-orange rounded-lg flex items-center justify-center text-white text-2xl">
                    {getFileIcon(file.file_type)}
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-brand-charcoal">{file.original_filename || file.filename}</p>
                    <div className="flex items-center space-x-4 mt-1">
                      <span className="text-sm text-text-secondary">{(file.file_size / 1024 / 1024).toFixed(2)} MB</span>
                      <span className="text-sm text-text-secondary">•</span>
                      <span className="text-sm text-text-secondary">{file.file_type}</span>
                      <span className="text-sm text-text-secondary">•</span>
                      <span className="text-sm text-text-secondary">{new Date(file.uploaded_at).toLocaleString()}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <Badge variant="success">{file.status}</Badge>
                  <Button size="sm" variant="outline" onClick={() => handleViewPreviousFile(file)}>View</Button>
                  <Button size="sm" onClick={() => handleViewLayer1Output(file)}>Normalize</Button>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {showPreview && previewFile && (
        <PreviewModal 
          file={previewFile} 
          onClose={handleClosePreview} 
        />
      )}

      {showLayer1Output && selectedDrawingId && (
        <Layer1OutputModal
          drawingId={selectedDrawingId}
          onClose={handleCloseLayer1Output}
        />
      )}
    </div>
  );
}
