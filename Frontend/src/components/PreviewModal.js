import { useEffect, useState, useRef } from 'react';
import Button from './Button';
import Badge from './Badge';

export default function PreviewModal({ file, onClose }) {
  const [loading, setLoading] = useState(true);
  const containerRef = useRef(null);

  useEffect(() => {
    const ext = getFileExtension(file.name);
    
    if (ext === 'pdf') {
      loadPDF();
    } else {
      setLoading(false);
    }
  }, [file]);

  const getFileExtension = (filename) => {
    return filename.split('.').pop().toLowerCase();
  };

  const loadPDF = async () => {
    try {
      const pdfjsLib = await import('pdfjs-dist');
      pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;
      
      const pdf = await pdfjsLib.getDocument(file.previewUrl).promise;
      const container = containerRef.current;
      
      if (container) {
        container.innerHTML = '';
        
        for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber++) {
          const page = await pdf.getPage(pageNumber);
          const viewport = page.getViewport({ scale: 1.5 });
          
          const canvas = document.createElement('canvas');
          const context = canvas.getContext('2d');
          canvas.height = viewport.height;
          canvas.width = viewport.width;
          canvas.className = 'mb-4 mx-auto';
          
          await page.render({ canvasContext: context, viewport }).promise;
          container.appendChild(canvas);
        }
      }
      
      setLoading(false);
    } catch (err) {
      console.error('PDF load error:', err);
      setLoading(false);
    }
  };

  const renderPreview = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-orange mx-auto mb-4"></div>
            <p className="text-text-secondary">Loading preview...</p>
          </div>
        </div>
      );
    }

    const ext = getFileExtension(file.name);
    console.log('Preview URL:', file.previewUrl);
    console.log('File extension:', ext);

    if (['png', 'jpg', 'jpeg'].includes(ext)) {
      return (
        <img 
          src={file.previewUrl} 
          alt={file.name} 
          className="max-h-[70vh] w-auto mx-auto"
          onError={(e) => {
            console.error('Image load error:', e);
            e.target.style.display = 'none';
            e.target.parentElement.innerHTML = '<div class="text-center text-red-600">Failed to load image</div>';
          }}
        />
      );
    }

    if (ext === 'pdf') {
      return (
        <div ref={containerRef} className="max-h-[70vh] overflow-y-auto">
          {/* PDF pages will be rendered here */}
        </div>
      );
    }

    if (['dxf', 'dwg', 'cad'].includes(ext)) {
      return (
        <div className="flex flex-col items-center justify-center h-96 bg-bg-section rounded-lg">
          <div className="text-6xl mb-4">📐</div>
          <p className="text-lg font-semibold text-brand-charcoal mb-2">{file.name}</p>
          <p className="text-text-secondary">CAD Preview Not Available Yet</p>
        </div>
      );
    }

    return (
      <div className="flex items-center justify-center h-96 bg-bg-section rounded-lg">
        <p className="text-text-secondary">Preview not available for this file type</p>
      </div>
    );
  };

  if (!file) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50 backdrop-blur-sm animate-fadeIn"
      onClick={onClose}
    >
      <div 
        className="bg-bg-card rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden animate-slideUp"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-6 border-b border-border-warm">
          <div className="flex items-center space-x-4">
            <div>
              <h3 className="text-xl font-bold text-brand-charcoal">{file.name}</h3>
              <div className="flex items-center space-x-3 mt-1">
                <span className="text-sm text-text-secondary">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                <Badge variant="info">{file.type}</Badge>
              </div>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="text-text-secondary hover:text-brand-orange transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {renderPreview()}
        </div>
      </div>
    </div>
  );
}
