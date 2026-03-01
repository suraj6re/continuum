import { useState } from 'react';

export default function ProductivityPanel({ onProductivityChange, loading }) {
  const [rates, setRates] = useState({
    'Concrete': 50,
    'Masonry': 100,
    'Finishing': 150
  });

  const handleChange = (key, value) => {
    const newRates = { ...rates, [key]: parseFloat(value) };
    setRates(newRates);
    onProductivityChange(newRates);
  };

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-16 bg-gray-200 rounded"></div>
        <div className="h-16 bg-gray-200 rounded"></div>
        <div className="h-16 bg-gray-200 rounded"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Concrete Productivity (m³/day)
        </label>
        <input
          type="number"
          value={rates['Concrete']}
          onChange={(e) => handleChange('Concrete', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          min="10"
          max="200"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Masonry Productivity (m²/day)
        </label>
        <input
          type="number"
          value={rates['Masonry']}
          onChange={(e) => handleChange('Masonry', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          min="20"
          max="300"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Finishing Productivity (m²/day)
        </label>
        <input
          type="number"
          value={rates['Finishing']}
          onChange={(e) => handleChange('Finishing', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          min="50"
          max="400"
        />
      </div>

      <div className="pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500">
          Adjust productivity rates to recalculate schedule in real-time
        </p>
      </div>
    </div>
  );
}
