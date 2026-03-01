import { useState, useEffect, useMemo } from 'react';
import { analyzeValidation } from '../services/validationEngine';

export const useValidation = (qtoElements, costItems, processingStatus) => {
  const [validationData, setValidationData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (processingStatus === 'complete' && qtoElements.length > 0) {
      setLoading(true);
      setTimeout(() => {
        const data = analyzeValidation(qtoElements, costItems);
        setValidationData(data);
        setLoading(false);
      }, 500);
    }
  }, [qtoElements, costItems, processingStatus]);

  const updateElementApproval = (elementId, approvalStatus) => {
    if (!validationData) return;
    
    const updatedElements = validationData.elements.map(e => 
      (e.id || e.element_id) === elementId ? { ...e, approval_status: approvalStatus } : e
    );
    
    const validated = updatedElements.filter(e => e.approval_status === 'approved').length;
    const userCorrected = updatedElements.filter(e => e.user_corrected).length;
    const coverage = ((validated + userCorrected) / updatedElements.length) * 100;
    
    setValidationData({
      ...validationData,
      elements: updatedElements,
      metrics: {
        ...validationData.metrics,
        validated,
        coverage_percent: coverage
      }
    });
  };

  const updateElementOverride = (elementId, overrideQuantity, notes) => {
    if (!validationData) return;
    
    const updatedElements = validationData.elements.map(e => 
      (e.id || e.element_id) === elementId 
        ? { ...e, override_quantity: overrideQuantity, notes, user_corrected: true, approval_status: 'user_corrected' } 
        : e
    );
    
    const validated = updatedElements.filter(e => e.approval_status === 'approved').length;
    const userCorrected = updatedElements.filter(e => e.user_corrected).length;
    const coverage = ((validated + userCorrected) / updatedElements.length) * 100;
    
    setValidationData({
      ...validationData,
      elements: updatedElements,
      metrics: {
        ...validationData.metrics,
        user_corrections: userCorrected,
        coverage_percent: coverage
      }
    });
  };

  const approveAllHighConfidence = () => {
    if (!validationData) return;
    
    const updatedElements = validationData.elements.map(e => 
      e.confidence >= 0.95 ? { ...e, approval_status: 'approved' } : e
    );
    
    const validated = updatedElements.filter(e => e.approval_status === 'approved').length;
    const userCorrected = updatedElements.filter(e => e.user_corrected).length;
    const coverage = ((validated + userCorrected) / updatedElements.length) * 100;
    
    setValidationData({
      ...validationData,
      elements: updatedElements,
      metrics: {
        ...validationData.metrics,
        validated,
        coverage_percent: coverage
      }
    });
  };

  return {
    validationData,
    loading,
    updateElementApproval,
    updateElementOverride,
    approveAllHighConfidence
  };
};
