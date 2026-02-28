import Card from '../components/Card';
import Table from '../components/Table';
import Badge from '../components/Badge';

export default function Suppliers() {
  const suppliers = [
    { name: 'ABC Concrete Ltd', material: 'Concrete', rating: 4.8, price: '₹8,500/m³', delivery: '2-3 days', verified: true },
    { name: 'Steel Masters Inc', material: 'Steel', rating: 4.6, price: '₹85/kg', delivery: '1-2 days', verified: true },
    { name: 'BuildMart Supplies', material: 'Bricks', rating: 4.5, price: '₹450/m²', delivery: '3-4 days', verified: false },
    { name: 'Premium Tiles Co', material: 'Tiles', rating: 4.7, price: '₹650/m²', delivery: '5-7 days', verified: true },
  ];

  const columns = [
    { header: 'Supplier', accessor: 'name' },
    { header: 'Material', accessor: 'material' },
    { 
      header: 'Rating', 
      accessor: 'rating',
      render: (row) => (
        <div className="flex items-center">
          <span className="text-brand-amber mr-1">★</span>
          <span>{row.rating}</span>
        </div>
      )
    },
    { header: 'Price', accessor: 'price' },
    { header: 'Delivery', accessor: 'delivery' },
    { 
      header: 'Status', 
      accessor: 'verified',
      render: (row) => (
        <Badge variant={row.verified ? 'success' : 'warning'}>
          {row.verified ? 'Verified' : 'Pending'}
        </Badge>
      )
    },
  ];

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-brand-charcoal mb-2">Suppliers</h1>
        <p className="text-text-secondary">Verified supplier network and comparison</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card>
          <p className="text-text-secondary text-sm mb-1">Total Suppliers</p>
          <p className="text-4xl font-bold text-brand-charcoal">24</p>
        </Card>
        <Card>
          <p className="text-text-secondary text-sm mb-1">Verified</p>
          <p className="text-4xl font-bold text-emerald-600">18</p>
        </Card>
        <Card>
          <p className="text-text-secondary text-sm mb-1">Avg Rating</p>
          <p className="text-4xl font-bold text-brand-amber">4.6★</p>
        </Card>
        <Card>
          <p className="text-text-secondary text-sm mb-1">Active Orders</p>
          <p className="text-4xl font-bold text-brand-orange">6</p>
        </Card>
      </div>

      <Card title="Supplier Directory" action={
        <select className="px-3 py-1 border border-border-warm rounded-lg text-sm">
          <option>All Materials</option>
          <option>Concrete</option>
          <option>Steel</option>
          <option>Bricks</option>
        </select>
      }>
        <Table columns={columns} data={suppliers} />
      </Card>
    </div>
  );
}
