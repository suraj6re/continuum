export default function ParetoChart({ points, loading }) {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-pulse w-full h-full bg-gray-200 rounded"></div>
      </div>
    );
  }

  if (!points || points.length === 0) {
    return (
      <div className="flex items-center justify-center h-96 text-gray-500">
        No data available
      </div>
    );
  }

  const maxDuration = Math.max(...points.map(p => p.duration));
  const minDuration = Math.min(...points.map(p => p.duration));
  const maxCost = Math.max(...points.map(p => p.cost));
  const minCost = Math.min(...points.map(p => p.cost));

  const chartWidth = 600;
  const chartHeight = 400;
  const padding = 60;

  const scaleX = (duration) => {
    return padding + ((duration - minDuration) / (maxDuration - minDuration)) * (chartWidth - 2 * padding);
  };

  const scaleY = (cost) => {
    return chartHeight - padding - ((cost - minCost) / (maxCost - minCost)) * (chartHeight - 2 * padding);
  };

  return (
    <div className="overflow-x-auto">
      <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="w-full h-96">
        {/* Axes */}
        <line x1={padding} y1={chartHeight - padding} x2={chartWidth - padding} y2={chartHeight - padding} stroke="#d1d5db" strokeWidth="2" />
        <line x1={padding} y1={padding} x2={padding} y2={chartHeight - padding} stroke="#d1d5db" strokeWidth="2" />

        {/* Axis labels */}
        <text x={chartWidth / 2} y={chartHeight - 10} textAnchor="middle" className="text-xs fill-gray-600">
          Duration (days)
        </text>
        <text x={20} y={chartHeight / 2} textAnchor="middle" transform={`rotate(-90 20 ${chartHeight / 2})`} className="text-xs fill-gray-600">
          Cost (₹)
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
            <line
              x1={padding + ratio * (chartWidth - 2 * padding)}
              y1={padding}
              x2={padding + ratio * (chartWidth - 2 * padding)}
              y2={chartHeight - padding}
              stroke="#f3f4f6"
              strokeWidth="1"
            />
          </g>
        ))}

        {/* Points */}
        {points.map((point, idx) => {
          const x = scaleX(point.duration);
          const y = scaleY(point.cost);
          
          let color = '#3b82f6';
          let radius = 6;
          
          if (point.type === 'baseline') {
            color = '#6b7280';
            radius = 8;
          } else if (point.type === 'optimal') {
            color = '#10b981';
            radius = 10;
          }

          return (
            <g key={idx}>
              <circle cx={x} cy={y} r={radius} fill={color} opacity="0.8" />
              <text x={x} y={y - 15} textAnchor="middle" className="text-xs fill-gray-700 font-medium">
                {point.label}
              </text>
            </g>
          );
        })}

        {/* Legend */}
        <g transform={`translate(${chartWidth - 150}, ${padding})`}>
          <circle cx="10" cy="10" r="6" fill="#6b7280" />
          <text x="25" y="15" className="text-xs fill-gray-700">Baseline</text>
          
          <circle cx="10" cy="35" r="6" fill="#3b82f6" />
          <text x="25" y="40" className="text-xs fill-gray-700">Scenario</text>
          
          <circle cx="10" cy="60" r="8" fill="#10b981" />
          <text x="25" y="65" className="text-xs fill-gray-700">Optimal</text>
        </g>
      </svg>
    </div>
  );
}
