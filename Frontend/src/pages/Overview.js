import Card from '../components/Card';
import Badge from '../components/Badge';

export default function Overview() {
  const stats = [
    { label: 'Active Projects', value: '12', change: '+3'},
    { label: 'Total Drawings', value: '48', change: '+8'},
    { label: 'Cost Estimates', value: '₹2.4M', change: '+12%'},
    { label: 'Avg Confidence', value: '94%', change: '+2%'},
  ];

  const recentProjects = [
    { name: 'Highway Bridge Construction', status: 'In Progress', confidence: 96, date: '2024-01-15' },
    { name: 'Residential Complex Phase 2', status: 'Completed', confidence: 98, date: '2024-01-10' },
    { name: 'Commercial Plaza Foundation', status: 'In Progress', confidence: 92, date: '2024-01-08' },
  ];

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-brand-charcoal mb-2">Overview</h1>
        <p className="text-text-secondary">Your construction intelligence dashboard</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, idx) => (
          <Card key={idx}>
            <div className="flex items-start justify-between">
              <div>
                <p className="text-text-secondary text-sm mb-1">{stat.label}</p>
                <p className="text-3xl font-bold text-brand-charcoal">{stat.value}</p>
                <p className="text-emerald-600 text-sm mt-1">{stat.change}</p>
              </div>
              <div className="text-3xl">{stat.icon}</div>
            </div>
          </Card>
        ))}
      </div>

      <Card title="Recent Projects">
        <div className="space-y-4">
          {recentProjects.map((project, idx) => (
            <div key={idx} className="flex items-center justify-between p-4 bg-bg-section rounded-lg">
              <div className="flex-1">
                <h4 className="font-semibold text-brand-charcoal">{project.name}</h4>
                <p className="text-sm text-text-secondary">{project.date}</p>
              </div>
              <div className="flex items-center space-x-4">
                <Badge variant={project.status === 'Completed' ? 'success' : 'warning'}>
                  {project.status}
                </Badge>
                <div className="text-right">
                  <p className="text-sm text-text-secondary">Confidence</p>
                  <p className="font-semibold text-brand-orange">{project.confidence}%</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
