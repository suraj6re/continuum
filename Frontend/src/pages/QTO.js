import Card from '../components/Card';
import Table from '../components/Table';
import Badge from '../components/Badge';
import Button from '../components/Button';

export default function QTO() {
  const qtoData = [
    { element: 'Concrete Slab', quantity: 245.5, unit: 'm³', confidence: 98, category: 'Structural' },
    { element: 'Steel Reinforcement', quantity: 12450, unit: 'kg', confidence: 96, category: 'Structural' },
    { element: 'Brick Masonry', quantity: 1850, unit: 'm²', confidence: 94, category: 'Walls' },
    { element: 'Plaster Work', quantity: 3200, unit: 'm²', confidence: 92, category: 'Finishing' },
    { element: 'Floor Tiles', quantity: 1450, unit: 'm²', confidence: 95, category: 'Finishing' },
  ];

  const columns = [
    { header: 'Element', accessor: 'element' },
    { header: 'Quantity', accessor: 'quantity', render: (row) => `${row.quantity} ${row.unit}` },
    { header: 'Category', accessor: 'category' },
    { 
      header: 'Confidence', 
      accessor: 'confidence',
      render: (row) => (
        <Badge variant={row.confidence >= 95 ? 'success' : row.confidence >= 90 ? 'warning' : 'error'}>
          {row.confidence}%
        </Badge>
      )
    },
  ];

  const summary = [
    { label: 'Total Elements', value: '24' },
    { label: 'Avg Confidence', value: '95%' },
    { label: 'High Confidence', value: '18' },
    { label: 'Needs Review', value: '2' },
  ];

  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-brand-charcoal mb-2">Quantity Take-Off</h1>
          <p className="text-text-secondary">AI-extracted quantities from construction drawings</p>
        </div>
        <Button>Export QTO</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        {summary.map((item, idx) => (
          <Card key={idx}>
            <p className="text-text-secondary text-sm mb-1">{item.label}</p>
            <p className="text-3xl font-bold text-brand-charcoal">{item.value}</p>
          </Card>
        ))}
      </div>

      <Card title="Extracted Quantities" action={
        <div className="flex space-x-2">
          <select className="px-3 py-1 border border-border-warm rounded-lg text-sm">
            <option>All Categories</option>
            <option>Structural</option>
            <option>Walls</option>
            <option>Finishing</option>
          </select>
        </div>
      }>
        <Table columns={columns} data={qtoData} />
      </Card>
    </div>
  );
}
