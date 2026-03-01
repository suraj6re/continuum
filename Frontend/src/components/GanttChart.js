export default function GanttChart({ tasks, criticalPath, loading }) {
  if (loading) {
    return (
      <div className="h-96 flex items-center justify-center">
        <div className="animate-pulse w-full h-full bg-gray-200 rounded"></div>
      </div>
    );
  }

  if (!tasks || tasks.length === 0) {
    return (
      <div className="h-96 flex items-center justify-center text-gray-500">
        No tasks to display
      </div>
    );
  }

  const maxDay = Math.max(...tasks.map(t => t.end_day), 1);
  const dayWidth = Math.max(30, Math.min(50, 1200 / maxDay));

  const getCategoryColor = (category) => {
    switch (category) {
      case 'Foundation': return 'bg-purple-500';
      case 'Structural': return 'bg-blue-500';
      case 'Walls': return 'bg-orange-500';
      case 'Finishing': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="overflow-x-auto">
      <div className="min-w-max">
        {/* Timeline header */}
        <div className="flex items-center mb-4 pl-64">
          <div className="flex">
            {Array.from({ length: Math.ceil(maxDay / 7) + 1 }, (_, i) => (
              <div key={i} className="text-xs text-gray-600 font-medium" style={{ width: `${dayWidth * 7}px` }}>
                Week {i + 1}
              </div>
            ))}
          </div>
        </div>

        {/* Tasks */}
        <div className="space-y-2">
          {tasks.map((task) => {
            const isCritical = criticalPath.has(task.id);
            const barWidth = task.duration_days * dayWidth;
            const barLeft = task.start_day * dayWidth;

            return (
              <div key={task.id} className="flex items-center group">
                {/* Task name */}
                <div className="w-64 pr-4 text-sm text-gray-700 truncate" title={task.name}>
                  {task.name}
                </div>

                {/* Timeline */}
                <div className="flex-1 relative h-10">
                  <div
                    className={`absolute h-8 rounded ${getCategoryColor(task.category)} ${
                      isCritical ? 'ring-2 ring-red-500 ring-offset-1' : ''
                    } transition-all hover:opacity-80 cursor-pointer`}
                    style={{
                      left: `${barLeft}px`,
                      width: `${barWidth}px`
                    }}
                    title={`${task.name}\nDuration: ${task.duration_days} days\nStart: Day ${task.start_day}\nEnd: Day ${task.end_day}\nQuantity: ${task.quantity}\nProductivity: ${task.productivity}`}
                  >
                    <div className="flex items-center justify-center h-full text-white text-xs font-medium px-2">
                      {task.duration_days}d
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Legend */}
        <div className="flex items-center space-x-6 mt-6 pl-64 text-xs">
          <div className="flex items-center">
            <div className="w-4 h-4 bg-purple-500 rounded mr-2"></div>
            <span className="text-gray-600">Foundation</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-blue-500 rounded mr-2"></div>
            <span className="text-gray-600">Structural</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-orange-500 rounded mr-2"></div>
            <span className="text-gray-600">Walls</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-green-500 rounded mr-2"></div>
            <span className="text-gray-600">Finishing</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-gray-300 rounded ring-2 ring-red-500 mr-2"></div>
            <span className="text-gray-600">Critical Path</span>
          </div>
        </div>
      </div>
    </div>
  );
}
