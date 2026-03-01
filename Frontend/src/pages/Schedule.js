import Card from '../components/Card';
import Button from '../components/Button';
import ScheduleSummary from '../components/ScheduleSummary';
import ProductivityPanel from '../components/ProductivityPanel';
import GanttChart from '../components/GanttChart';
import { useProjectStore } from '../hooks/useProjectStore';
import { useSchedule } from '../hooks/useSchedule';
import { exportScheduleToCSV, exportScheduleToJSON } from '../services/scheduleGenerator';

export default function Schedule() {
  const { qtoElements, processingStatus } = useProjectStore();
  const { tasks, summary, criticalPath, loading, updateProductivity } = useSchedule(qtoElements, processingStatus);

  const handleExportCSV = () => {
    exportScheduleToCSV(tasks, summary, {});
  };

  const handleExportJSON = () => {
    exportScheduleToJSON(tasks, summary, {});
  };

  if (processingStatus !== 'complete') {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-xl text-gray-600 mb-2">Complete QTO to generate schedule.</p>
          <p className="text-sm text-gray-500">Upload and process drawings first.</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-brand-charcoal mb-2">Project Schedule</h1>
          <p className="text-text-secondary">
            {loading ? 'Generating schedule...' : 'AI-generated phase-wise construction schedule'}
          </p>
        </div>
        <div className="flex space-x-2">
          <Button onClick={handleExportCSV} disabled={loading || tasks.length === 0}>
            Export CSV
          </Button>
          <Button onClick={handleExportJSON} variant="outline" disabled={loading || tasks.length === 0}>
            Export JSON
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <ScheduleSummary 
          title="Total Tasks" 
          value={summary.total_tasks}
          loading={loading}
        />
        <ScheduleSummary 
          title="Total Duration" 
          value={`${summary.total_duration} days`}
          loading={loading}
        />
        <ScheduleSummary 
          title="Structural Phase" 
          value={`${summary.structural_duration} days`}
          loading={loading}
        />
        <ScheduleSummary 
          title="Finishing Phase" 
          value={`${summary.finishing_duration} days`}
          loading={loading}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="md:col-span-3">
          <Card title="Gantt Chart">
            <GanttChart tasks={tasks} criticalPath={criticalPath} loading={loading} />
          </Card>
        </div>

        <Card title="Productivity Rates">
          <ProductivityPanel onProductivityChange={updateProductivity} loading={loading} />
        </Card>
      </div>

      <Card title="Task List">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Task</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Duration</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Start</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">End</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {tasks.map((task) => {
                const isCritical = criticalPath.has(task.id);
                return (
                  <tr key={task.id} className={isCritical ? 'bg-red-50' : 'hover:bg-gray-50'}>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {task.name}
                      {isCritical && (
                        <span className="ml-2 px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded">
                          Critical
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">{task.category}</td>
                    <td className="px-6 py-4 text-sm text-gray-500">{task.duration_days} days</td>
                    <td className="px-6 py-4 text-sm text-gray-500">Day {task.start_day}</td>
                    <td className="px-6 py-4 text-sm text-gray-500">Day {task.end_day}</td>
                    <td className="px-6 py-4 text-sm">
                      <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                        Planned
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
