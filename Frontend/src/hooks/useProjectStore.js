import { createContext, useContext, useState } from 'react';

const ProjectContext = createContext();

export const ProjectProvider = ({ children }) => {
  const [currentProjectId, setCurrentProjectId] = useState(null);
  const [qtoSummary, setQtoSummary] = useState(null);
  const [qtoElements, setQtoElements] = useState([]);
  const [processingStatus, setProcessingStatus] = useState('idle');

  const updateQTOData = (data) => {
    setCurrentProjectId(data.project_id);
    setQtoSummary(data.summary);
    setQtoElements(data.elements || []);
    setProcessingStatus('complete');
  };

  const startProcessing = () => {
    setProcessingStatus('processing');
  };

  const setError = () => {
    setProcessingStatus('error');
  };

  const reset = () => {
    setCurrentProjectId(null);
    setQtoSummary(null);
    setQtoElements([]);
    setProcessingStatus('idle');
  };

  return (
    <ProjectContext.Provider value={{
      currentProjectId,
      qtoSummary,
      qtoElements,
      processingStatus,
      updateQTOData,
      startProcessing,
      setError,
      reset
    }}>
      {children}
    </ProjectContext.Provider>
  );
};

export const useProjectStore = () => {
  const context = useContext(ProjectContext);
  if (!context) {
    throw new Error('useProjectStore must be used within ProjectProvider');
  }
  return context;
};
