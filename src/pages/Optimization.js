import Card from '../components/Card';
import Button from '../components/Button';

export default function Optimization() {
  const suggestions = [
    { 
      item: 'Concrete Grade M30', 
      current: '₹8,500/m³', 
      alternative: 'M25 Grade', 
      newCost: '₹7,800/m³', 
      savings: '₹171,850',
      impact: 'Low structural impact for non-critical areas'
    },
    { 
      item: 'Premium Floor Tiles', 
      current: '₹650/m²', 
      alternative: 'Standard Grade', 
      newCost: '₹480/m²', 
      savings: '₹246,500',
      impact: 'Aesthetic change only'
    },
    { 
      item: 'Steel TMT Bars', 
      current: '₹85/kg', 
      alternative: 'Bulk Purchase', 
      newCost: '₹78/kg', 
      savings: '₹87,150',
      impact: 'No quality impact'
    },
  ];

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-brand-charcoal mb-2">Optimization</h1>
        <p className="text-text-secondary">AI-powered cost optimization suggestions</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <p className="text-text-secondary text-sm mb-1">Potential Savings</p>
          <p className="text-4xl font-bold text-emerald-600">₹5.05L</p>
        </Card>
        <Card>
          <p className="text-text-secondary text-sm mb-1">Suggestions</p>
          <p className="text-4xl font-bold text-brand-charcoal">8</p>
        </Card>
        <Card>
          <p className="text-text-secondary text-sm mb-1">Avg Cost Reduction</p>
          <p className="text-4xl font-bold text-brand-orange">9.2%</p>
        </Card>
      </div>

      <Card title="Optimization Suggestions">
        <div className="space-y-4">
          {suggestions.map((suggestion, idx) => (
            <div key={idx} className="p-6 bg-bg-section rounded-lg border border-border-warm">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h4 className="font-semibold text-brand-charcoal text-lg">{suggestion.item}</h4>
                  <p className="text-sm text-text-secondary mt-1">{suggestion.impact}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-text-secondary">Potential Savings</p>
                  <p className="text-2xl font-bold text-emerald-600">{suggestion.savings}</p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="p-3 bg-bg-card rounded-lg">
                  <p className="text-xs text-text-secondary mb-1">Current</p>
                  <p className="font-semibold text-brand-charcoal">{suggestion.current}</p>
                </div>
                <div className="p-3 bg-emerald-50 rounded-lg border border-emerald-200">
                  <p className="text-xs text-emerald-700 mb-1">Alternative: {suggestion.alternative}</p>
                  <p className="font-semibold text-emerald-700">{suggestion.newCost}</p>
                </div>
              </div>
              
              <div className="flex space-x-3">
                <Button size="sm">Apply Suggestion</Button>
                <Button variant="outline" size="sm">View Details</Button>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
