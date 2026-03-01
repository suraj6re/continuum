import { useState } from 'react';

export default function ValidationTable({ elements, loading, onApprove, onOverride }) {
  const [editingId, setEditingId] = useState(null);
  const [overrideValue, setOverrideValue] = useState('');
  const [notes, setNotes] = useState('');

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        {[1, 2, 3].map(i => (
          <div key={i} className="h-16 bg-gray-200 rounded"></div>
        ))}
      </div>
    );
  }

  if (!elements || elements.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No validation data available
      </div>
    );
  }

  const getConfidenceBadge = (confidence) => {
    if (confidence >= 0.95) {
      return <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
        {(confidence * 100).toFixed(0)}%
      </span>;
    } else if (confidence >= 0.90) {
      return <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded">
        {(confidence * 100).toFixed(0)}%
      </span>;
    } else {
      return <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded">
        {(confidence * 100).toFixed(0)}%
      </span>;
    }
  };

  const getStatusBadge = (status) => {
    if (status === 'Validated') {
      return <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">Validated</span>;
    } else if (status === 'Review Recommended') {
      return <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded">Review</span>;
    } else {
      return <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded">Attention</span>;
    }
  };

  const getApprovalBadge = (status) => {
    if (status === 'approved') {
      return <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">Approved</span>;
    } else if (status === 'user_corrected') {
      return <span className="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-800 rounded">Corrected</span>;
    } else {
      return <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded">Pending</span>;
    }
  };

  const handleStartEdit = (element) => {
    setEditingId(element.id || element.element_id);
    setOverrideValue(element.override_quantity || element.quantity);
    setNotes(element.notes || '');
  };

  const handleSaveOverride = (elementId) => {
    onOverride(elementId, parseFloat(overrideValue), notes);
    setEditingId(null);
    setOverrideValue('');
    setNotes('');
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setOverrideValue('');
    setNotes('');
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Element</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quantity</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Confidence</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Flags</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Approval</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {elements.map((element) => {
            const elementId = element.id || element.element_id;
            const isEditing = editingId === elementId;

            return (
              <tr key={elementId} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-gray-900">
                  {element.element_name || element.name}
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">{element.category}</td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  {isEditing ? (
                    <input
                      type="number"
                      value={overrideValue}
                      onChange={(e) => setOverrideValue(e.target.value)}
                      className="w-24 px-2 py-1 border border-gray-300 rounded text-sm"
                    />
                  ) : (
                    <>
                      {element.override_quantity || element.quantity} {element.unit || ''}
                      {element.user_corrected && (
                        <span className="ml-2 text-xs text-purple-600">(Corrected)</span>
                      )}
                    </>
                  )}
                </td>
                <td className="px-6 py-4 text-sm">
                  {getConfidenceBadge(element.confidence)}
                </td>
                <td className="px-6 py-4 text-sm">
                  {getStatusBadge(element.validation_status)}
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  {element.flags.length > 0 ? (
                    <div className="space-y-1">
                      {element.flags.map((flag, idx) => (
                        <div key={idx} className="text-xs text-red-600">{flag}</div>
                      ))}
                    </div>
                  ) : (
                    <span className="text-green-600">No issues</span>
                  )}
                </td>
                <td className="px-6 py-4 text-sm">
                  {getApprovalBadge(element.approval_status)}
                </td>
                <td className="px-6 py-4 text-sm">
                  {isEditing ? (
                    <div className="space-y-2">
                      <input
                        type="text"
                        placeholder="Notes..."
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-xs"
                      />
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleSaveOverride(elementId)}
                          className="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
                        >
                          Save
                        </button>
                        <button
                          onClick={handleCancelEdit}
                          className="px-2 py-1 text-xs bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex space-x-2">
                      {element.approval_status === 'pending' && (
                        <button
                          onClick={() => onApprove(elementId, 'approved')}
                          className="px-2 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700"
                        >
                          Approve
                        </button>
                      )}
                      <button
                        onClick={() => handleStartEdit(element)}
                        className="px-2 py-1 text-xs bg-purple-600 text-white rounded hover:bg-purple-700"
                      >
                        Override
                      </button>
                    </div>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
