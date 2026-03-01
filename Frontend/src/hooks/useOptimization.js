import { useState, useMemo } from 'react';
import { calculateOptimization, calculateRiskLevel, OPTIMIZATION_MODES } from '../services/optimizationEngine';

export const useOptimization = (costSummary, scheduleSummary) => {
  const [mode, setMode] = useState(OPTIMIZATION_MODES.BALANCED);
  const [variables, setVariables] = useState({
    productivityMultiplier: 1.0,
    overtimeMultiplier: 1.0,
    resourceLevel: 'medium',
    priceVolatility: 1.0,
    crewMultiplier: 1.0
  });
  const [scenarios, setScenarios] = useState([]);

  const optimizationData = useMemo(() => {
    return calculateOptimization(costSummary, scheduleSummary, variables, mode);
  }, [costSummary, scheduleSummary, variables, mode]);

  const riskLevel = useMemo(() => {
    return calculateRiskLevel(variables);
  }, [variables]);

  const updateVariable = (key, value) => {
    setVariables(prev => ({ ...prev, [key]: value }));
  };

  const saveScenario = (name) => {
    if (!optimizationData) return;
    
    const scenario = {
      id: Date.now(),
      name,
      mode,
      variables: { ...variables },
      results: { ...optimizationData },
      risk: riskLevel
    };
    
    setScenarios(prev => [...prev, scenario]);
  };

  const removeScenario = (id) => {
    setScenarios(prev => prev.filter(s => s.id !== id));
  };

  const resetVariables = () => {
    setVariables({
      productivityMultiplier: 1.0,
      overtimeMultiplier: 1.0,
      resourceLevel: 'medium',
      priceVolatility: 1.0,
      crewMultiplier: 1.0
    });
  };

  return {
    mode,
    setMode,
    variables,
    updateVariable,
    resetVariables,
    optimizationData,
    riskLevel,
    scenarios,
    saveScenario,
    removeScenario
  };
};
