import { useState } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import SupplierForm from '../components/SupplierForm';
import SupplierTable from '../components/SupplierTable';
import SupplierComparisonChart from '../components/SupplierComparisonChart';
import RiskBadge from '../components/RiskBadge';
import { useProjectStore } from '../hooks/useProjectStore';
import { useSuppliers } from '../hooks/useSuppliers';
import { exportSupplierReport, RANKING_MODES } from '../services/supplierEngine';

export default function Suppliers() {
  const { qtoElements, costSummary, costItems, processingStatus, setSelectedSupplier: setGlobalSelectedSupplier } = useProjectStore();
  const {
    suppliers,
    selectedSupplier,
    rankingMode,
    setRankingMode,
    addSupplier,
    selectSupplier
  } = useSuppliers(qtoElements, costSummary);

  const [showAddForm, setShowAddForm] = useState(false);

  const handleSelectSupplier = (id) => {
    selectSupplier(id);
    const supplier = suppliers.find(s => s.id === id);
    if (supplier) {
      setGlobalSelectedSupplier(supplier);
    }
  };

  const handleExport = () => {
    exportSupplierReport(suppliers, selectedSupplier, rankingMode, costSummary?.total_cost);
  };

  if (processingStatus !== 'complete') {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-xl text-gray-600 mb-2">Complete QTO and Cost Analysis to enable supplier comparison.</p>
          <p className="text-sm text-gray-500">Upload and process drawings first.</p>
        </div>
      </div>
    );
  }

  if (!costSummary || !costItems) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-xl text-gray-600 mb-2">Cost Intelligence required before supplier evaluation.</p>
          <p className="text-sm text-gray-500">Generate cost analysis first.</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-brand-charcoal mb-2">Supplier Comparison</h1>
          <p className="text-text-secondary">Compare suppliers and optimize procurement</p>
        </div>
        <div className="flex space-x-2">
          <Button onClick={() => setShowAddForm(!showAddForm)}>
            {showAddForm ? 'Cancel' : 'Add Supplier'}
          </Button>
          <Button onClick={handleExport} variant="outline" disabled={suppliers.length === 0}>
            Export Report
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
        <Card>
          <p className="text-sm text-gray-600 mb-1">Selected Supplier</p>
          <p className="text-lg font-bold text-gray-900">
            {selectedSupplier ? selectedSupplier.name : 'None'}
          </p>
        </Card>
        <Card>
          <p className="text-sm text-gray-600 mb-1">Total Cost</p>
          <p className="text-lg font-bold text-gray-900">
            {selectedSupplier ? `₹${(selectedSupplier.costs.total_cost / 100000).toFixed(2)}L` : 'N/A'}
          </p>
        </Card>
        <Card>
          <p className="text-sm text-gray-600 mb-1">Cost Savings</p>
          <p className={`text-lg font-bold ${
            selectedSupplier && selectedSupplier.savings > 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            {selectedSupplier ? (
              selectedSupplier.savings > 0 ? 
                `-₹${(selectedSupplier.savings / 100000).toFixed(2)}L` : 
                `+₹${(Math.abs(selectedSupplier.savings) / 100000).toFixed(2)}L`
            ) : 'N/A'}
          </p>
        </Card>
        <Card>
          <p className="text-sm text-gray-600 mb-1">Risk Level</p>
          <p className={`text-lg font-bold ${
            selectedSupplier?.risk?.riskLevel === 'High' ? 'text-red-600' :
            selectedSupplier?.risk?.riskLevel === 'Medium' ? 'text-yellow-600' :
            'text-green-600'
          }`}>
            {selectedSupplier?.risk?.riskLevel || 'N/A'}
          </p>
        </Card>
        <Card>
          <p className="text-sm text-gray-600 mb-1">Delivery Impact</p>
          <p className="text-lg font-bold text-gray-900">
            {selectedSupplier ? `${selectedSupplier.deliveryTimeDays} days` : 'N/A'}
          </p>
        </Card>
      </div>

      {showAddForm && (
        <Card title="Add New Supplier" className="mb-8">
          <SupplierForm 
            onAdd={(supplier) => {
              addSupplier(supplier);
              setShowAddForm(false);
            }}
            onCancel={() => setShowAddForm(false)}
          />
        </Card>
      )}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="md:col-span-3">
          <Card 
            title="Supplier Comparison" 
            action={
              <select 
                value={rankingMode}
                onChange={(e) => setRankingMode(e.target.value)}
                className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
              >
                <option value={RANKING_MODES.BEST_VALUE}>Best Value</option>
                <option value={RANKING_MODES.LOWEST_COST}>Lowest Cost</option>
                <option value={RANKING_MODES.FASTEST_DELIVERY}>Fastest Delivery</option>
              </select>
            }
          >
            <SupplierTable 
              suppliers={suppliers}
              selectedSupplierId={selectedSupplier?.id}
              onSelect={handleSelectSupplier}
              baselineCost={costSummary.total_cost}
            />
          </Card>
        </div>

        <div className="space-y-6">
          <Card title="Cost Breakdown">
            <SupplierComparisonChart supplier={selectedSupplier} loading={false} />
          </Card>

          {selectedSupplier && (
            <Card title="Risk Assessment">
              <RiskBadge supplier={selectedSupplier} />
            </Card>
          )}
        </div>
      </div>

      {selectedSupplier && selectedSupplier.deliveryTimeDays > 15 && (
        <div className="mb-8 p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-start">
            <span className="text-2xl mr-3">⚠</span>
            <div>
              <p className="text-sm font-medium text-yellow-900 mb-1">Delivery Impact Warning</p>
              <p className="text-sm text-yellow-800">
                Selected supplier has a delivery time of {selectedSupplier.deliveryTimeDays} days, 
                which may delay structural work start. Consider impact on project schedule.
              </p>
            </div>
          </div>
        </div>
      )}

      <Card title="Baseline vs Selected Supplier">
        <div className="grid grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-4">Baseline Cost</h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                <span className="text-sm text-gray-600">Material Cost</span>
                <span className="text-sm font-medium">₹{costSummary.material_cost.toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                <span className="text-sm text-gray-600">Labor Cost</span>
                <span className="text-sm font-medium">₹{costSummary.labor_cost.toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                <span className="text-sm text-gray-600">Equipment Cost</span>
                <span className="text-sm font-medium">₹{costSummary.equipment_cost.toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gray-100 rounded border-2 border-gray-300">
                <span className="text-sm font-bold text-gray-900">Total</span>
                <span className="text-sm font-bold text-gray-900">₹{costSummary.total_cost.toLocaleString('en-IN')}</span>
              </div>
            </div>
          </div>

          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-4">
              {selectedSupplier ? selectedSupplier.name : 'No Supplier Selected'}
            </h4>
            {selectedSupplier ? (
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-blue-50 rounded">
                  <span className="text-sm text-gray-600">Material Cost</span>
                  <span className="text-sm font-medium">₹{selectedSupplier.costs.material_cost.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-blue-50 rounded">
                  <span className="text-sm text-gray-600">Labor Cost</span>
                  <span className="text-sm font-medium">₹{selectedSupplier.costs.labor_cost.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-blue-50 rounded">
                  <span className="text-sm text-gray-600">Equipment Cost</span>
                  <span className="text-sm font-medium">₹{selectedSupplier.costs.equipment_cost.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-blue-100 rounded border-2 border-blue-300">
                  <span className="text-sm font-bold text-blue-900">Total</span>
                  <span className="text-sm font-bold text-blue-900">₹{selectedSupplier.costs.total_cost.toLocaleString('en-IN')}</span>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500 text-sm">
                Select a supplier to view comparison
              </div>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}
