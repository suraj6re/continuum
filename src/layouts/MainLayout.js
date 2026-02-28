import Sidebar from './Sidebar';
import Topbar from './Topbar';

export default function MainLayout({ children, activeItem, onNavigate }) {
  return (
    <div className="min-h-screen bg-bg-page">
      <Sidebar activeItem={activeItem} onNavigate={onNavigate} />
      <Topbar />
      <main className="ml-64 pt-16">
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
