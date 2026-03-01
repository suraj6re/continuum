export const RANKING_MODES = {
  LOWEST_COST: 'lowest_cost',
  FASTEST_DELIVERY: 'fastest_delivery',
  BEST_VALUE: 'best_value'
};

export const calculateSupplierCost = (supplier, qtoElements, baseCostSummary) => {
  if (!qtoElements || !baseCostSummary) return null;

  let materialCost = 0;
  
  // Calculate material cost based on supplier rates
  qtoElements.forEach(element => {
    const elementId = element.id || element.element_id;
    const rate = supplier.materialRates[elementId] || 0;
    materialCost += (element.quantity || 0) * rate;
  });

  // Calculate labor cost with supplier multiplier
  const laborCost = Math.round((baseCostSummary.labor_cost || 0) * (supplier.laborMultiplier || 1.0));

  // Equipment cost (simplified - could be duration-based)
  const equipmentCost = baseCostSummary.equipment_cost || 0;

  const totalCost = materialCost + laborCost + equipmentCost;

  return {
    material_cost: Math.round(materialCost),
    labor_cost: laborCost,
    equipment_cost: equipmentCost,
    total_cost: totalCost
  };
};

export const calculateRiskScore = (supplier, baselineCost) => {
  let riskScore = 0;
  let riskLevel = 'Low';
  let riskFactors = [];

  // Reliability check
  if (supplier.reliabilityScore < 60) {
    riskScore += 40;
    riskFactors.push('Low reliability score');
  } else if (supplier.reliabilityScore < 75) {
    riskScore += 20;
    riskFactors.push('Moderate reliability');
  }

  // Delivery time check
  if (supplier.deliveryTimeDays > 30) {
    riskScore += 30;
    riskFactors.push('Long delivery time');
  } else if (supplier.deliveryTimeDays > 15) {
    riskScore += 15;
    riskFactors.push('Extended delivery');
  }

  // Price deviation check
  if (supplier.costs && baselineCost) {
    const deviation = ((baselineCost - supplier.costs.total_cost) / baselineCost) * 100;
    if (deviation > 15) {
      riskScore += 25;
      riskFactors.push('Suspiciously low price');
    } else if (deviation < -20) {
      riskScore += 10;
      riskFactors.push('High price premium');
    }
  }

  // Determine risk level
  if (riskScore >= 50) {
    riskLevel = 'High';
  } else if (riskScore >= 25) {
    riskLevel = 'Medium';
  }

  return { riskScore, riskLevel, riskFactors };
};

export const rankSuppliers = (suppliers, mode) => {
  const ranked = [...suppliers];

  switch (mode) {
    case RANKING_MODES.LOWEST_COST:
      ranked.sort((a, b) => (a.costs?.total_cost || 0) - (b.costs?.total_cost || 0));
      break;
    case RANKING_MODES.FASTEST_DELIVERY:
      ranked.sort((a, b) => a.deliveryTimeDays - b.deliveryTimeDays);
      break;
    case RANKING_MODES.BEST_VALUE:
      // Weighted score: 60% cost, 40% reliability
      ranked.sort((a, b) => {
        const scoreA = (a.costs?.total_cost || 0) * 0.6 - a.reliabilityScore * 10000 * 0.4;
        const scoreB = (b.costs?.total_cost || 0) * 0.6 - b.reliabilityScore * 10000 * 0.4;
        return scoreA - scoreB;
      });
      break;
    default:
      break;
  }

  return ranked;
};

export const generateMockSuppliers = (qtoElements) => {
  if (!qtoElements || qtoElements.length === 0) return [];

  const suppliers = [
    {
      id: 'S1',
      name: 'BuildPro Materials Ltd',
      laborMultiplier: 1.0,
      deliveryTimeDays: 10,
      reliabilityScore: 85,
      paymentTerms: '30 days',
      materialRates: {}
    },
    {
      id: 'S2',
      name: 'QuickBuild Supplies',
      laborMultiplier: 1.15,
      deliveryTimeDays: 5,
      reliabilityScore: 78,
      paymentTerms: '15 days',
      materialRates: {}
    },
    {
      id: 'S3',
      name: 'Economy Construction Co',
      laborMultiplier: 0.9,
      deliveryTimeDays: 20,
      reliabilityScore: 65,
      paymentTerms: '45 days',
      materialRates: {}
    }
  ];

  // Generate rates for each element
  qtoElements.forEach(element => {
    const elementId = element.id || element.element_id;
    const baseRate = 1000; // Default base rate
    
    suppliers[0].materialRates[elementId] = baseRate;
    suppliers[1].materialRates[elementId] = Math.round(baseRate * 1.1);
    suppliers[2].materialRates[elementId] = Math.round(baseRate * 0.85);
  });

  return suppliers;
};

export const exportSupplierReport = (suppliers, selectedSupplier, rankingMode, baselineCost) => {
  const data = {
    ranking_mode: rankingMode,
    baseline_cost: baselineCost,
    selected_supplier: selectedSupplier,
    suppliers: suppliers.map(s => ({
      ...s,
      costs: s.costs,
      risk: s.risk
    })),
    exported_at: new Date().toISOString()
  };

  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `supplier-report-${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
};
