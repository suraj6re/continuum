import { useState, useEffect, useMemo } from 'react';
import { 
  generateProcurementPlan, 
  generatePaymentMilestones, 
  calculateProcurementRisk,
  ORDER_STATUS,
  PAYMENT_STATUS
} from '../services/procurementEngine';
import { fetchProcurementData } from '../services/procurementService';
import { useProjectStore } from './useProjectStore';

export const useProcurement = (qtoElements, selectedSupplier, scheduleTasks) => {
  const { currentProjectId } = useProjectStore();
  const [procurementItems, setProcurementItems] = useState([]);
  const [paymentMilestones, setPaymentMilestones] = useState([]);
  const [isFinalized, setIsFinalized] = useState(false);
  const [backendData, setBackendData] = useState(null);

  useEffect(() => {
    if (currentProjectId && procurementItems.length === 0) {
      fetchProcurementData(currentProjectId)
        .then(data => {
          if (data && data.procurement_items) {
            setBackendData(data);
            setProcurementItems(data.procurement_items);
            if (data.payment_milestones) {
              setPaymentMilestones(data.payment_milestones);
            }
          } else if (qtoElements && selectedSupplier) {
            const items = generateProcurementPlan(qtoElements, selectedSupplier, scheduleTasks);
            setProcurementItems(items);
            const totalCost = items.reduce((sum, item) => sum + item.total_cost, 0);
            const milestones = generatePaymentMilestones(totalCost);
            setPaymentMilestones(milestones);
          }
        })
        .catch(err => {
          console.error('Procurement fetch error:', err);
          if (qtoElements && selectedSupplier) {
            const items = generateProcurementPlan(qtoElements, selectedSupplier, scheduleTasks);
            setProcurementItems(items);
            const totalCost = items.reduce((sum, item) => sum + item.total_cost, 0);
            const milestones = generatePaymentMilestones(totalCost);
            setPaymentMilestones(milestones);
          }
        });
    }
  }, [currentProjectId, qtoElements, selectedSupplier, scheduleTasks, procurementItems.length]);

  const summary = useMemo(() => {
    const totalValue = procurementItems.reduce((sum, item) => sum + item.total_cost, 0);
    const totalItems = procurementItems.length;
    const pendingOrders = procurementItems.filter(item => 
      item.order_status === ORDER_STATUS.NOT_ORDERED || item.order_status === ORDER_STATUS.ORDERED
    ).length;
    const deliveredOrders = procurementItems.filter(item => 
      item.order_status === ORDER_STATUS.DELIVERED
    ).length;
    const paymentDue = paymentMilestones
      .filter(m => m.status === PAYMENT_STATUS.PENDING)
      .reduce((sum, m) => sum + m.amount, 0);

    return {
      total_value: totalValue,
      total_items: totalItems,
      pending_orders: pendingOrders,
      delivered_orders: deliveredOrders,
      payment_due: paymentDue
    };
  }, [procurementItems, paymentMilestones]);

  const risk = useMemo(() => {
    if (!selectedSupplier) return null;
    return calculateProcurementRisk(procurementItems, selectedSupplier);
  }, [procurementItems, selectedSupplier]);

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

  const updateMilestoneStatus = (milestoneId, newStatus) => {
    setPaymentMilestones(prev =>
      prev.map(m => m.id === milestoneId ? { ...m, status: newStatus } : m)
    );
  };

  const finalizeProcurement = () => {
    setIsFinalized(true);
  };

  return {
    procurementItems,
    paymentMilestones,
    summary,
    risk,
    isFinalized,
    updateOrderStatus,
    updatePaymentStatus,
    updateMilestoneStatus,
    finalizeProcurement
  };
};
