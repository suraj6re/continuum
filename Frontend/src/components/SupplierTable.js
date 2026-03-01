export default function SupplierTable({ suppliers, selectedSupplierId, onSelect, baselineCost }) {
  if (!suppliers || suppliers.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No suppliers added. Add suppliers to compare costs.
      </div>
    );
  }

  const getRiskBadge = (riskLevel) => {
    const config = {
      Low: 'bg-green-100 text-green-800',
      Medium: 'bg-yellow-100 text-yellow-800',
      High: 'bg-red-100 text-red-800'
    };
    return config[riskLevel] || config.Low;
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Supplier</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Cost</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Material</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Labor</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Delivery</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reliability</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Risk</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Savings</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {suppliers.map((supplier, idx) => {
            const isSelected = supplier.id === selectedSupplierId;
            const isBest = idx === 0;

            return (
              <tr 
                key={supplier.id} 
                className={`${isSelected ? 'bg-blue-50' : 'hover:bg-gray-50'} ${isBest ? 'border-l-4 border-green-500' : ''}`}
              >
                <td className="px-6 py-4 text-sm font-medium text-gray-900">
                  {supplier.name}
                  {isBest && (
                    <span className="ml-2 px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
                      Best
                    </span>
                  )}
                  {isSelected && (
                    <span className="ml-2 px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                      Selected
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">
                  ₹{supplier.costs?.total_cost.toLocaleString('en-IN') || 'N/A'}
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  ₹{supplier.costs?.material_cost.toLocaleString('en-IN') || 'N/A'}
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  ₹{supplier.costs?.labor_cost.toLocaleString('en-IN') || 'N/A'}
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  {supplier.deliveryTimeDays} days
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  <div className="flex items-center">
                    <span className="text-yellow-500 mr-1">★</span>
                    {supplier.reliabilityScore}/100
                  </div>
                </td>
                <td className="px-6 py-4 text-sm">
                  <span className={`px-2 py-1 text-xs font-medium rounded ${getRiskBadge(supplier.risk?.riskLevel)}`}>
                    {supplier.risk?.riskLevel || 'Low'}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm">
                  {supplier.savings > 0 ? (
                    <span className="text-green-600 font-medium">
                      -₹{supplier.savings.toLocaleString('en-IN')}
                    </span>
                  ) : (
                    <span className="text-red-600 font-medium">
                      +₹{Math.abs(supplier.savings).toLocaleString('en-IN')}
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 text-sm">
                  <button
                    onClick={() => onSelect(supplier.id)}
                    className={`px-3 py-1 text-xs font-medium rounded ${
                      isSelected
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    {isSelected ? 'Selected' : 'Select'}
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
