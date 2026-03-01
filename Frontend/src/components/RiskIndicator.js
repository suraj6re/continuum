export default function RiskIndicator({ riskLevel, loading }) {
  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="h-24 bg-gray-200 rounded"></div>
      </div>
    );
  }

  const riskConfig = {
    Low: {
      color: 'bg-green-100 border-green-300',
      textColor: 'text-green-800',
      icon: '✓',
      message: 'Low risk scenario with conservative parameters'
    },
    Medium: {
      color: 'bg-yellow-100 border-yellow-300',
      textColor: 'text-yellow-800',
      icon: '⚠',
      message: 'Moderate risk - monitor execution closely'
    },
    High: {
      color: 'bg-red-100 border-red-300',
      textColor: 'text-red-800',
      icon: '⚠',
      message: 'High risk - aggressive optimization may impact quality'
    }
  };

  const config = riskConfig[riskLevel] || riskConfig.Low;

  return (
    <div className={`p-6 rounded-lg border-2 ${config.color}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center">
          <span className="text-3xl mr-3">{config.icon}</span>
          <div>
            <p className="text-sm font-medium text-gray-700">Risk Level</p>
            <p className={`text-2xl font-bold ${config.textColor}`}>{riskLevel}</p>
          </div>
        </div>
      </div>
      <p className="text-sm text-gray-600">{config.message}</p>
      
      <div className="mt-4 pt-4 border-t border-gray-300">
        <p className="text-xs text-gray-600 font-medium mb-2">Risk Factors:</p>
        <ul className="text-xs text-gray-600 space-y-1">
          <li>• Productivity assumptions</li>
          <li>• Resource availability</li>
          <li>• Schedule compression</li>
          <li>• Cost escalation</li>
        </ul>
      </div>
    </div>
  );
}
