import { useState } from 'react';
import MainLayout from './layouts/MainLayout';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Overview from './pages/Overview';
import Upload from './pages/Upload';
import QTO from './pages/QTO';
import Cost from './pages/Cost';
import Schedule from './pages/Schedule';
import Validation from './pages/Validation';
import Optimization from './pages/Optimization';
import Suppliers from './pages/Suppliers';
import Procurement from './pages/Procurement';
import Reports from './pages/Reports';
import Settings from './pages/Settings';

function App() {
  const [currentView, setCurrentView] = useState('landing');
  const [activeItem, setActiveItem] = useState('overview');

  const handleNavigation = (view) => {
    setActiveItem(view);
  };

  const handleGetStarted = () => {
    setCurrentView('login');
  };

  const handleLogin = () => {
    setCurrentView('app');
    setActiveItem('upload');
  };

  if (currentView === 'landing') {
    return <Landing onGetStarted={handleGetStarted} />;
  }

  if (currentView === 'login') {
    return <Login onLogin={handleLogin} />;
  }

  const renderPage = () => {
    switch (activeItem) {
      case 'overview': return <Overview />;
      case 'upload': return <Upload />;
      case 'qto': return <QTO />;
      case 'cost': return <Cost />;
      case 'schedule': return <Schedule />;
      case 'validation': return <Validation />;
      case 'optimization': return <Optimization />;
      case 'suppliers': return <Suppliers />;
      case 'procurement': return <Procurement />;
      case 'reports': return <Reports />;
      case 'settings': return <Settings />;
      default: return <Overview />;
    }
  };

  return (
    <MainLayout activeItem={activeItem} onNavigate={handleNavigation}>
      {renderPage()}
    </MainLayout>
  );
}

export default App;
