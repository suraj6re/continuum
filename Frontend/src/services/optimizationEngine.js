export const OPTIMIZATION_MODES = {
  MINIMIZE_DURATION: 'minimize_duration',
  MINIMIZE_COST: 'minimize_cost',
  BALANCED: 'balanced'
};

export const calculateOptimization = (costSummary, scheduleSummary, variables, mode) => {
  if (!costSummary || !scheduleSummary) {
    return null;
  }

  const {
    productivityMultiplier = 1.0,
    overtimeMultiplier = 1.0,
    resourceLevel = 'medium',
    priceVolatility = 1.0,
    crewMultiplier = 1.0
  } = variables;

  // Baseline values
  const baseDuration = scheduleSummary.total_duration || 0;
  const baseMaterialCost = costSummary.material_cost || 0;
  const baseLaborCost = costSummary.labor_cost || 0;
  const baseEquipmentCost = costSummary.equipment_cost || 0;
  const baseTotalCost = costSummary.total_cost || 0;

  // Apply optimization based on mode
  let optimizedDuration = baseDuration;
  let optimizedMaterialCost = baseMaterialCost;
  let optimizedLaborCost = baseLaborCost;
  let optimizedEquipmentCost = baseEquipmentCost;

  // Duration calculation
  optimizedDuration = Math.ceil(baseDuration / productivityMultiplier);

  // Material cost (affected by price volatility)
  optimizedMaterialCost = Math.round(baseMaterialCost * priceVolatility);

  // Labor cost (affected by crew size, overtime, and duration)
  const durationRatio = optimizedDuration / baseDuration;
  optimizedLaborCost = Math.round(
    baseLaborCost * crewMultiplier * overtimeMultiplier * (1 + (1 - durationRatio) * 0.3)
  );

  // Equipment cost (affected by duration)
  optimizedEquipmentCost = Math.round(baseEquipmentCost * durationRatio * 1.1);

  // Apply mode-specific adjustments
  if (mode === OPTIMIZATION_MODES.MINIMIZE_DURATION) {
    optimizedDuration = Math.ceil(optimizedDuration * 0.85);
    optimizedLaborCost = Math.round(optimizedLaborCost * 1.25);
    optimizedEquipmentCost = Math.round(optimizedEquipmentCost * 1.15);
  } else if (mode === OPTIMIZATION_MODES.MINIMIZE_COST) {
    optimizedDuration = Math.ceil(optimizedDuration * 1.1);
    optimizedLaborCost = Math.round(optimizedLaborCost * 0.9);
    optimizedEquipmentCost = Math.round(optimizedEquipmentCost * 0.95);
  }

  // Resource level impact
  const resourceMultipliers = {
    low: { duration: 1.2, cost: 0.85 },
    medium: { duration: 1.0, cost: 1.0 },
    high: { duration: 0.85, cost: 1.2 }
  };
  const resourceImpact = resourceMultipliers[resourceLevel] || resourceMultipliers.medium;
  optimizedDuration = Math.ceil(optimizedDuration * resourceImpact.duration);
  optimizedLaborCost = Math.round(optimizedLaborCost * resourceImpact.cost);

  const optimizedTotalCost = optimizedMaterialCost + optimizedLaborCost + optimizedEquipmentCost;

  // Calculate differences
  const durationDiff = baseDuration - optimizedDuration;
  const durationDiffPct = ((durationDiff / baseDuration) * 100).toFixed(1);
  const costDiff = baseTotalCost - optimizedTotalCost;
  const costDiffPct = ((costDiff / baseTotalCost) * 100).toFixed(1);

  // Calculate efficiency score
  const efficiencyScore = durationDiffPct > 0 && costDiffPct < 0
    ? (Math.abs(parseFloat(durationDiffPct)) / Math.abs(parseFloat(costDiffPct))).toFixed(2)
    : 0;

  return {
    baseline: {
      duration: baseDuration,
      material_cost: baseMaterialCost,
      labor_cost: baseLaborCost,
      equipment_cost: baseEquipmentCost,
      total_cost: baseTotalCost
    },
    optimized: {
      duration: optimizedDuration,
      material_cost: optimizedMaterialCost,
      labor_cost: optimizedLaborCost,
      equipment_cost: optimizedEquipmentCost,
      total_cost: optimizedTotalCost
    },
    differences: {
      duration_diff: durationDiff,
      duration_diff_pct: parseFloat(durationDiffPct),
      cost_diff: costDiff,
      cost_diff_pct: parseFloat(costDiffPct),
      efficiency_score: parseFloat(efficiencyScore)
    }
  };
};

export const calculateRiskLevel = (variables) => {
  const { productivityMultiplier, overtimeMultiplier, resourceLevel } = variables;
  
  let riskScore = 0;
  
  if (productivityMultiplier > 1.5) riskScore += 3;
  else if (productivityMultiplier > 1.3) riskScore += 2;
  else if (productivityMultiplier > 1.1) riskScore += 1;
  
  if (overtimeMultiplier > 1.3) riskScore += 2;
  else if (overtimeMultiplier > 1.2) riskScore += 1;
  
  if (resourceLevel === 'high') riskScore += 2;
  else if (resourceLevel === 'low') riskScore += 1;
  
  if (riskScore >= 5) return 'High';
  if (riskScore >= 3) return 'Medium';
  return 'Low';
};

export const generateParetoPoints = (costSummary, scheduleSummary) => {
  if (!costSummary || !scheduleSummary) return [];
  
  const points = [];
  const baseDuration = scheduleSummary.total_duration || 100;
  const baseCost = costSummary.total_cost || 1000000;
  
  // Baseline
  points.push({ duration: baseDuration, cost: baseCost, label: 'Baseline', type: 'baseline' });
  
  // Generate optimization scenarios
  const scenarios = [
    { prod: 1.2, ot: 1.0, label: 'Low Risk', type: 'scenario' },
    { prod: 1.4, ot: 1.1, label: 'Medium Risk', type: 'scenario' },
    { prod: 1.6, ot: 1.2, label: 'High Risk', type: 'scenario' },
    { prod: 1.0, ot: 1.0, label: 'Conservative', type: 'scenario' },
    { prod: 1.3, ot: 1.15, label: 'Balanced', type: 'optimal' }
  ];
  
  scenarios.forEach(s => {
    const duration = Math.ceil(baseDuration / s.prod);
    const cost = Math.round(baseCost * (1 + (s.prod - 1) * 0.15 + (s.ot - 1) * 0.2));
    points.push({ duration, cost, label: s.label, type: s.type });
  });
  
  return points;
};

export const exportOptimizationReport = (optimizationData, scenarios, variables, mode) => {
  const data = {
    optimization_mode: mode,
    variables,
    baseline: optimizationData.baseline,
    optimized: optimizationData.optimized,
    differences: optimizationData.differences,
    scenarios,
    risk_level: calculateRiskLevel(variables),
    exported_at: new Date().toISOString()
  };
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `optimization-report-${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
};
