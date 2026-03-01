export default function PaymentMilestones({ milestones, onUpdateMilestone, isFinalized }) {
  if (!milestones || milestones.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No payment milestones defined
      </div>
    );
  }

  const totalPercentage = milestones.reduce((sum, m) => sum + m.percentage, 0);

  return (
    <div className="space-y-4">
      {milestones.map((milestone) => (
        <div key={milestone.id} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
          <div className="flex justify-between items-start mb-3">
            <div>
              <h4 className="text-sm font-medium text-gray-900">{milestone.name}</h4>
              <p className="text-xs text-gray-500 mt-1">{milestone.percentage}% of total</p>
              <p className="text-xs text-gray-500">Due: Day {milestone.due_day}</p>
            </div>
            <div className="text-right">
              <p className="text-lg font-bold text-gray-900">
                ₹{milestone.amount.toLocaleString('en-IN')}
              </p>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex-1 mr-4">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    milestone.status === 'Completed' ? 'bg-green-600' :
                    milestone.status === 'Partial' ? 'bg-yellow-600' :
                    'bg-gray-400'
                  }`}
                  style={{ width: `${milestone.percentage}%` }}
                ></div>
              </div>
            </div>

            {isFinalized ? (
              <span className={`px-2 py-1 text-xs font-medium rounded ${
                milestone.status === 'Completed' ? 'bg-green-100 text-green-800' :
                milestone.status === 'Partial' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {milestone.status}
              </span>
            ) : (
              <select
                value={milestone.status}
                onChange={(e) => onUpdateMilestone(milestone.id, { status: e.target.value })}
                className="px-2 py-1 text-xs border border-gray-300 rounded"
              >
                <option value="Pending">Pending</option>
                <option value="Partial">Partial</option>
                <option value="Completed">Completed</option>
              </select>
            )}
          </div>
        </div>
      ))}

      <div className="pt-4 border-t border-gray-300">
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium text-gray-700">Total Milestones</span>
          <span className={`text-lg font-bold ${totalPercentage === 100 ? 'text-green-600' : 'text-red-600'}`}>
            {totalPercentage}%
          </span>
        </div>
        {totalPercentage !== 100 && (
          <p className="text-xs text-red-600 mt-1">⚠ Warning: Total must equal 100%</p>
        )}
      </div>
    </div>
  );
}
