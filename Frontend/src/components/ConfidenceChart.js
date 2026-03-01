export default function ConfidenceChart({ summary, loading }) {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-pulse">
          <div className="w-48 h-48 bg-gray-200 rounded-full"></div>
        </div>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        No data available
      </div>
    );
  }

  const total = summary.total || 1;
  const highPct = ((summary.high_confidence / total) * 100).toFixed(1);
  const mediumPct = ((summary.medium_confidence / total) * 100).toFixed(1);
  const lowPct = ((summary.low_confidence / total) * 100).toFixed(1);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-center">
        <svg viewBox="0 0 200 200" className="w-48 h-48">
          <circle cx="100" cy="100" r="80" fill="none" stroke="#e5e7eb" strokeWidth="40" />
          <circle
            cx="100"
            cy="100"
            r="80"
            fill="none"
            stroke="#10b981"
            strokeWidth="40"
            strokeDasharray={`${(highPct / 100) * 502.4} 502.4`}
            transform="rotate(-90 100 100)"
          />
          <circle
            cx="100"
            cy="100"
            r="80"
            fill="none"
            stroke="#f59e0b"
            strokeWidth="40"
            strokeDasharray={`${(mediumPct / 100) * 502.4} 502.4`}
            strokeDashoffset={`-${(highPct / 100) * 502.4}`}
            transform="rotate(-90 100 100)"
          />
          <circle
            cx="100"
            cy="100"
            r="80"
            fill="none"
            stroke="#ef4444"
            strokeWidth="40"
            strokeDasharray={`${(lowPct / 100) * 502.4} 502.4`}
            strokeDashoffset={`-${((highPct + mediumPct) / 100) * 502.4}`}
            transform="rotate(-90 100 100)"
          />
        </svg>
      </div>
      
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
            <span className="text-sm text-gray-600">High (≥95%)</span>
          </div>
          <span className="text-sm font-medium text-gray-900">
            {summary.high_confidence} ({highPct}%)
          </span>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-amber-500 rounded-full mr-2"></div>
            <span className="text-sm text-gray-600">Medium (90-95%)</span>
          </div>
          <span className="text-sm font-medium text-gray-900">
            {summary.medium_confidence} ({mediumPct}%)
          </span>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
            <span className="text-sm text-gray-600">Low (&lt;90%)</span>
          </div>
          <span className="text-sm font-medium text-gray-900">
            {summary.low_confidence} ({lowPct}%)
          </span>
        </div>
      </div>

      <div className="pt-4 border-t border-gray-200">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Average Confidence</span>
          <span className="text-lg font-bold text-gray-900">
            {(summary.average_confidence * 100).toFixed(1)}%
          </span>
        </div>
      </div>
    </div>
  );
}
