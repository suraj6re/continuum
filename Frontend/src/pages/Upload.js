import { useState } from 'react';
import Card from '../components/Card';
import UploadZone from '../components/UploadZone';
import Stepper from '../components/Stepper';
import Badge from '../components/Badge';
import Button from '../components/Button';
import { uploadDrawing } from '../services/api';

export default function Upload() {
  const [file, setFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [uploadData, setUploadData] = useState(null);
  const [error, setError] = useState(null);

  const steps = ['Upload', 'Normalize', 'Extract', 'Parse', 'QTO', 'Validate', 'Complete'];

  const handleFileSelect = async (selectedFile) => {
    setFile(selectedFile);
    setAnalyzing(true);
    setCurrentStep(1);
    setError(null);
    
    try {
      const response = await uploadDrawing(selectedFile);
      setUploadData(response.data);
      
      const interval = setInterval(() => {
        setCurrentStep(prev => {
          if (prev >= steps.length - 1) {
            clearInterval(interval);
            setAnalyzing(false);
            return prev;
          }
          return prev + 1;
        });
      }, 1500);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
      setAnalyzing(false);
      setFile(null);
    }
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
            <Button onClick={() => setError(null)}>Try Again</Button>
          </div>
        </Card>
      )}

      {!file && !error ? (
        <Card>
          <UploadZone onFileSelect={handleFileSelect} />
        </Card>
      ) : (
        <div className="space-y-6">
          <Card title="File Information">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-brand-orange rounded-lg flex items-center justify-center text-white text-xl">
                  📄
                </div>
                <div>
                  <p className="font-semibold text-brand-charcoal">{file.name}</p>
                  <p className="text-sm text-text-secondary">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              </div>
              <Badge variant={analyzing ? 'warning' : 'success'}>
                {analyzing ? 'Processing' : 'Complete'}
              </Badge>
            </div>
          </Card>

          <Card title="Analysis Progress">
            <Stepper steps={steps} currentStep={currentStep} />
          </Card>

          {!analyzing && (
            <Card title="Analysis Complete">
              <div className="text-center py-8">
                <div className="text-6xl mb-4">✓</div>
                <h3 className="text-2xl font-bold text-brand-charcoal mb-2">Drawing Processed Successfully</h3>
                <p className="text-text-secondary mb-6">Your drawing has been analyzed and quantities extracted</p>
                <div className="flex justify-center space-x-4">
                  <Button>View QTO Results</Button>
                  <Button variant="outline">View Cost Estimate</Button>
                </div>
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
