import Card from '../components/Card';
import ProgressBar from '../components/ProgressBar';
import Badge from '../components/Badge';

export default function Validation() {
  const validationChecks = [
    { check: 'Dimension Consistency', status: 'Passed', confidence: 98, issues: 0 },
    { check: 'Plan-Section Alignment', status: 'Passed', confidence: 96, issues: 0 },
    { check: 'Symbol Recognition', status: 'Warning', confidence: 92, issues: 2 },
    { check: 'Text Extraction', status: 'Passed', confidence: 95, issues: 0 },
    { check: 'Quantity Logic', status: 'Passed', confidence: 97, issues: 0 },
  ];

  const outliers = [
    { element: 'Column C-12', issue: 'Dimension mismatch between plan and section', severity: 'Medium' },
    { element: 'Beam B-8', issue: 'Reinforcement quantity outside typical range', severity: 'Low' },
  ];

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-brand-charcoal mb-2">Validation & Confidence</h1>
        <p className="text-text-secondary">Quality checks and confidence scoring</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <p className="text-text-secondary text-sm mb-2">Overall Confidence</p>
          <p className="text-4xl font-bold text-brand-charcoal mb-4">95.6%</p>
          <ProgressBar value={95.6} showLabel={false} />
        </Card>
        <Card>
          <p className="text-text-secondary text-sm mb-1">Validation Checks</p>
          <p className="text-4xl font-bold text-emerald-600">18/20</p>
          <p className="text-sm text-text-secondary mt-2">Passed</p>
        </Card>
        <Card>
          <p className="text-text-secondary text-sm mb-1">Issues Found</p>
          <p className="text-4xl font-bold text-brand-orange">2</p>
          <p className="text-sm text-text-secondary mt-2">Needs review</p>
        </Card>
      </div>

      <Card title="Validation Checks" className="mb-6">
        <div className="space-y-4">
          {validationChecks.map((check, idx) => (
            <div key={idx} className="flex items-center justify-between p-4 bg-bg-section rounded-lg">
              <div className="flex-1">
                <h4 className="font-semibold text-brand-charcoal">{check.check}</h4>
                <div className="mt-2 w-64">
                  <ProgressBar value={check.confidence} showLabel={false} />
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <p className="text-sm text-text-secondary">Confidence</p>
                  <p className="font-semibold text-brand-charcoal">{check.confidence}%</p>
                </div>
                <Badge variant={check.status === 'Passed' ? 'success' : 'warning'}>
                  {check.status}
                </Badge>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {outliers.length > 0 && (
        <Card title="Issues Requiring Review">
          <div className="space-y-3">
            {outliers.map((outlier, idx) => (
              <div key={idx} className="flex items-start justify-between p-4 bg-amber-50 border border-amber-200 rounded-lg">
                <div className="flex-1">
                  <h4 className="font-semibold text-brand-charcoal">{outlier.element}</h4>
                  <p className="text-sm text-text-secondary mt-1">{outlier.issue}</p>
                </div>
                <Badge variant={outlier.severity === 'High' ? 'error' : outlier.severity === 'Medium' ? 'warning' : 'info'}>
                  {outlier.severity}
                </Badge>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
