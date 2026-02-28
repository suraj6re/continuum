import Card from '../components/Card';
import Button from '../components/Button';

export default function Reports() {
  const reports = [
    { name: 'Complete QTO Report', date: '2024-01-15', size: '2.4 MB', type: 'PDF' },
    { name: 'Cost Estimation Summary', date: '2024-01-15', size: '1.8 MB', type: 'PDF' },
    { name: 'Project Schedule', date: '2024-01-14', size: '1.2 MB', type: 'PDF' },
    { name: 'Validation Report', date: '2024-01-14', size: '890 KB', type: 'PDF' },
  ];

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-brand-charcoal mb-2">Reports</h1>
        <p className="text-text-secondary">Export compliance-ready documentation</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <p className="text-text-secondary text-sm mb-1">Total Reports</p>
          <p className="text-4xl font-bold text-brand-charcoal">12</p>
        </Card>
        <Card>
          <p className="text-text-secondary text-sm mb-1">This Month</p>
          <p className="text-4xl font-bold text-brand-orange">4</p>
        </Card>
        <Card>
          <p className="text-text-secondary text-sm mb-1">Compliance Status</p>
          <p className="text-4xl font-bold text-emerald-600">✓</p>
        </Card>
      </div>

      <Card title="Generate New Report" className="mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Button>Complete Project Report</Button>
          <Button variant="secondary">QTO Summary</Button>
          <Button variant="secondary">Cost Analysis</Button>
          <Button variant="secondary">Schedule Report</Button>
        </div>
      </Card>

      <Card title="Recent Reports">
        <div className="space-y-3">
          {reports.map((report, idx) => (
            <div key={idx} className="flex items-center justify-between p-4 bg-bg-section rounded-lg">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                  <span className="text-red-600 font-bold text-sm">PDF</span>
                </div>
                <div>
                  <h4 className="font-semibold text-brand-charcoal">{report.name}</h4>
                  <p className="text-sm text-text-secondary">{report.date} • {report.size}</p>
                </div>
              </div>
              <div className="flex space-x-2">
                <Button size="sm" variant="outline">View</Button>
                <Button size="sm">Download</Button>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card title="Compliance Summary">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-4 bg-emerald-50 rounded-lg border border-emerald-200">
            <h4 className="font-semibold text-emerald-700 mb-2">✓ Quality Standards</h4>
            <p className="text-sm text-emerald-600">All quality checks passed</p>
          </div>
          <div className="p-4 bg-emerald-50 rounded-lg border border-emerald-200">
            <h4 className="font-semibold text-emerald-700 mb-2">✓ Documentation</h4>
            <p className="text-sm text-emerald-600">Complete and compliant</p>
          </div>
        </div>
      </Card>
    </div>
  );
}
