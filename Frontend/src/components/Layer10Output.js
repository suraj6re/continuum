export default function Layer10Output({ data }) {
  if (!data || !data.tasks || data.tasks.length === 0) {
    return (
      <div>
        <h3 className="text-xl font-bold text-brand-charcoal mb-4">Layer 10 - Explainable Scheduling</h3>
        <div className="bg-bg-section p-6 rounded-lg text-center text-text-secondary">
          No scheduling data available
        </div>
      </div>
    );
  }

  const criticalTasks = data.tasks.filter(task => task.is_critical);
  const nonCriticalTasks = data.tasks.filter(task => !task.is_critical);

  return (
    <div>
      <h3 className="text-xl font-bold text-brand-charcoal mb-4">Layer 10 - Explainable Scheduling</h3>
      <p className="text-text-secondary mb-6">
        CPM-based project scheduling with critical path analysis, task dependencies, and Gantt chart visualization.
      </p>

      {/* Project Summary */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-white border border-border-light rounded-lg p-4 shadow-sm">
          <div className="text-text-secondary text-sm mb-1">Project Duration</div>
          <div className="text-2xl font-bold text-brand-charcoal">{data.project_duration_days} days</div>
        </div>
        <div className="bg-white border border-border-light rounded-lg p-4 shadow-sm">
          <div className="text-text-secondary text-sm mb-1">Total Tasks</div>
          <div className="text-2xl font-bold text-brand-charcoal">{data.total_tasks}</div>
        </div>
        <div className="bg-white border border-border-light rounded-lg p-4 shadow-sm">
          <div className="text-text-secondary text-sm mb-1">Critical Tasks</div>
          <div className="text-2xl font-bold text-red-600">{data.critical_tasks_count}</div>
        </div>
        <div className="bg-white border border-border-light rounded-lg p-4 shadow-sm">
          <div className="text-text-secondary text-sm mb-1">Non-Critical Tasks</div>
          <div className="text-2xl font-bold text-green-600">{data.total_tasks - data.critical_tasks_count}</div>
        </div>
      </div>

      {/* Critical Path */}
      {data.critical_path && data.critical_path.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <h4 className="text-sm font-semibold text-red-900 mb-3">🔴 Critical Path</h4>
          <div className="flex items-center gap-2 flex-wrap">
            {data.critical_path.map((task, index) => (
              <div key={index} className="flex items-center">
                <span className="px-3 py-1 bg-red-600 text-white rounded text-sm font-medium">
                  {task}
                </span>
                {index < data.critical_path.length - 1 && (
                  <span className="mx-2 text-red-600 font-bold">→</span>
                )}
              </div>
            ))}
          </div>
          <p className="text-xs text-red-800 mt-3">
            These tasks have zero float and directly impact project completion time. Any delay in these tasks will delay the entire project.
          </p>
        </div>
      )}

      {/* Gantt Chart Visualization */}
      <div className="bg-white border border-border-light rounded-lg p-6 shadow-sm mb-6">
        <h4 className="text-sm font-semibold text-brand-charcoal mb-4">📊 Gantt Chart</h4>
        <div className="space-y-3">
          {data.tasks.map((task, index) => {
            const totalDuration = data.project_duration_days;
            const startPercent = (task.early_start / totalDuration) * 100;
            const widthPercent = (task.duration_days / totalDuration) * 100;
            
            return (
              <div key={index} className="relative">
                <div className="flex items-center mb-1">
                  <div className="w-48 text-sm font-medium text-brand-charcoal truncate" title={task.task_name}>
                    {task.task_name}
                  </div>
                  <div className="flex-1 relative h-8 bg-gray-100 rounded">
                    <div
                      className={`absolute h-full rounded flex items-center justify-center text-xs font-medium text-white ${
                        task.is_critical ? 'bg-red-600' : 'bg-blue-500'
                      }`}
                      style={{
                        left: `${startPercent}%`,
                        width: `${widthPercent}%`
                      }}
                    >
                      {task.duration_days}d
                    </div>
                  </div>
                  <div className="w-24 text-right text-xs text-text-secondary ml-2">
                    Day {task.early_start}-{task.early_finish}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        <div className="flex justify-between mt-4 text-xs text-text-secondary">
          <span>Day 0</span>
          <span>Day {data.project_duration_days}</span>
        </div>
      </div>

      {/* Task Details Table */}
      <div className="bg-white border border-border-light rounded-lg p-6 shadow-sm mb-6">
        <h4 className="text-sm font-semibold text-brand-charcoal mb-4">📋 Task Details</h4>
        
        {/* Critical Tasks */}
        {criticalTasks.length > 0 && (
          <div className="mb-6">
            <h5 className="text-xs font-semibold text-red-600 mb-3 uppercase">Critical Tasks (Zero Float)</h5>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-red-50">
                  <tr>
                    <th className="text-left p-2 font-semibold text-text-secondary">Task</th>
                    <th className="text-right p-2 font-semibold text-text-secondary">Quantity</th>
                    <th className="text-right p-2 font-semibold text-text-secondary">Duration</th>
                    <th className="text-right p-2 font-semibold text-text-secondary">ES</th>
                    <th className="text-right p-2 font-semibold text-text-secondary">EF</th>
                    <th className="text-right p-2 font-semibold text-text-secondary">LS</th>
                    <th className="text-right p-2 font-semibold text-text-secondary">LF</th>
                    <th className="text-right p-2 font-semibold text-text-secondary">Float</th>
                  </tr>
                </thead>
                <tbody>
                  {criticalTasks.map((task, idx) => (
                    <tr key={idx} className="border-t border-red-100">
                      <td className="p-2 font-medium text-brand-charcoal">{task.task_name}</td>
                      <td className="p-2 text-right">{task.quantity} {task.unit}</td>
                      <td className="p-2 text-right font-semibold">{task.duration_days}d</td>
                      <td className="p-2 text-right">{task.early_start}</td>
                      <td className="p-2 text-right">{task.early_finish}</td>
                      <td className="p-2 text-right">{task.late_start || task.early_start}</td>
                      <td className="p-2 text-right">{task.late_finish || task.early_finish}</td>
                      <td className="p-2 text-right">
                        <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs font-bold">
                          {task.float || 0}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Non-Critical Tasks */}
        {nonCriticalTasks.length > 0 && (
          <div>
            <h5 className="text-xs font-semibold text-green-600 mb-3 uppercase">Non-Critical Tasks (Has Float)</h5>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-green-50">
                  <tr>
                    <th className="text-left p-2 font-semibold text-text-secondary">Task</th>
                    <th className="text-right p-2 font-semibold text-text-secondary">Quantity</th>
                    <th className="text-right p-2 font-semibold text-text-secondary">Duration</th>
                    <th className="text-right p-2 font-semibold text-text-secondary">ES</th>
                    <th className="text-right p-2 font-semibold text-text-secondary">EF</th>
                    <th className="text-right p-2 font-semibold text-text-secondary">LS</th>
                    <th className="text-right p-2 font-semibold text-text-secondary">LF</th>
                    <th className="text-right p-2 font-semibold text-text-secondary">Float</th>
                  </tr>
                </thead>
                <tbody>
                  {nonCriticalTasks.map((task, idx) => (
                    <tr key={idx} className="border-t border-green-100">
                      <td className="p-2 font-medium text-brand-charcoal">{task.task_name}</td>
                      <td className="p-2 text-right">{task.quantity} {task.unit}</td>
                      <td className="p-2 text-right font-semibold">{task.duration_days}d</td>
                      <td className="p-2 text-right">{task.early_start}</td>
                      <td className="p-2 text-right">{task.early_finish}</td>
                      <td className="p-2 text-right">{task.late_start || task.early_start}</td>
                      <td className="p-2 text-right">{task.late_finish || task.early_finish}</td>
                      <td className="p-2 text-right">
                        <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-bold">
                          {task.float || 0}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="bg-bg-section p-4 rounded-lg">
        <h4 className="text-sm font-semibold text-brand-charcoal mb-3">📖 Legend</h4>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-semibold">ES:</span> Early Start - Earliest time a task can start
          </div>
          <div>
            <span className="font-semibold">EF:</span> Early Finish - Earliest time a task can finish
          </div>
          <div>
            <span className="font-semibold">LS:</span> Late Start - Latest time a task can start without delaying project
          </div>
          <div>
            <span className="font-semibold">LF:</span> Late Finish - Latest time a task can finish without delaying project
          </div>
          <div>
            <span className="font-semibold">Float:</span> Slack time available (LS - ES or LF - EF)
          </div>
          <div>
            <span className="font-semibold">Critical Path:</span> Tasks with zero float that determine project duration
          </div>
        </div>
      </div>
    </div>
  );
}
