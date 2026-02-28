export default function ProgressBar({ value, max = 100, className = '', showLabel = true }) {
  const percentage = (value / max) * 100;
  
  return (
    <div className={className}>
      <div className="flex justify-between items-center mb-2">
        {showLabel && (
          <span className="text-sm font-medium text-text-secondary">{percentage.toFixed(0)}%</span>
        )}
      </div>
      <div className="w-full bg-bg-section rounded-full h-2 overflow-hidden">
        <div 
          className="bg-brand-orange h-full rounded-full transition-all duration-300"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
