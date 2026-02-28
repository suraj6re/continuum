import Card from '../components/Card';
import Badge from '../components/Badge';
import Button from '../components/Button';

export default function Schedule() {
  const tasks = [
    { name: 'Site Preparation', duration: '5 days', start: 'Week 1', status: 'Completed', critical: false },
    { name: 'Foundation Work', duration: '12 days', start: 'Week 2', status: 'In Progress', critical: true },
    { name: 'Structural Framework', duration: '18 days', start: 'Week 4', status: 'Pending', critical: true },
    { name: 'Masonry Work', duration: '15 days', start: 'Week 7', status: 'Pending', critical: false },
    { name: 'Plumbing & Electrical', duration: '10 days', start: 'Week 9', status: 'Pending', critical: false },
    { name: 'Finishing Work', duration: '14 days', start: 'Week 11', status: 'Pending', critical: false },
  ];

  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-brand-charcoal mb-2">Project Schedule</h1>
          <p className="text-text-secondary">AI-generated phase-wise construction schedule</p>
        </div>
        <Button>Export Schedule</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card>
          <p className="text-text-secondary text-sm mb-1">Total Duration</p>
          <p className="text-3xl font-bold text-brand-charcoal">84 days</p>
        </Card>
        <Card>
          <p className="text-text-secondary text-sm mb-1">Critical Path</p>
          <p className="text-3xl font-bold text-brand-orange">45 days</p>
        </Card>
        <Card>
          <p className="text-text-secondary text-sm mb-1">Total Tasks</p>
          <p className="text-3xl font-bold text-brand-charcoal">24</p>
        </Card>
        <Card>
          <p className="text-text-secondary text-sm mb-1">Completion</p>
          <p className="text-3xl font-bold text-emerald-600">18%</p>
        </Card>
      </div>

      <Card title="Task Timeline">
        <div className="space-y-4">
          {tasks.map((task, idx) => (
            <div key={idx} className="flex items-center justify-between p-4 bg-bg-section rounded-lg">
              <div className="flex-1">
                <div className="flex items-center space-x-3">
                  <h4 className="font-semibold text-brand-charcoal">{task.name}</h4>
                  {task.critical && (
                    <Badge variant="error">Critical Path</Badge>
                  )}
                </div>
                <p className="text-sm text-text-secondary mt-1">
                  {task.duration} • Starts {task.start}
                </p>
              </div>
              <Badge variant={
                task.status === 'Completed' ? 'success' : 
                task.status === 'In Progress' ? 'warning' : 'info'
              }>
                {task.status}
              </Badge>
            </div>
          ))}
        </div>
      </Card>

      <div className="mt-6">
        <Card title="Gantt Chart View">
          <div className="h-64 flex items-center justify-center bg-bg-section rounded-lg">
            <p className="text-text-muted">Interactive Gantt chart visualization</p>
          </div>
        </Card>
      </div>
    </div>
  );
}
