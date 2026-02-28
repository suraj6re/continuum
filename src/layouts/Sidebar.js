export default function Sidebar({ activeItem, onNavigate }) {
  const menuItems = [
    { id: 'overview', label: 'Overview'},
    { id: 'upload', label: 'Upload Drawing'},
    { id: 'qto', label: 'QTO'},
    { id: 'cost', label: 'Cost Intelligence'},
    { id: 'schedule', label: 'Schedule'},
    { id: 'validation', label: 'Validation & Confidence'},
    { id: 'optimization', label: 'Optimization'},
    { id: 'suppliers', label: 'Suppliers'},
    { id: 'procurement', label: 'Procurement'},
    { id: 'reports', label: 'Reports'},
    { id: 'settings', label: 'Settings'},
  ];

  return (
    <div className="w-64 bg-brand-charcoal h-screen fixed left-0 top-0 flex flex-col">
      <div className="p-6 border-b border-gray-700">
        <h1 className="text-2xl font-bold text-white">StructIQ</h1>
        <p className="text-xs text-gray-400 mt-1">Construction Intelligence</p>
      </div>
      
      <nav className="flex-1 overflow-y-auto py-4">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onNavigate(item.id)}
            className={`w-full px-6 py-3 flex items-center space-x-3 transition-colors text-left
              ${activeItem === item.id 
                ? 'bg-brand-orange text-white border-l-4 border-brand-orange' 
                : 'text-gray-300 hover:bg-gray-800'}`}
          >
            <span className="text-lg">{item.icon}</span>
            <span className="text-sm font-medium">{item.label}</span>
          </button>
        ))}
      </nav>
    </div>
  );
}
