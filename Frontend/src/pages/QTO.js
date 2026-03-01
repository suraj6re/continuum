import { useEffect } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import QTOSummaryCard from '../components/QTOSummaryCard';
import QTOTable from '../components/QTOTable';
import { useProjectStore } from '../hooks/useProjectStore';
import { exportQTOToCSV, exportQTOToJSON } from '../services/qtoService';

export default function QTO() {
  const { qtoSummary, qtoElements, processingStatus } = useProjectStore();

  const isLoading = processingStatus === 'processing';
  const isComplete = processingStatus === 'complete';

  const handleExportCSV = () => {
    exportQTOToCSV(qtoElements);
  };

  const handleExportJSON = () => {
    exportQTOToJSON({ summary: qtoSummary, elements: qtoElements });
  };

  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-brand-charcoal mb-2">Quantity Take-Off</h1>
          <p className="text-text-secondary">
            {isLoading ? 'AI extracting quantities...' : 'AI-extracted quantities from construction drawings'}
          </p>
        </div>
        <div className="flex space-x-2">
          <Button onClick={handleExportCSV} disabled={!isComplete || qtoElements.length === 0}>
            Export CSV
          </Button>
          <Button onClick={handleExportJSON} variant="outline" disabled={!isComplete || qtoElements.length === 0}>
            Export JSON
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <QTOSummaryCard 
          title="Total Elements" 
          value={qtoSummary?.total_elements || 0}
          loading={isLoading}
        />
        <QTOSummaryCard 
          title="Avg Confidence" 
          value={qtoSummary ? `${(qtoSummary.average_confidence * 100).toFixed(0)}%` : '0%'}
          loading={isLoading}
        />
        <QTOSummaryCard 
          title="High Confidence" 
          value={qtoSummary?.high_confidence || 0}
          loading={isLoading}
        />
        <QTOSummaryCard 
          title="Needs Review" 
          value={qtoSummary?.needs_review || 0}
          loading={isLoading}
        />
      </div>

      <Card title="Extracted Quantities">
        <QTOTable elements={qtoElements} loading={isLoading} />
      </Card>
    </div>
  );
}
