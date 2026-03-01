export default function ScenarioComparison({ scenarios, onRemove }) {
  if (!scenarios || scenarios.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No saved scenarios. Adjust parameters and save scenarios to compare.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Scenario</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Duration</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Cost</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Labor Cost</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Material Cost</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Productivity</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Risk</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {scenarios.map((scenario) => (
            <tr key={scenario.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 text-sm font-medium text-gray-900">
                {scenario.name}
                <div className="text-xs text-gray-500 mt-1">{scenario.mode}</div>
              </td>
              <td className="px-6 py-4 text-sm text-gray-500">
                {scenario.results.optimized.duration} days
              </td>
              <td className="px-6 py-4 text-sm font-medium text-gray-900">
                ₹{scenario.results.optimized.total_cost.toLocaleString('en-IN')}
              </td>
              <td className="px-6 py-4 text-sm text-gray-500">
                ₹{scenario.results.optimized.labor_cost.toLocaleString('en-IN')}
              </td>
              <td className="px-6 py-4 text-sm text-gray-500">
                ₹{scenario.results.optimized.material_cost.toLocaleString('en-IN')}
              </td>
              <td className="px-6 py-4 text-sm text-gray-500">
                {scenario.variables.productivityMultiplier.toFixed(2)}x
              </td>
              <td className="px-6 py-4 text-sm">
                <span className={`px-2 py-1 text-xs font-medium rounded ${
                  scenario.risk === 'High' ? 'bg-red-100 text-red-800' :
                  scenario.risk === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {scenario.risk}
                </span>
              </td>
              <td className="px-6 py-4 text-sm">
                <button
                  onClick={() => onRemove(scenario.id)}
                  className="text-red-600 hover:text-red-800 text-xs"
                >
                  Remove
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
