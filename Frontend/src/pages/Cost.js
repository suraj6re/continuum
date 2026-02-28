import Card from '../components/Card';
import Table from '../components/Table';
import Button from '../components/Button';

export default function Cost() {
  const costBreakdown = [
    { item: 'Concrete Works', quantity: '245.5 m³', rate: 8500, amount: 2086750, uncertainty: '±5%' },
    { item: 'Steel Reinforcement', quantity: '12450 kg', rate: 85, amount: 1058250, uncertainty: '±3%' },
    { item: 'Brick Masonry', quantity: '1850 m²', rate: 450, amount: 832500, uncertainty: '±4%' },
    { item: 'Plaster Work', quantity: '3200 m²', rate: 180, amount: 576000, uncertainty: '±6%' },
    { item: 'Floor Tiles', quantity: '1450 m²', rate: 650, amount: 942500, uncertainty: '±4%' },
  ];

  const columns = [
    { header: 'Item', accessor: 'item' },
    { header: 'Quantity', accessor: 'quantity' },
    { header: 'Rate (₹)', accessor: 'rate', render: (row) => `₹${row.rate.toLocaleString()}` },
    { header: 'Amount (₹)', accessor: 'amount', render: (row) => `₹${row.amount.toLocaleString()}` },
    { header: 'Uncertainty', accessor: 'uncertainty' },
  ];

  const totalCost = costBreakdown.reduce((sum, item) => sum + item.amount, 0);

  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-brand-charcoal mb-2">Cost Intelligence</h1>
          <p className="text-text-secondary">AI-powered cost estimation with uncertainty analysis</p>
        </div>
        <Button>Export Cost Report</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card className="md:col-span-2">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-text-secondary text-sm mb-2">Total Project Cost</p>
              <p className="text-5xl font-bold text-brand-charcoal">₹{(totalCost / 100000).toFixed(2)}L</p>
              <p className="text-text-secondary text-sm mt-2">Base estimate: ₹{((totalCost * 0.95) / 100000).toFixed(2)}L - ₹{((totalCost * 1.05) / 100000).toFixed(2)}L</p>
            </div>
            <div className="text-right">
              <div className="bg-emerald-100 text-emerald-700 px-4 py-2 rounded-lg">
                <p className="text-xs font-medium">Confidence Band</p>
                <p className="text-2xl font-bold">±4.5%</p>
              </div>
            </div>
          </div>
        </Card>

        <Card>
          <p className="text-text-secondary text-sm mb-2">Cost per Sq.Ft</p>
          <p className="text-3xl font-bold text-brand-charcoal">₹1,245</p>
          <p className="text-emerald-600 text-sm mt-2">Within market range</p>
        </Card>
      </div>

      <Card title="Cost Breakdown" action={
        <select className="px-3 py-1 border border-border-warm rounded-lg text-sm">
          <option>All Items</option>
          <option>Structural</option>
          <option>Finishing</option>
        </select>
      }>
        <Table columns={columns} data={costBreakdown} />
        <div className="mt-6 pt-6 border-t border-border-warm flex justify-between items-center">
          <p className="text-lg font-semibold text-brand-charcoal">Total Estimated Cost</p>
          <p className="text-2xl font-bold text-brand-orange">₹{(totalCost / 100000).toFixed(2)}L</p>
        </div>
      </Card>
    </div>
  );
}
