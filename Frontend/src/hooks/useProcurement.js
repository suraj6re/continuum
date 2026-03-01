import { useState, useEffect, useMemo } from 'react';
import { 
  generateProcurementPlan, 
  generatePaymentMilestones, 
  generateCashFlowData,
  calculateProcurementRisk,
  exportProcurementReport
} from '../services/procurementEngine';

export const useProcurement = (qtoElements, costItems, selectedSupplier, scheduleTasks) => {
  const [procurementItems, setProcurementItems] = useState([]);
  const [paymentMilestones, setPaymentMilestones] = useState([]);
  const [isFinalized, setIsFinalized] = useState(false);

  const procurementData = useMemo(() => {
    if (!selectedSupplier) return { items: [], summary: null };
    return generateProcurementPlan(qtoElements, costItems, selectedSupplier, scheduleTasks);
  }, [qtoElements, costItems, selectedSupplier, scheduleTasks]);

  useEffect(() => {
    if (procurementData.items.length > 0) {
      setProcurementItems(procurementData.items);
      if (procurementData.summary) {
        setPaymentMilestones(generatePaymentMilestones(procurementData.summary.total_value));
      }
    }
  }, [procurementData]);

  const cashFlowData = useMemo(() => {
    return generateCashFlowData(procurementItems, paymentMilestones);
  }, [procurementItems, paymentMilestones]);

  const riskAnalysis = useMemo(() => {
    if (!selectedSupplier) return null;
    return calculateProcurementRisk(selectedSupplier, procurementItems);
  }, [selectedSupplier, procurementItems]);

  const updateOrderStatus = (itemId, newStatus) => {
    setProcurementItems(prev => 
      prev.map(item => item.id === itemId ? { ...item, order_status: newStatus } : item)
    );
  };

  const updatePaymentStatus = (itemId, newStatus) => {
    setProcurementItems(prev => 
      prev.map(item => item.id === itemId ? { ...item, payment_status: newStatus } : item)
    );
  };

  const updateMilestone = (milestoneId, updates) => {
    setPaymentMilestones(prev => 
      prev.map(m => m.id === milestoneId ? { ...m, ...updates } : m)
    );
  };

  const finalizeProcurement = () => {
    setIsFinalized(true);
  };

  const exportReport = () => {
    const report = exportProcurementReport(
      { items: procurementItems, summary: procurementData.summary },
      selectedSupplier,
      paymentMilestones,
      riskAnalysis
    );
    
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `procurement-report-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return {
    procurementItems,
    summary: procurementData.summary,
    paymentMilestones,
    cashFlowData,
    riskAnalysis,
    isFinalized,
    updateOrderStatus,
    updatePaymentStatus,
    updateMilestone,
    finalizeProcurement,
    exportReport
  };
};
