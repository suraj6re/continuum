export default function SupplierComparisonChart({ supplier, loading }) {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-pulse w-full h-full bg-gray-200 rounded"></div>
      </div>
    );
  }

  if (!supplier || !supplier.costs) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        Select a supplier to view cost breakdown
      </div>
    );
  }

  const total = supplier.costs.total_cost;
  const materialPct = ((supplier.costs.material_cost / total) * 100).toFixed(1);
  const laborPct = ((supplier.costs.labor_cost / total) * 100).toFixed(1);
  const equipmentPct = ((supplier.costs.equipment_cost / total) * 100).toFixed(1);

  return (
    <div className="space-y-6">
      <div>
        <h4 className="text-lg font-semibold text-gray-900 mb-4">{supplier.name}</h4>
        
        <div className="space-y-4">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600">Material Cost</span>
              <span className="font-medium text-gray-900">{materialPct}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-blue-600 h-3 rounded-full"
                style={{ width: `${materialPct}%` }}
              ></div>
            </div>
            <div className="text-xs text-gray-500 mt-1">
              ₹{supplier.costs.material_cost.toLocaleString('en-IN')}
            </div>
          </div>

          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600">Labor Cost</span>
              <span className="font-medium text-gray-900">{laborPct}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-green-600 h-3 rounded-full"
                style={{ width: `${laborPct}%` }}
              ></div>
            </div>
            <div className="text-xs text-gray-500 mt-1">
              ₹{supplier.costs.labor_cost.toLocaleString('en-IN')}
            </div>
          </div>

          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600">Equipment Cost</span>
              <span className="font-medium text-gray-900">{equipmentPct}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-orange-600 h-3 rounded-full"
                style={{ width: `${equipmentPct}%` }}
              ></div>
            </div>
            <div className="text-xs text-gray-500 mt-1">
              ₹{supplier.costs.equipment_cost.toLocaleString('en-IN')}
            </div>
          </div>
        </div>
      </div>

      <div className="pt-4 border-t border-gray-200">
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium text-gray-700">Total Cost</span>
          <span className="text-xl font-bold text-gray-900">
            ₹{supplier.costs.total_cost.toLocaleString('en-IN')}
          </span>
        </div>
      </div>

      <div className="pt-4 border-t border-gray-200 space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Delivery Time</span>
          <span className="font-medium text-gray-900">{supplier.deliveryTimeDays} days</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Reliability Score</span>
          <span className="font-medium text-gray-900">{supplier.reliabilityScore}/100</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Payment Terms</span>
          <span className="font-medium text-gray-900">{supplier.paymentTerms}</span>
        </div>
      </div>
    </div>
  );
}
