import { useEffect, useState } from 'react';

export default function CostSummaryCard({ title, value, loading }) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    if (!loading && value) {
      let start = 0;
      const end = value;
      const duration = 1000;
      const increment = end / (duration / 16);
      
      const timer = setInterval(() => {
        start += increment;
        if (start >= end) {
          setDisplayValue(end);
          clearInterval(timer);
        } else {
          setDisplayValue(Math.floor(start));
        }
      }, 16);

      return () => clearInterval(timer);
    }
  }, [value, loading]);

  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
          <div className="h-8 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <p className="text-sm text-gray-600 mb-1">{title}</p>
      <p className="text-3xl font-bold text-gray-900">
        ₹{displayValue.toLocaleString('en-IN')}
      </p>
    </div>
  );
}
