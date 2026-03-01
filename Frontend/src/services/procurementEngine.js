export const generateProcurementPlan = (qtoElements, costItems, selectedSupplier, scheduleTasks) => {
  if (!qtoElements || qtoElements.length === 0) {
    return { items: [], summary: null };
  }

  const procurementItems = qtoElements.map((element, index) => {
    const costItem = costItems?.find(c => 
      c.element_name === element.element_name || 
      c.material === element.material
    );

    const scheduleTask = scheduleTasks?.find(t => 
      t.name.toLowerCase().includes(element.element_name?.toLowerCase()) ||
      t.name.toLowerCase().includes(element.material?.toLowerCase())
    );

    const unitRate = costItem?.unit_rate || selectedSupplier?.pricing?.[element.material] || 0;
    const totalCost = unitRate * (element.quantity || 0);
    const deliveryTime = selectedSupplier?.deliveryTimeDays || 7;
    const requiredByDay = scheduleTask?.start || 0;
    const deliveryETA = requiredByDay - deliveryTime;

    return {
      id: `PO-${String(index + 1).padStart(4, '0')}`,
      element_name: element.element_name || element.material,
      material: element.material,
      quantity: element.quantity || 0,
      unit: element.unit || 'm³',
      supplier_rate: unitRate,
      total_cost: totalCost,
      required_by_day: requiredByDay,
      delivery_time: deliveryTime,
      delivery_eta: Math.max(0, deliveryETA),
      order_status: 'Not Ordered',
      payment_status: 'Pending',
      is_delayed: deliveryETA > requiredByDay
    };
  });

  const totalValue = procurementItems.reduce((sum, item) => sum + item.total_cost, 0);
  const pendingOrders = procurementItems.filter(i => i.order_status === 'Not Ordered').length;
  const deliveredOrders = procurementItems.filter(i => i.order_status === 'Delivered').length;
  const delayedItems = procurementItems.filter(i => i.is_delayed).length;

  const summary = {
    total_value: totalValue,
    total_items: procurementItems.length,
    pending_orders: pendingOrders,
    delivered_orders: deliveredOrders,
    delayed_items: delayedItems,
    payment_due: totalValue * 0.2
  };

  return { items: procurementItems, summary };
};

export const generatePaymentMilestones = (totalValue) => {
  return [
    { id: 1, name: 'Advance Payment', percentage: 20, amount: totalValue * 0.2, status: 'Pending', due_day: 0 },
    { id: 2, name: 'On Delivery', percentage: 50, amount: totalValue * 0.5, status: 'Pending', due_day: 7 },
    { id: 3, name: 'After Inspection', percentage: 30, amount: totalValue * 0.3, status: 'Pending', due_day: 14 }
  ];
};

export const generateCashFlowData = (procurementItems, paymentMilestones) => {
  const maxDay = Math.max(...procurementItems.map(i => i.required_by_day), 30);
  const data = [];
  let cumulative = 0;

  for (let day = 0; day <= maxDay; day++) {
    const dayPayments = paymentMilestones
      .filter(m => m.due_day === day && m.status !== 'Completed')
      .reduce((sum, m) => sum + m.amount, 0);
    
    cumulative += dayPayments;
    data.push({ day, amount: cumulative });
  }

  return data;
};

export const calculateProcurementRisk = (selectedSupplier, procurementItems) => {
  let riskScore = 0;
  const factors = [];

  if (selectedSupplier?.reliability < 0.7) {
    riskScore += 30;
    factors.push('Low supplier reliability');
  }

  const delayedCount = procurementItems.filter(i => i.is_delayed).length;
  if (delayedCount > procurementItems.length * 0.3) {
    riskScore += 25;
    factors.push('High delivery delay risk');
  }

  if (selectedSupplier?.deliveryTimeDays > 14) {
    riskScore += 20;
    factors.push('Long delivery time');
  }

  const avgDeviation = selectedSupplier?.priceDeviation || 0;
  if (Math.abs(avgDeviation) > 15) {
    riskScore += 15;
    factors.push('High price deviation');
  }

  const level = riskScore < 30 ? 'Low' : riskScore < 60 ? 'Medium' : 'High';
  
  return { level, score: riskScore, factors };
};

export const exportProcurementReport = (procurementData, selectedSupplier, paymentMilestones, riskAnalysis) => {
  const report = {
    generated_at: new Date().toISOString(),
    supplier: {
      name: selectedSupplier?.name,
      location: selectedSupplier?.location,
      reliability: selectedSupplier?.reliability
    },
    summary: procurementData.summary,
    purchase_items: procurementData.items,
    payment_milestones: paymentMilestones,
    risk_analysis: riskAnalysis,
    total_procurement_value: procurementData.summary?.total_value || 0
  };

  return report;
};
