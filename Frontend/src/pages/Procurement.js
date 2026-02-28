import Card from '../components/Card';
import Button from '../components/Button';
import Badge from '../components/Badge';

export default function Procurement() {
  const rfqItems = [
    { material: 'Concrete M30', quantity: '245.5 m³', supplier: 'ABC Concrete Ltd', status: 'Sent' },
    { material: 'Steel TMT Bars', quantity: '12450 kg', supplier: 'Steel Masters Inc', status: 'Pending' },
    { material: 'Brick Masonry', quantity: '1850 m²', supplier: 'BuildMart Supplies', status: 'Draft' },
  ];

  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-brand-charcoal mb-2">Procurement</h1>
          <p className="text-text-secondary">RFQ generation and supplier communication</p>
        </div>
        <Button>Generate New RFQ</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <p className="text-text-secondary text-sm mb-1">Active RFQs</p>
          <p className="text-4xl font-bold text-brand-charcoal">8</p>
        </Card>
        <Card>
          <p className="text-text-secondary text-sm mb-1">Pending Quotes</p>
          <p className="text-4xl font-bold text-brand-orange">5</p>
        </Card>
        <Card>
          <p className="text-text-secondary text-sm mb-1">Total Value</p>
          <p className="text-4xl font-bold text-emerald-600">₹54.9L</p>
        </Card>
      </div>

      <Card title="Request for Quotations" className="mb-6">
        <div className="space-y-4">
          {rfqItems.map((item, idx) => (
            <div key={idx} className="flex items-center justify-between p-4 bg-bg-section rounded-lg">
              <div className="flex-1">
                <h4 className="font-semibold text-brand-charcoal">{item.material}</h4>
                <p className="text-sm text-text-secondary mt-1">
                  Quantity: {item.quantity} • Supplier: {item.supplier}
                </p>
              </div>
              <div className="flex items-center space-x-3">
                <Badge variant={
                  item.status === 'Sent' ? 'success' : 
                  item.status === 'Pending' ? 'warning' : 'info'
                }>
                  {item.status}
                </Badge>
                <Button size="sm" variant="outline">View</Button>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card title="Email Preview">
        <div className="bg-bg-section p-6 rounded-lg border border-border-warm">
          <div className="mb-4">
            <p className="text-sm text-text-secondary">To: supplier@abcconcrete.com</p>
            <p className="text-sm text-text-secondary">Subject: RFQ - Concrete M30 Supply</p>
          </div>
          <div className="prose text-sm text-text-primary">
            <p className="mb-3">Dear Supplier,</p>
            <p className="mb-3">
              We request a quotation for the following materials for our construction project:
            </p>
            <ul className="mb-3 ml-6 list-disc">
              <li>Material: Concrete M30</li>
              <li>Quantity: 245.5 m³</li>
              <li>Delivery Location: Project Site, Sector 45</li>
              <li>Required By: 15th February 2024</li>
            </ul>
            <p>Please provide your best quote including delivery charges.</p>
          </div>
          <div className="mt-6 flex space-x-3">
            <Button size="sm">Send Email</Button>
            <Button size="sm" variant="outline">Edit</Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
