import Card from '../components/Card';
import Button from '../components/Button';
import ProcurementSummary from '../components/ProcurementSummary';
import PurchaseOrderTable from '../components/PurchaseOrderTable';
import PaymentMilestones from '../components/PaymentMilestones';
import CashFlowChart from '../components/CashFlowChart';
import DeliveryTracker from '../components/DeliveryTracker';
import { useProjectStore } from '../hooks/useProjectStore';
import { useProcurement } from '../hooks/useProcurement';
import { useSchedule } from '../hooks/useSchedule';
import { generateCashFlowData, exportProcurementReport } from '../services/procurementEngine';

export default function Procurement() {
  const { qtoElements, selectedSupplier, processingStatus } = useProjectStore();
  const { tasks: scheduleTasks } = useSchedule(qtoElements, processingStatus);
  const {
    procurementItems,
    paymentMilestones,
    summary,
    risk,
    isFinalized,
    updateOrderStatus,
    updatePaymentStatus,
    updateMilestoneStatus,
    finalizeProcurement
  } = useProcurement(qtoElements, selectedSupplier, scheduleTasks);

  const handleExport = () => {
    const procurementData = {
      items: procurementItems,
      summary
    };
    exportProcurementReport(procurementData, selectedSupplier, paymentMilestones, risk);
  };

  const cashFlowData = generateCashFlowData(procurementItems, paymentMilestones);

  if (processingStatus !== 'complete') {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-xl text-gray-600 mb-2">Complete QTO to enable procurement planning.</p>
          <p className="text-sm text-gray-500">Upload and process drawings first.</p>
        </div>
      </div>
    );
  }

  if (!selectedSupplier) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-xl text-gray-600 mb-4">Select a supplier to initiate procurement.</p>
          <p className="text-sm text-gray-500 mb-6">Go to Suppliers page and select a supplier first.</p>
          <Button onClick={() => window.location.hash = '#suppliers'}>
            Go to Suppliers
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-brand-charcoal mb-2">Procurement Execution</h1>
          <p className="text-text-secondary">
            Supplier: <span className="font-semibold">{selectedSupplier.name}</span>
          </p>
        </div>
        <div className="flex space-x-2">
          <Button 
            onClick={finalizeProcurement} 
            disabled={isFinalized}
          >
            {isFinalized ? 'Plan Finalized' : 'Finalize Procurement Plan'}
          </Button>
          <Button onClick={handleExport} variant="outline">
            Export Report
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-6 gap-6 mb-8">
        <ProcurementSummary
          title="Total Procurement Value"
          value={`₹${(summary.total_value / 100000).toFixed(2)}L`}
          color="blue"
        />
        <ProcurementSummary
          title="Purchase Items"
          value={summary.total_items}
          color="gray"
        />
        <ProcurementSummary
          title="Pending Orders"
          value={summary.pending_orders}
          color="orange"
        />
        <ProcurementSummary
          title="Delivered Orders"
          value={summary.delivered_orders}
          color="green"
        />
        <ProcurementSummary
          title="Payment Due"
          value={`₹${(summary.payment_due / 100000).toFixed(2)}L`}
          color="red"
        />
        <ProcurementSummary
          title="Supplier Risk"
          value={risk?.riskLevel || 'Low'}
          color={risk?.riskLevel === 'High' ? 'red' : risk?.riskLevel === 'Medium' ? 'orange' : 'green'}
        />
      </div>

      {risk && risk.riskFactors && risk.riskFactors.length > 0 && (
        <div className="mb-8 p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-start">
            <span className="text-2xl mr-3">⚠</span>
            <div>
              <p className="text-sm font-medium text-yellow-900 mb-2">Procurement Risk Analysis - {risk.riskLevel} Risk</p>
              <ul className="text-sm text-yellow-800 space-y-1">
                {risk.riskFactors.map((factor, idx) => (
                  <li key={idx}>• {factor}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      <Card title="Purchase Orders" className="mb-8">
        <PurchaseOrderTable
          items={procurementItems}
          onUpdateOrder={updateOrderStatus}
          onUpdatePayment={updatePaymentStatus}
          isFinalized={isFinalized}
        />
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card title="Payment Milestones">
          <PaymentMilestones
            milestones={paymentMilestones}
            onUpdateStatus={updateMilestoneStatus}
            isFinalized={isFinalized}
          />
        </Card>

        <Card title="Delivery Tracker" className="md:col-span-2">
          <DeliveryTracker items={procurementItems} />
        </Card>
      </div>

      <Card title="Cash Flow Projection">
        <CashFlowChart cashFlowData={cashFlowData} loading={false} />
        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-900">
            <span className="font-semibold">Peak Payment Period:</span> Day {cashFlowData[cashFlowData.length - 1]?.day || 0}
          </p>
          <p className="text-sm text-blue-900 mt-1">
            <span className="font-semibold">Maximum Liquidity Required:</span> ₹{((cashFlowData[cashFlowData.length - 1]?.amount || 0) / 100000).toFixed(2)}L
          </p>
        </div>
      </Card>
    </div>
  );
}
