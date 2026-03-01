import { useEffect, useState, useMemo } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import CostSummaryCard from '../components/CostSummaryCard';
import CostBreakdownTable from '../components/CostBreakdownTable';
import CostDistributionChart from '../components/CostDistributionChart';
import { useProjectStore } from '../hooks/useProjectStore';
import { fetchCostData, exportCostToCSV, exportCostToJSON } from '../services/costService';

export default function Cost() {
  const { 
    currentProjectId, 
    processingStatus, 
    costSummary, 
    costItems, 
    pricingAdjustment,
    updateCostData,
    updatePricingAdjustment
  } = useProjectStore();
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (processingStatus === 'complete' && currentProjectId && !costSummary) {
      setLoading(true);
      fetchCostData(currentProjectId)
        .then(data => {
          updateCostData(data);
          setError(null);
        })
        .catch(err => {
          console.error('Cost data error:', err);
          setError(err.message);
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [processingStatus, currentProjectId, costSummary, updateCostData]);

  const adjustedCostItems = useMemo(() => {
    if (!costItems.length) return [];
    return costItems.map(item => ({
      ...item,
      unit_rate: item.unit_rate * pricingAdjustment,
      material_cost: Math.round(item.material_cost * pricingAdjustment),
      labor_cost: Math.round(item.labor_cost * pricingAdjustment),
      equipment_cost: Math.round(item.equipment_cost * pricingAdjustment),
      total_cost: Math.round(item.total_cost * pricingAdjustment)
    }));
  }, [costItems, pricingAdjustment]);

  const adjustedCostSummary = useMemo(() => {
    if (!costSummary) return null;
    return {
      material_cost: Math.round(costSummary.material_cost * pricingAdjustment),
      labor_cost: Math.round(costSummary.labor_cost * pricingAdjustment),
      equipment_cost: Math.round(costSummary.equipment_cost * pricingAdjustment),
      total_cost: Math.round(costSummary.total_cost * pricingAdjustment)
    };
  }, [costSummary, pricingAdjustment]);

  const handleExportCSV = () => {
    exportCostToCSV(adjustedCostItems, adjustedCostSummary, pricingAdjustment);
  };

  const handleExportJSON = () => {
    exportCostToJSON(adjustedCostItems, adjustedCostSummary, pricingAdjustment);
  };

  const handleRetry = () => {
    if (currentProjectId) {
      setLoading(true);
      setError(null);
      fetchCostData(currentProjectId)
        .then(data => {
          updateCostData(data);
          setError(null);
        })
        .catch(err => {
          console.error('Cost data error:', err);
          setError(err.message);
        })
        .finally(() => {
          setLoading(false);
        });
    }
  };

  if (processingStatus !== 'complete') {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-xl text-gray-600 mb-2">Complete QTO extraction to unlock cost intelligence.</p>
          <p className="text-sm text-gray-500">Upload and process drawings first.</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-xl text-red-600 mb-4">Failed to load cost data</p>
          <p className="text-sm text-gray-500 mb-4">{error}</p>
          <Button onClick={handleRetry}>Retry</Button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-brand-charcoal mb-2">Cost Intelligence</h1>
          <p className="text-text-secondary">
            {loading ? 'Loading cost data...' : 'AI-powered cost estimation with uncertainty analysis'}
          </p>
        </div>
        <div className="flex space-x-2">
          <Button onClick={handleExportCSV} disabled={loading || !adjustedCostItems.length}>
            Export CSV
          </Button>
          <Button onClick={handleExportJSON} variant="outline" disabled={loading || !adjustedCostItems.length}>
            Export JSON
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <CostSummaryCard 
          title="Material Cost" 
          value={adjustedCostSummary?.material_cost || 0}
          loading={loading}
        />
        <CostSummaryCard 
          title="Labor Cost" 
          value={adjustedCostSummary?.labor_cost || 0}
          loading={loading}
        />
        <CostSummaryCard 
          title="Equipment Cost" 
          value={adjustedCostSummary?.equipment_cost || 0}
          loading={loading}
        />
        <CostSummaryCard 
          title="Total Cost" 
          value={adjustedCostSummary?.total_cost || 0}
          loading={loading}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card title="Cost Distribution" className="md:col-span-2">
          <CostDistributionChart costSummary={adjustedCostSummary} loading={loading} />
        </Card>

        <Card title="Market Adjustment">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Adjustment Factor
              </label>
              <input
                type="range"
                min="0.8"
                max="1.5"
                step="0.01"
                value={pricingAdjustment}
                onChange={(e) => updatePricingAdjustment(parseFloat(e.target.value))}
                className="w-full"
                disabled={loading}
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>0.8x</span>
                <span className="font-bold text-gray-900">{pricingAdjustment.toFixed(2)}x</span>
                <span>1.5x</span>
              </div>
            </div>
            <div className="pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-600 mb-2">Impact on Total Cost</p>
              <p className="text-2xl font-bold text-brand-orange">
                {pricingAdjustment > 1 ? '+' : ''}
                {((pricingAdjustment - 1) * 100).toFixed(0)}%
              </p>
            </div>
          </div>
        </Card>
      </div>

      <Card title="Cost Breakdown">
        <CostBreakdownTable items={adjustedCostItems} loading={loading} />
        {adjustedCostSummary && (
          <div className="mt-6 pt-6 border-t border-gray-200 flex justify-between items-center">
            <p className="text-lg font-semibold text-gray-900">Total Estimated Cost</p>
            <p className="text-2xl font-bold text-brand-orange">
              ₹{adjustedCostSummary.total_cost.toLocaleString('en-IN')}
            </p>
          </div>
        )}
      </Card>
    </div>
  );
}
