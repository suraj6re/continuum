export default function DeliveryTracker({ items }) {
  if (!items || items.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No delivery items to track
      </div>
    );
  }

  const getProgress = (status) => {
    switch (status) {
      case 'Not Ordered': return 0;
      case 'Ordered': return 33;
      case 'In Transit': return 66;
      case 'Delivered': return 100;
      default: return 0;
    }
  };

  const getProgressColor = (progress) => {
    if (progress === 100) return 'bg-green-600';
    if (progress >= 50) return 'bg-yellow-600';
    return 'bg-blue-600';
  };

  const overallProgress = items.length > 0
    ? Math.round(items.reduce((sum, item) => sum + getProgress(item.order_status), 0) / items.length)
    : 0;

  return (
    <div className="space-y-6">
      <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-blue-900">Overall Delivery Progress</span>
          <span className="text-2xl font-bold text-blue-900">{overallProgress}%</span>
        </div>
        <div className="w-full bg-blue-200 rounded-full h-4">
          <div
            className="bg-blue-600 h-4 rounded-full transition-all duration-500"
            style={{ width: `${overallProgress}%` }}
          ></div>
        </div>
      </div>

      <div className="space-y-3">
        {items.slice(0, 5).map((item) => {
          const progress = getProgress(item.order_status);
          const progressColor = getProgressColor(progress);

          return (
            <div key={item.id} className="p-3 bg-gray-50 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-900">{item.element_name}</span>
                <span className="text-xs text-gray-600">{item.order_status}</span>
              </div>

              <div className="relative">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`${progressColor} h-2 rounded-full transition-all duration-500`}
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>

                <div className="flex justify-between mt-1 text-xs text-gray-500">
                  <span className={progress >= 0 ? 'font-medium text-gray-700' : ''}>Ordered</span>
                  <span className={progress >= 33 ? 'font-medium text-gray-700' : ''}>Processing</span>
                  <span className={progress >= 66 ? 'font-medium text-gray-700' : ''}>In Transit</span>
                  <span className={progress === 100 ? 'font-medium text-green-700' : ''}>Delivered</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {items.length > 5 && (
        <p className="text-xs text-gray-500 text-center">
          Showing 5 of {items.length} items
        </p>
      )}
    </div>
  );
}
