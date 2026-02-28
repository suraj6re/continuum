import Badge from './Badge';

export default function Layer3Output({ data }) {
  if (!data) {
    return (
      <div className="mt-6 p-8 bg-bg-section rounded-lg text-center">
        <p className="text-text-secondary">No Layer 3 data available</p>
      </div>
    );
  }

  return (
    <div className="mt-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-brand-charcoal">Layer 3 — Quantity Takeoff Output</h3>
        <Badge variant="success">QTO COMPLETE</Badge>
      </div>

      <div className="bg-white rounded-lg border border-border-warm p-4">
        <pre className="text-xs overflow-auto max-h-[600px] bg-gray-50 p-4 rounded">
          {JSON.stringify(data, null, 2)}
        </pre>
      </div>
    </div>
  );
}
