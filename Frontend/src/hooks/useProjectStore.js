import { createContext, useContext, useState } from 'react';

const ProjectContext = createContext();

export const ProjectProvider = ({ children }) => {
  const [currentProjectId, setCurrentProjectId] = useState(null);
  const [qtoSummary, setQtoSummary] = useState(null);
  const [qtoElements, setQtoElements] = useState([]);
  const [processingStatus, setProcessingStatus] = useState('idle');
  const [costSummary, setCostSummary] = useState(null);
  const [costItems, setCostItems] = useState([]);
  const [pricingAdjustment, setPricingAdjustment] = useState(1.0);
  const [selectedSupplier, setSelectedSupplier] = useState(null);

  const updateQTOData = (data) => {
    setCurrentProjectId(data.project_id);
    setQtoSummary(data.summary);
    setQtoElements(data.elements || []);
    setProcessingStatus('complete');
  };

  const updateCostData = (data) => {
    setCostSummary(data.cost_summary);
    setCostItems(data.cost_items || []);
  };

  const updatePricingAdjustment = (factor) => {
    setPricingAdjustment(factor);
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
    setCostSummary(null);
    setCostItems([]);
    setPricingAdjustment(1.0);
    setSelectedSupplier(null);
  };

  return (
    <ProjectContext.Provider value={{
      currentProjectId,
      qtoSummary,
      qtoElements,
      processingStatus,
      costSummary,
      costItems,
      pricingAdjustment,
      selectedSupplier,
      updateQTOData,
      updateCostData,
      updatePricingAdjustment,
      setSelectedSupplier,
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
