export default function Topbar({ user = { name: 'Vikrant Thakur', role: 'Civil Engineer' }, onToggleSidebar, sidebarOpen }) {
  return (
    <div className={`h-16 bg-bg-card border-b border-border-warm fixed top-0 right-0 z-10 flex items-center justify-between px-8 transition-all duration-300 ${sidebarOpen ? 'left-64' : 'left-0'}`}>
      <div className="flex items-center space-x-4">
        {!sidebarOpen && (
          <button onClick={onToggleSidebar} className="text-text-primary hover:text-brand-orange transition-colors">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        )}
        <input
          type="text"
          placeholder="Search projects, drawings..."
          className="w-96 px-4 py-2 rounded-lg border border-border-warm focus:outline-none focus:ring-2 focus:ring-brand-orange"
        />
      </div>
      
      <div className="flex items-center space-x-6">
        <button className="relative text-text-secondary hover:text-text-primary">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          <span className="absolute top-0 right-0 w-2 h-2 bg-red-600 rounded-full"></span>
        </button>
        
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-full bg-brand-orange flex items-center justify-center text-white font-semibold">
            {user.name.split(' ').map(n => n[0]).join('')}
          </div>
          <div>
            <p className="text-sm font-medium text-text-primary">{user.name}</p>
            <p className="text-xs text-text-secondary">{user.role}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
