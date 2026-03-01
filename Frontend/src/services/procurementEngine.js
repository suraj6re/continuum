export const ORDER_STATUS = {
  NOT_ORDERED: 'Not Ordered',
  ORDERED: 'Ordered',
  IN_TRANSIT: 'In Transit',
  DELIVERED: 'Delivered'
};

export const PAYMENT_STATUS = {
  PENDING: 'Pending',
  PARTIAL: 'Partial',
  COMPLETED: 'Completed'
};

export const generateProcurementPlan = (qtoElements, selectedSupplier, scheduleTasks) => {
  if (!qtoElements || !selectedSupplier) return [];

  const procurementItems = qtoElements.map((element, index) => {
    const elementId = element.id || element.element_id;
    const supplierRate = selectedSupplier.materialRates?.[elementId] || 1000;
    const totalCost = (element.quantity || 0) * supplierRate;
    
    // Find required by day from schedule
    let requiredByDay = 10 + index * 5; // Default staggered delivery
    if (scheduleTasks && scheduleTasks.length > 0) {
      const relatedTask = scheduleTasks.find(t => 
        t.element_name?.toLowerCase().includes(element.element_name?.toLowerCase() || element.name?.toLowerCase())
      );
      if (relatedTask) {
        requiredByDay = relatedTask.start_day || requiredByDay;
      }
    }

    const deliveryETA = requiredByDay - selectedSupplier.deliveryTimeDays;

    return {
      id: `PO-${Date.now()}-${index}`,
      element_name: element.element_name || element.name,
      quantity: element.quantity,
      unit: element.unit || 'm³',
      supplier_rate: supplierRate,
      total_cost: totalCost,
      required_by_day: requiredByDay,
      delivery_time: selectedSupplier.deliveryTimeDays,
      delivery_eta: deliveryETA,
      order_status: ORDER_STATUS.NOT_ORDERED,
      payment_status: PAYMENT_STATUS.PENDING,
      is_delayed: deliveryETA > requiredByDay
    };
  });

  return procurementItems;
};

export const generatePaymentMilestones = (totalCost) => {
  return [
    { id: 1, name: 'Advance Payment', percentage: 20, amount: Math.round(totalCost * 0.2), status: PAYMENT_STATUS.PENDING },
    { id: 2, name: 'On Delivery', percentage: 50, amount: Math.round(totalCost * 0.5), status: PAYMENT_STATUS.PENDING },
    { id: 3, name: 'After Inspection', percentage: 30, amount: Math.round(totalCost * 0.3), status: PAYMENT_STATUS.PENDING }
  ];
};

export const calculateProcurementRisk = (procurementItems, selectedSupplier) => {
  let riskScore = 0;
  const riskFactors = [];

  // Supplier reliability
  if (selectedSupplier.reliabilityScore < 70) {
    riskScore += 30;
    riskFactors.push('Low supplier reliability');
  }

  // Delivery delays
  const delayedItems = procurementItems.filter(item => item.is_delayed).length;
  if (delayedItems > 0) {
    riskScore += 25;
    riskFactors.push(`${delayedItems} items may be delayed`);
  }

  // High upfront payment
  const advancePayment = 0.2; // 20%
  if (advancePayment > 0.3) {
    riskScore += 20;
    riskFactors.push('High upfront payment required');
  }

  // Long delivery time
  if (selectedSupplier.deliveryTimeDays > 20) {
    riskScore += 15;
    riskFactors.push('Extended delivery timeline');
  }

  let riskLevel = 'Low';
  if (riskScore >= 50) riskLevel = 'High';
  else if (riskScore >= 30) riskLevel = 'Medium';

  return { riskScore, riskLevel, riskFactors };
};

export const generateCashFlowData = (procurementItems, paymentMilestones) => {
  const cashFlowPoints = [];
  let cumulativeCost = 0;

  // Sort items by required date
  const sortedItems = [...procurementItems].sort((a, b) => a.required_by_day - b.required_by_day);

  sortedItems.forEach(item => {
    // Advance payment
    const advanceDay = Math.max(0, item.required_by_day - item.delivery_time - 5);
    cumulativeCost += item.total_cost * 0.2;
    cashFlowPoints.push({ day: advanceDay, amount: cumulativeCost, label: 'Advance' });

    // Delivery payment
    const deliveryDay = item.required_by_day;
    cumulativeCost += item.total_cost * 0.5;
    cashFlowPoints.push({ day: deliveryDay, amount: cumulativeCost, label: 'Delivery' });

    // Final payment
    const finalDay = item.required_by_day + 7;
    cumulativeCost += item.total_cost * 0.3;
    cashFlowPoints.push({ day: finalDay, amount: cumulativeCost, label: 'Final' });
  });

  return cashFlowPoints;
};

export const exportProcurementReport = (procurementData, selectedSupplier, paymentMilestones, risk) => {
  const data = {
    supplier: {
      name: selectedSupplier.name,
      reliability: selectedSupplier.reliabilityScore,
      delivery_time: selectedSupplier.deliveryTimeDays,
      payment_terms: selectedSupplier.paymentTerms
    },
    procurement_items: procurementData.items,
    payment_milestones: paymentMilestones,
    summary: procurementData.summary,
    risk_analysis: risk,
    exported_at: new Date().toISOString()
  };

  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `procurement-plan-${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
};
