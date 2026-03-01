export default function CostDistributionChart({ costSummary, loading }) {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-pulse">
          <div className="w-48 h-48 bg-gray-200 rounded-full"></div>
        </div>
      </div>
    );
  }

  if (!costSummary) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        No data available
      </div>
    );
  }

  const total = costSummary.total_cost;
  const materialPct = ((costSummary.material_cost / total) * 100).toFixed(1);
  const laborPct = ((costSummary.labor_cost / total) * 100).toFixed(1);
  const equipmentPct = ((costSummary.equipment_cost / total) * 100).toFixed(1);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-center">
        <svg viewBox="0 0 200 200" className="w-48 h-48">
          <circle cx="100" cy="100" r="80" fill="none" stroke="#e5e7eb" strokeWidth="40" />
          <circle
            cx="100"
            cy="100"
            r="80"
            fill="none"
            stroke="#3b82f6"
            strokeWidth="40"
            strokeDasharray={`${(materialPct / 100) * 502.4} 502.4`}
            transform="rotate(-90 100 100)"
          />
          <circle
            cx="100"
            cy="100"
            r="80"
            fill="none"
            stroke="#10b981"
            strokeWidth="40"
            strokeDasharray={`${(laborPct / 100) * 502.4} 502.4`}
            strokeDashoffset={`-${(materialPct / 100) * 502.4}`}
            transform="rotate(-90 100 100)"
          />
          <circle
            cx="100"
            cy="100"
            r="80"
            fill="none"
            stroke="#f59e0b"
            strokeWidth="40"
            strokeDasharray={`${(equipmentPct / 100) * 502.4} 502.4`}
            strokeDashoffset={`-${((materialPct + laborPct) / 100) * 502.4}`}
            transform="rotate(-90 100 100)"
          />
        </svg>
      </div>
      
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
            <span className="text-sm text-gray-600">Material</span>
          </div>
          <span className="text-sm font-medium text-gray-900">{materialPct}%</span>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
            <span className="text-sm text-gray-600">Labor</span>
          </div>
          <span className="text-sm font-medium text-gray-900">{laborPct}%</span>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-amber-500 rounded-full mr-2"></div>
            <span className="text-sm text-gray-600">Equipment</span>
          </div>
          <span className="text-sm font-medium text-gray-900">{equipmentPct}%</span>
        </div>
      </div>
    </div>
  );
}
