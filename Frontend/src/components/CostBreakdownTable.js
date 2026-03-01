export default function CostBreakdownTable({ items, loading }) {
  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        {[1, 2, 3].map(i => (
          <div key={i} className="h-12 bg-gray-200 rounded"></div>
        ))}
      </div>
    );
  }

  if (!items || items.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No cost data available
      </div>
    );
  }

  const getConfidenceBadge = (confidence) => {
    if (confidence >= 0.95) {
      return <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
        {(confidence * 100).toFixed(0)}%
      </span>;
    } else if (confidence >= 0.90) {
      return <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded">
        {(confidence * 100).toFixed(0)}%
      </span>;
    } else {
      return <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded">
        {(confidence * 100).toFixed(0)}%
      </span>;
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Element</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quantity</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Unit Rate</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Material</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Labor</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Equipment</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Confidence</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {items.map((item, idx) => (
            <tr key={idx} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {item.element_name}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {item.quantity} {item.unit}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ₹{item.unit_rate.toLocaleString('en-IN')}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ₹{item.material_cost.toLocaleString('en-IN')}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ₹{item.labor_cost.toLocaleString('en-IN')}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ₹{item.equipment_cost.toLocaleString('en-IN')}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                ₹{item.total_cost.toLocaleString('en-IN')}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm">
                {getConfidenceBadge(item.confidence)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
