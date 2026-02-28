import { useState } from 'react';

export default function UploadZone({ onFileSelect }) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    if (onFileSelect) onFileSelect(files[0]);
  };

  const handleFileInput = (e) => {
    const files = Array.from(e.target.files);
    if (onFileSelect) onFileSelect(files[0]);
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors
        ${isDragging ? 'border-brand-orange bg-orange-50' : 'border-border-warm bg-bg-card'}`}
    >
      <div className="flex flex-col items-center">
        <svg className="w-16 h-16 text-text-muted mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <p className="text-lg font-medium text-text-primary mb-2">Drop your drawing here</p>
        <p className="text-sm text-text-secondary mb-4">or click to browse</p>
        <input
          type="file"
          onChange={handleFileInput}
          accept=".pdf,.dwg,.dxf,.png,.jpg"
          className="hidden"
          id="file-upload"
        />
        <label htmlFor="file-upload" className="px-6 py-3 bg-brand-orange text-white rounded-xl font-medium cursor-pointer hover:bg-[#C2410C] transition-colors">
          Select File
        </label>
        <p className="text-xs text-text-muted mt-4">Supports PDF, CAD, DWG, DXF, PNG, JPG</p>
      </div>
    </div>
  );
}
