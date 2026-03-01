import { useProjectStore } from '../hooks/useProjectStore';

export default function Sidebar({ activeItem, onNavigate, isOpen, onToggle }) {
  const menuItems = [
    { id: 'overview', label: 'Overview' },
    { id: 'upload', label: 'Upload Drawing' },
    { id: 'qto', label: 'QTO' },
    { id: 'cost', label: 'Cost Intelligence' },
    { id: 'schedule', label: 'Schedule' },
    { id: 'validation', label: 'Validation & Confidence' },
    { id: 'optimization', label: 'Optimization' },
    { id: 'suppliers', label: 'Suppliers' },
    { id: 'procurement', label: 'Procurement' },
    { id: 'reports', label: 'Reports' },
    { id: 'settings', label: 'Settings' },
  ];

  return (
    <div className={`w-64 bg-brand-charcoal h-screen fixed left-0 top-0 flex flex-col transition-transform duration-300 z-20 ${isOpen ? 'translate-x-0' : '-translate-x-64'}`}>
      <div className="p-6 border-b border-gray-700 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">StructIQ</h1>
          <p className="text-xs text-gray-400 mt-1">Construction Intelligence</p>
        </div>
        <button onClick={onToggle} className="text-white hover:text-brand-orange transition-colors">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <nav className="flex-1 overflow-y-auto py-4">
        {menuItems.map((item, idx) => (
          <button
            key={item.id}
            onClick={() => onNavigate(item.id)}
            className={`w-full px-6 py-3 flex items-center space-x-3 transition-all text-left
              ${activeItem === item.id 
                ? 'bg-brand-orange text-white border-l-4 border-brand-orange' 
                : 'text-gray-300 hover:bg-gray-800'}
              ${isOpen ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-4'}`}
            style={{ 
              transitionDelay: isOpen ? `${idx * 50}ms` : '0ms',
              transitionDuration: '300ms'
            }}
          >
            <span className="text-lg">{item.icon}</span>
            <span className="text-sm font-medium">{item.label}</span>
          </button>
        ))}
      </nav>
    </div>
  );
}
