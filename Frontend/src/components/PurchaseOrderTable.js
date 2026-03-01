import { ORDER_STATUS, PAYMENT_STATUS } from '../services/procurementEngine';

export default function PurchaseOrderTable({ items, onUpdateOrder, onUpdatePayment, isFinalized }) {
  if (!items || items.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No procurement items available
      </div>
    );
  }

  const getStatusBadge = (status) => {
    const config = {
      [ORDER_STATUS.NOT_ORDERED]: 'bg-gray-100 text-gray-800',
      [ORDER_STATUS.ORDERED]: 'bg-blue-100 text-blue-800',
      [ORDER_STATUS.IN_TRANSIT]: 'bg-yellow-100 text-yellow-800',
      [ORDER_STATUS.DELIVERED]: 'bg-green-100 text-green-800'
    };
    return config[status] || config[ORDER_STATUS.NOT_ORDERED];
  };

  const getPaymentBadge = (status) => {
    const config = {
      [PAYMENT_STATUS.PENDING]: 'bg-red-100 text-red-800',
      [PAYMENT_STATUS.PARTIAL]: 'bg-yellow-100 text-yellow-800',
      [PAYMENT_STATUS.COMPLETED]: 'bg-green-100 text-green-800'
    };
    return config[status] || config[PAYMENT_STATUS.PENDING];
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Element</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quantity</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Unit Rate</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Cost</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Required By</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Delivery ETA</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order Status</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Payment</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {items.map((item) => (
            <tr key={item.id} className={item.is_delayed ? 'bg-red-50' : 'hover:bg-gray-50'}>
              <td className="px-6 py-4 text-sm font-medium text-gray-900">
                {item.element_name}
                {item.is_delayed && (
                  <span className="ml-2 text-xs text-red-600">⚠ Delayed</span>
                )}
              </td>
              <td className="px-6 py-4 text-sm text-gray-500">
                {item.quantity} {item.unit}
              </td>
              <td className="px-6 py-4 text-sm text-gray-500">
                ₹{item.supplier_rate.toLocaleString('en-IN')}
              </td>
              <td className="px-6 py-4 text-sm font-medium text-gray-900">
                ₹{item.total_cost.toLocaleString('en-IN')}
              </td>
              <td className="px-6 py-4 text-sm text-gray-500">
                Day {item.required_by_day}
              </td>
              <td className="px-6 py-4 text-sm text-gray-500">
                Day {item.delivery_eta}
              </td>
              <td className="px-6 py-4 text-sm">
                {isFinalized ? (
                  <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusBadge(item.order_status)}`}>
                    {item.order_status}
                  </span>
                ) : (
                  <select
                    value={item.order_status}
                    onChange={(e) => onUpdateOrder(item.id, e.target.value)}
                    className="px-2 py-1 text-xs border border-gray-300 rounded"
                  >
                    {Object.values(ORDER_STATUS).map(status => (
                      <option key={status} value={status}>{status}</option>
                    ))}
                  </select>
                )}
              </td>
              <td className="px-6 py-4 text-sm">
                {isFinalized ? (
                  <span className={`px-2 py-1 text-xs font-medium rounded ${getPaymentBadge(item.payment_status)}`}>
                    {item.payment_status}
                  </span>
                ) : (
                  <select
                    value={item.payment_status}
                    onChange={(e) => onUpdatePayment(item.id, e.target.value)}
                    className="px-2 py-1 text-xs border border-gray-300 rounded"
                  >
                    {Object.values(PAYMENT_STATUS).map(status => (
                      <option key={status} value={status}>{status}</option>
                    ))}
                  </select>
                )}
              </td>
              <td className="px-6 py-4 text-sm">
                <button
                  disabled={isFinalized}
                  className="text-blue-600 hover:text-blue-800 text-xs disabled:text-gray-400"
                >
                  Generate PO
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
