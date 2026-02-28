import { useState } from 'react';
import Sidebar from './Sidebar';
import Topbar from './Topbar';

export default function MainLayout({ children, activeItem, onNavigate }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-bg-page">
      <Sidebar activeItem={activeItem} onNavigate={onNavigate} isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
      <Topbar onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} sidebarOpen={sidebarOpen} />
      <main className={`pt-16 transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-0'}`}>
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
