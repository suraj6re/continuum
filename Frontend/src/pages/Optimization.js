import { useState } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import OptimizationControls from '../components/OptimizationControls';
import OptimizationSummary from '../components/OptimizationSummary';
import ScenarioComparison from '../components/ScenarioComparison';
import ParetoChart from '../components/ParetoChart';
import RiskIndicator from '../components/RiskIndicator';
import { useProjectStore } from '../hooks/useProjectStore';
import { useOptimization } from '../hooks/useOptimization';
import { generateParetoPoints, exportOptimizationReport } from '../services/optimizationEngine';
import { useSchedule } from '../hooks/useSchedule';

export default function Optimization() {
  const { qtoElements, costSummary, costItems, processingStatus } = useProjectStore();
  const { summary: scheduleSummary } = useSchedule(qtoElements, processingStatus);
  const {
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
  } = useOptimization(costSummary, scheduleSummary);

  const [scenarioName, setScenarioName] = useState('');

  const handleSaveScenario = () => {
    const name = scenarioName || `Scenario ${scenarios.length + 1}`;
    saveScenario(name);
    setScenarioName('');
  };

  const handleExport = () => {
    if (optimizationData) {
      exportOptimizationReport(optimizationData, scenarios, variables, mode);
    }
  };

  const paretoPoints = generateParetoPoints(costSummary, scheduleSummary);

  if (processingStatus !== 'complete') {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-xl text-gray-600 mb-2">Complete QTO and Schedule to enable optimization.</p>
          <p className="text-sm text-gray-500">Upload and process drawings first.</p>
        </div>
      </div>
    );
  }

  if (!costSummary || !scheduleSummary) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-xl text-gray-600 mb-2">Cost and Schedule data required.</p>
          <p className="text-sm text-gray-500">Generate cost analysis and schedule first.</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-brand-charcoal mb-2">Cost-Time Optimization</h1>
          <p className="text-text-secondary">Optimize project duration and cost trade-offs</p>
        </div>
        <Button onClick={handleExport} disabled={!optimizationData}>
          Export Report
        </Button>
      </div>

      {optimizationData && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
            <OptimizationSummary
              title="Optimized Duration"
              value={`${optimizationData.optimized.duration} days`}
              subtitle={`Baseline: ${optimizationData.baseline.duration} days`}
              color="blue"
            />
            <OptimizationSummary
              title="Optimized Cost"
              value={`₹${(optimizationData.optimized.total_cost / 100000).toFixed(2)}L`}
              subtitle={`Baseline: ₹${(optimizationData.baseline.total_cost / 100000).toFixed(2)}L`}
              color="green"
            />
            <OptimizationSummary
              title="Time Saved"
              value={`${optimizationData.differences.duration_diff} days`}
              subtitle={`${optimizationData.differences.duration_diff_pct.toFixed(1)}% reduction`}
              color={optimizationData.differences.duration_diff > 0 ? 'green' : 'red'}
            />
            <OptimizationSummary
              title="Cost Impact"
              value={`${optimizationData.differences.cost_diff_pct > 0 ? '-' : '+'}₹${Math.abs(optimizationData.differences.cost_diff / 100000).toFixed(2)}L`}
              subtitle={`${Math.abs(optimizationData.differences.cost_diff_pct).toFixed(1)}% ${optimizationData.differences.cost_diff_pct > 0 ? 'savings' : 'increase'}`}
              color={optimizationData.differences.cost_diff > 0 ? 'green' : 'red'}
            />
            <OptimizationSummary
              title="Efficiency Score"
              value={optimizationData.differences.efficiency_score.toFixed(2)}
              subtitle="Time saved / Cost increase"
              color="orange"
            />
          </div>

          <div className="mb-8 p-6 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm font-medium text-blue-900">
              Trade-off Analysis: {optimizationData.differences.duration_diff_pct > 0 ? (
                <>
                  Reducing duration by <span className="font-bold">{Math.abs(optimizationData.differences.duration_diff_pct).toFixed(1)}%</span>
                  {optimizationData.differences.cost_diff_pct < 0 ? (
                    <> increases cost by <span className="font-bold">{Math.abs(optimizationData.differences.cost_diff_pct).toFixed(1)}%</span></>
                  ) : (
                    <> while saving <span className="font-bold">{Math.abs(optimizationData.differences.cost_diff_pct).toFixed(1)}%</span> on cost</>
                  )}
                </>
              ) : (
                <>Extending duration may reduce costs</>
              )}
            </p>
          </div>
        </>
      )}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="md:col-span-3">
          <Card title="Pareto Frontier - Cost vs Duration">
            <ParetoChart points={paretoPoints} loading={false} />
          </Card>
        </div>

        <div className="space-y-6">
          <Card title="Optimization Controls">
            <OptimizationControls
              mode={mode}
              setMode={setMode}
              variables={variables}
              updateVariable={updateVariable}
              onReset={resetVariables}
              onSave={handleSaveScenario}
            />
          </Card>

          <Card title="Risk Assessment">
            <RiskIndicator riskLevel={riskLevel} loading={false} />
          </Card>
        </div>
      </div>

      {optimizationData && (
        <Card title="Cost Breakdown Comparison" className="mb-8">
          <div className="grid grid-cols-2 gap-6">
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-4">Baseline</h4>
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <span className="text-sm text-gray-600">Material Cost</span>
                  <span className="text-sm font-medium">₹{optimizationData.baseline.material_cost.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <span className="text-sm text-gray-600">Labor Cost</span>
                  <span className="text-sm font-medium">₹{optimizationData.baseline.labor_cost.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <span className="text-sm text-gray-600">Equipment Cost</span>
                  <span className="text-sm font-medium">₹{optimizationData.baseline.equipment_cost.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-100 rounded border-2 border-gray-300">
                  <span className="text-sm font-bold text-gray-900">Total</span>
                  <span className="text-sm font-bold text-gray-900">₹{optimizationData.baseline.total_cost.toLocaleString('en-IN')}</span>
                </div>
              </div>
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-4">Optimized</h4>
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-blue-50 rounded">
                  <span className="text-sm text-gray-600">Material Cost</span>
                  <span className="text-sm font-medium">₹{optimizationData.optimized.material_cost.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-blue-50 rounded">
                  <span className="text-sm text-gray-600">Labor Cost</span>
                  <span className="text-sm font-medium">₹{optimizationData.optimized.labor_cost.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-blue-50 rounded">
                  <span className="text-sm text-gray-600">Equipment Cost</span>
                  <span className="text-sm font-medium">₹{optimizationData.optimized.equipment_cost.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-blue-100 rounded border-2 border-blue-300">
                  <span className="text-sm font-bold text-blue-900">Total</span>
                  <span className="text-sm font-bold text-blue-900">₹{optimizationData.optimized.total_cost.toLocaleString('en-IN')}</span>
                </div>
              </div>
            </div>
          </div>
        </Card>
      )}

      <Card title="Scenario Comparison">
        <div className="mb-4">
          <input
            type="text"
            placeholder="Enter scenario name..."
            value={scenarioName}
            onChange={(e) => setScenarioName(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
          />
        </div>
        <ScenarioComparison scenarios={scenarios} onRemove={removeScenario} />
      </Card>
    </div>
  );
}
