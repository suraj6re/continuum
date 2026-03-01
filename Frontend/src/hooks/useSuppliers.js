import { useState, useEffect, useMemo } from 'react';
import { 
  calculateSupplierCost, 
  calculateRiskScore, 
  rankSuppliers, 
  generateMockSuppliers,
  RANKING_MODES 
} from '../services/supplierEngine';

export const useSuppliers = (qtoElements, costSummary) => {
  const [suppliers, setSuppliers] = useState([]);
  const [selectedSupplierId, setSelectedSupplierId] = useState(null);
  const [rankingMode, setRankingMode] = useState(RANKING_MODES.BEST_VALUE);

  useEffect(() => {
    if (qtoElements && qtoElements.length > 0 && suppliers.length === 0) {
      const mockSuppliers = generateMockSuppliers(qtoElements);
      setSuppliers(mockSuppliers);
    }
  }, [qtoElements, suppliers.length]);

  const suppliersWithCosts = useMemo(() => {
    if (!costSummary) return suppliers;

    return suppliers.map(supplier => {
      const costs = calculateSupplierCost(supplier, qtoElements, costSummary);
      const risk = calculateRiskScore(supplier, costSummary.total_cost);
      
      return {
        ...supplier,
        costs,
        risk,
        savings: costs ? costSummary.total_cost - costs.total_cost : 0
      };
    });
  }, [suppliers, qtoElements, costSummary]);

  const rankedSuppliers = useMemo(() => {
    return rankSuppliers(suppliersWithCosts, rankingMode);
  }, [suppliersWithCosts, rankingMode]);

  const selectedSupplier = useMemo(() => {
    return rankedSuppliers.find(s => s.id === selectedSupplierId);
  }, [rankedSuppliers, selectedSupplierId]);

  const addSupplier = (supplier) => {
    const newSupplier = {
      ...supplier,
      id: `S${Date.now()}`
    };
    setSuppliers(prev => [...prev, newSupplier]);
  };

  const updateSupplier = (id, updates) => {
    setSuppliers(prev => prev.map(s => s.id === id ? { ...s, ...updates } : s));
  };

  const removeSupplier = (id) => {
    setSuppliers(prev => prev.filter(s => s.id !== id));
    if (selectedSupplierId === id) {
      setSelectedSupplierId(null);
    }
  };

  const selectSupplier = (id) => {
    setSelectedSupplierId(id);
  };

  return {
    suppliers: rankedSuppliers,
    selectedSupplier,
    rankingMode,
    setRankingMode,
    addSupplier,
    updateSupplier,
    removeSupplier,
    selectSupplier
  };
};
