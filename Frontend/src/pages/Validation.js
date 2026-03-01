import Card from '../components/Card';
import Button from '../components/Button';
import ValidationSummary from '../components/ValidationSummary';
import ValidationTable from '../components/ValidationTable';
import ConfidenceChart from '../components/ConfidenceChart';
import ValidationMetrics from '../components/ValidationMetrics';
import { useProjectStore } from '../hooks/useProjectStore';
import { useValidation } from '../hooks/useValidation';
import { exportValidationReport } from '../services/validationEngine';

export default function Validation() {
  const { qtoElements, costItems, processingStatus } = useProjectStore();
  const { 
    validationData, 
    loading, 
    updateElementApproval, 
    updateElementOverride, 
    approveAllHighConfidence 
  } = useValidation(qtoElements, costItems, processingStatus);

  const handleExportCSV = () => {
    if (validationData) {
      exportValidationReport(validationData, 'csv');
    }
  };

  const handleExportJSON = () => {
    if (validationData) {
      exportValidationReport(validationData, 'json');
    }
  };

  if (processingStatus !== 'complete') {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-xl text-gray-600 mb-2">Complete QTO extraction to enable validation.</p>
          <p className="text-sm text-gray-500">Upload and process drawings first.</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-brand-charcoal mb-2">Validation & Confidence</h1>
          <p className="text-text-secondary">
            {loading ? 'Analyzing validation...' : 'Quality checks and confidence scoring'}
          </p>
        </div>
        <div className="flex space-x-2">
          <Button 
            onClick={approveAllHighConfidence} 
            disabled={loading || !validationData}
          >
            Approve All High Confidence
          </Button>
          <Button onClick={handleExportCSV} disabled={loading || !validationData}>
            Export CSV
          </Button>
          <Button onClick={handleExportJSON} variant="outline" disabled={loading || !validationData}>
            Export JSON
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
        <ValidationSummary 
          title="Avg Confidence" 
          value={validationData ? `${(validationData.summary.average_confidence * 100).toFixed(1)}%` : '0%'}
          loading={loading}
        />
        <ValidationSummary 
          title="High Confidence" 
          value={validationData?.summary.high_confidence || 0}
          loading={loading}
        />
        <ValidationSummary 
          title="Medium Confidence" 
          value={validationData?.summary.medium_confidence || 0}
          loading={loading}
        />
        <ValidationSummary 
          title="Low Confidence" 
          value={validationData?.summary.low_confidence || 0}
          loading={loading}
        />
        <ValidationSummary 
          title="Needs Review" 
          value={validationData?.summary.needs_review || 0}
          loading={loading}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card title="Confidence Distribution">
          <ConfidenceChart summary={validationData?.summary} loading={loading} />
        </Card>

        <Card title="Validation Metrics">
          <ValidationMetrics metrics={validationData?.metrics} loading={loading} />
        </Card>

        <Card title="Category Heatmap">
          {loading ? (
            <div className="animate-pulse space-y-3">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="h-12 bg-gray-200 rounded"></div>
              ))}
            </div>
          ) : validationData ? (
            <div className="space-y-3">
              {['Foundation', 'Structural', 'Walls', 'Finishing'].map(category => {
                const categoryElements = validationData.elements.filter(e => e.category === category);
                const avgConfidence = categoryElements.length > 0
                  ? categoryElements.reduce((sum, e) => sum + e.confidence, 0) / categoryElements.length
                  : 0;
                const confidencePct = (avgConfidence * 100).toFixed(0);
                
                let bgColor = 'bg-green-100';
                let textColor = 'text-green-800';
                if (avgConfidence < 0.90) {
                  bgColor = 'bg-red-100';
                  textColor = 'text-red-800';
                } else if (avgConfidence < 0.95) {
                  bgColor = 'bg-yellow-100';
                  textColor = 'text-yellow-800';
                }

                return (
                  <div key={category} className={`p-3 rounded-lg ${bgColor}`}>
                    <div className="flex justify-between items-center">
                      <span className={`text-sm font-medium ${textColor}`}>{category}</span>
                      <span className={`text-lg font-bold ${textColor}`}>{confidencePct}%</span>
                    </div>
                    <div className="mt-2 text-xs text-gray-600">
                      {categoryElements.length} elements
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">No data</div>
          )}
        </Card>
      </div>

      {validationData?.crossValidation && validationData.crossValidation.length > 0 && (
        <Card title="Cross-Validation Checks" className="mb-8">
          <div className="space-y-3">
            {validationData.crossValidation.map((check, idx) => (
              <div key={idx} className="flex items-start justify-between p-4 bg-amber-50 border border-amber-200 rounded-lg">
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900">{check.check}</h4>
                  <p className="text-sm text-gray-600 mt-1">{check.message}</p>
                </div>
                <span className={`px-2 py-1 text-xs font-medium rounded ${
                  check.status === 'Warning' ? 'bg-yellow-100 text-yellow-800' : 'bg-blue-100 text-blue-800'
                }`}>
                  {check.status}
                </span>
              </div>
            ))}
          </div>
        </Card>
      )}

      <Card title="Element Validation">
        <ValidationTable 
          elements={validationData?.elements || []} 
          loading={loading}
          onApprove={updateElementApproval}
          onOverride={updateElementOverride}
        />
      </Card>
    </div>
  );
}
