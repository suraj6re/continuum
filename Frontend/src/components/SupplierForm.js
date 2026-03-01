import { useState } from 'react';

export default function SupplierForm({ onAdd, onCancel }) {
  const [formData, setFormData] = useState({
    name: '',
    laborMultiplier: 1.0,
    deliveryTimeDays: 10,
    reliabilityScore: 75,
    paymentTerms: '30 days',
    materialRates: {}
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onAdd(formData);
    setFormData({
      name: '',
      laborMultiplier: 1.0,
      deliveryTimeDays: 10,
      reliabilityScore: 75,
      paymentTerms: '30 days',
      materialRates: {}
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Supplier Name</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          required
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Labor Multiplier
          </label>
          <input
            type="number"
            step="0.1"
            value={formData.laborMultiplier}
            onChange={(e) => setFormData({ ...formData, laborMultiplier: parseFloat(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Delivery Time (days)
          </label>
          <input
            type="number"
            value={formData.deliveryTimeDays}
            onChange={(e) => setFormData({ ...formData, deliveryTimeDays: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Reliability Score (0-100)
          </label>
          <input
            type="number"
            min="0"
            max="100"
            value={formData.reliabilityScore}
            onChange={(e) => setFormData({ ...formData, reliabilityScore: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Payment Terms
          </label>
          <input
            type="text"
            value={formData.paymentTerms}
            onChange={(e) => setFormData({ ...formData, paymentTerms: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <div className="flex space-x-3 pt-4">
        <button
          type="submit"
          className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
        >
          Add Supplier
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-medium"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
