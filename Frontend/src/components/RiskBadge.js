export default function RiskBadge({ supplier }) {
  if (!supplier || !supplier.risk) {
    return null;
  }

  const { riskLevel, riskFactors } = supplier.risk;

  const config = {
    Low: {
      bg: 'bg-green-100',
      border: 'border-green-300',
      text: 'text-green-800',
      icon: '✓'
    },
    Medium: {
      bg: 'bg-yellow-100',
      border: 'border-yellow-300',
      text: 'text-yellow-800',
      icon: '⚠'
    },
    High: {
      bg: 'bg-red-100',
      border: 'border-red-300',
      text: 'text-red-800',
      icon: '⚠'
    }
  };

  const style = config[riskLevel] || config.Low;

  return (
    <div className={`p-4 rounded-lg border ${style.bg} ${style.border}`}>
      <div className="flex items-center mb-2">
        <span className="text-2xl mr-2">{style.icon}</span>
        <div>
          <p className="text-xs font-medium text-gray-600">Risk Level</p>
          <p className={`text-lg font-bold ${style.text}`}>{riskLevel}</p>
        </div>
      </div>
      
      {riskFactors && riskFactors.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-300">
          <p className="text-xs font-medium text-gray-600 mb-1">Risk Factors:</p>
          <ul className="text-xs text-gray-600 space-y-1">
            {riskFactors.map((factor, idx) => (
              <li key={idx}>• {factor}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
