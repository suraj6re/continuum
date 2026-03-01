export default function ValidationMetrics({ metrics, loading }) {
  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="h-12 bg-gray-200 rounded"></div>
        ))}
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="text-center py-8 text-gray-500">
        No metrics available
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
        <span className="text-sm font-medium text-gray-700">Total Elements</span>
        <span className="text-xl font-bold text-gray-900">{metrics.total_elements}</span>
      </div>

      <div className="flex justify-between items-center p-4 bg-green-50 rounded-lg">
        <span className="text-sm font-medium text-green-700">Elements Validated</span>
        <span className="text-xl font-bold text-green-900">{metrics.validated}</span>
      </div>

      <div className="flex justify-between items-center p-4 bg-red-50 rounded-lg">
        <span className="text-sm font-medium text-red-700">Elements Flagged</span>
        <span className="text-xl font-bold text-red-900">{metrics.flagged}</span>
      </div>

      <div className="flex justify-between items-center p-4 bg-purple-50 rounded-lg">
        <span className="text-sm font-medium text-purple-700">User Corrections</span>
        <span className="text-xl font-bold text-purple-900">{metrics.user_corrections}</span>
      </div>

      <div className="flex justify-between items-center p-4 bg-blue-50 rounded-lg border-2 border-blue-200">
        <span className="text-sm font-medium text-blue-700">Validation Coverage</span>
        <span className="text-2xl font-bold text-blue-900">{metrics.coverage_percent.toFixed(1)}%</span>
      </div>

      <div className="pt-4 border-t border-gray-200">
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className="bg-blue-600 h-3 rounded-full transition-all duration-500"
            style={{ width: `${metrics.coverage_percent}%` }}
          ></div>
        </div>
        <p className="text-xs text-gray-500 mt-2 text-center">
          Coverage = (Validated + Corrected) / Total
        </p>
      </div>
    </div>
  );
}
