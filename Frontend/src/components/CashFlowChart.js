export default function CashFlowChart({ cashFlowData, loading }) {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-pulse w-full h-full bg-gray-200 rounded"></div>
      </div>
    );
  }

  if (!cashFlowData || cashFlowData.length === 0) {
    return (
      <div className="flex items-center justify-center h-96 text-gray-500">
        No cash flow data available
      </div>
    );
  }

  const maxDay = Math.max(...cashFlowData.map(d => d.day));
  const maxAmount = Math.max(...cashFlowData.map(d => d.amount));

  const chartWidth = 800;
  const chartHeight = 400;
  const padding = 60;

  const scaleX = (day) => {
    return padding + (day / maxDay) * (chartWidth - 2 * padding);
  };

  const scaleY = (amount) => {
    return chartHeight - padding - (amount / maxAmount) * (chartHeight - 2 * padding);
  };

  // Create path for line chart
  const pathData = cashFlowData
    .map((point, idx) => {
      const x = scaleX(point.day);
      const y = scaleY(point.amount);
      return `${idx === 0 ? 'M' : 'L'} ${x} ${y}`;
    })
    .join(' ');

  return (
    <div className="overflow-x-auto">
      <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="w-full h-96">
        {/* Axes */}
        <line x1={padding} y1={chartHeight - padding} x2={chartWidth - padding} y2={chartHeight - padding} stroke="#d1d5db" strokeWidth="2" />
        <line x1={padding} y1={padding} x2={padding} y2={chartHeight - padding} stroke="#d1d5db" strokeWidth="2" />

        {/* Axis labels */}
        <text x={chartWidth / 2} y={chartHeight - 10} textAnchor="middle" className="text-xs fill-gray-600">
          Timeline (Days)
        </text>
        <text x={20} y={chartHeight / 2} textAnchor="middle" transform={`rotate(-90 20 ${chartHeight / 2})`} className="text-xs fill-gray-600">
          Cumulative Cost (₹)
        </text>

        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((ratio, i) => (
          <g key={i}>
            <line
              x1={padding}
              y1={padding + ratio * (chartHeight - 2 * padding)}
              x2={chartWidth - padding}
              y2={padding + ratio * (chartHeight - 2 * padding)}
              stroke="#f3f4f6"
              strokeWidth="1"
            />
          </g>
        ))}

        {/* Area under curve */}
        <path
          d={`${pathData} L ${scaleX(maxDay)} ${chartHeight - padding} L ${padding} ${chartHeight - padding} Z`}
          fill="#3b82f6"
          opacity="0.2"
        />

        {/* Line */}
        <path
          d={pathData}
          fill="none"
          stroke="#3b82f6"
          strokeWidth="3"
        />

        {/* Points */}
        {cashFlowData.map((point, idx) => {
          const x = scaleX(point.day);
          const y = scaleY(point.amount);
          
          return (
            <g key={idx}>
              <circle cx={x} cy={y} r="5" fill="#3b82f6" />
              {idx % 3 === 0 && (
                <text x={x} y={y - 10} textAnchor="middle" className="text-xs fill-gray-700">
                  ₹{(point.amount / 100000).toFixed(1)}L
                </text>
              )}
            </g>
          );
        })}

        {/* Peak indicator */}
        {(() => {
          const peakPoint = cashFlowData[cashFlowData.length - 1];
          const x = scaleX(peakPoint.day);
          const y = scaleY(peakPoint.amount);
          return (
            <g>
              <circle cx={x} cy={y} r="8" fill="#ef4444" />
              <text x={x} y={y - 15} textAnchor="middle" className="text-xs fill-red-600 font-bold">
                Peak
              </text>
            </g>
          );
        })()}
      </svg>

      <div className="mt-4 flex items-center justify-center space-x-6 text-xs text-gray-600">
        <div className="flex items-center">
          <div className="w-4 h-4 bg-blue-500 rounded mr-2"></div>
          <span>Cumulative Outflow</span>
        </div>
        <div className="flex items-center">
          <div className="w-4 h-4 bg-red-500 rounded-full mr-2"></div>
          <span>Peak Payment</span>
        </div>
      </div>
    </div>
  );
}
