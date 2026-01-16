import React, { useState } from 'react';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Icons } from './icons';
import { Button } from './ui/Button';
import { cn } from '../lib/utils';
import { useAuth } from '../context/AuthContext.v2';

// Logout Button Component
const LogoutButton: React.FC<{ isSidebarOpen: boolean }> = ({ isSidebarOpen }) => {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      setIsLoggingOut(false);
    }
  };

  return (
    <button
      onClick={handleLogout}
      disabled={isLoggingOut}
      className={cn(
        'flex items-center p-3 rounded-md transition-colors duration-200 w-full',
        'text-text-secondary hover:bg-surface-hover hover:text-text',
        isSidebarOpen ? 'justify-start' : 'justify-center'
      )}
    >
      {isLoggingOut ? (
        <Icons.Spinner className={cn('h-5 w-5 animate-spin', isSidebarOpen ? 'mr-3' : 'mr-0')} />
      ) : (
        <Icons.LogOut className={cn('h-5 w-5', isSidebarOpen ? 'mr-3' : 'mr-0')} />
      )}
      {isSidebarOpen && (
        <span className="transition-opacity duration-300 opacity-100">
          Logout
        </span>
      )}
    </button>
  );
};

const SidebarLayout: React.FC = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true); // Default to open
  const location = useLocation();
  const { user } = useAuth();

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  // Check if user is super admin
  const isSuperAdmin = user?.role === 'super_admin' || user?.role === 'admin';

  const allSidebarItems = [
    { path: '/', label: 'Dashboard', icon: Icons.LayoutDashboard, requiresSuperAdmin: false },
    { path: '/knowledge-base', label: 'Knowledge Base', icon: Icons.BookOpen, requiresSuperAdmin: false },
    { path: '/chat', label: 'Internal Chat', icon: Icons.Search, requiresSuperAdmin: false },
    { path: '/database-chat', label: 'Database Chat', icon: Icons.Database, requiresSuperAdmin: false },
    { path: '/ai-agent', label: 'AI Agent', icon: Icons.Sparkles, requiresSuperAdmin: false, badge: 'BETA' },
    { path: '/settings', label: 'Settings', icon: Icons.Settings, requiresSuperAdmin: false },
    { path: '/admin/public-chat', label: 'Public Chat Config', icon: Icons.MessageSquare, requiresSuperAdmin: false },
    { path: '/admin/public-agent', label: 'Public Agent Config', icon: Icons.Brain, requiresSuperAdmin: false, badge: 'BETA' },
    { path: '/admin/dashboard', label: 'Admin Dashboard', icon: Icons.Shield, requiresSuperAdmin: true },
  ];

  // Filter sidebar items based on user role
  const sidebarItems = allSidebarItems.filter(item => 
    !item.requiresSuperAdmin || isSuperAdmin
  );

  // Determine the current page title for the header
  const currentPageTitle = sidebarItems.find(item => item.path === location.pathname)?.label || 'Welcome';

  return (
    <div className="flex min-h-screen bg-background text-text">
      {/* Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-40 transition-all duration-300 ease-in-out flex flex-col',
          isSidebarOpen ? 'w-64' : 'w-20',
          'bg-surface border-r border-border'
        )}
      >
        <div className="flex items-center justify-between p-3 h-16 border-b border-border">
          <span className={cn('font-bold text-lg text-primary transition-opacity duration-300', isSidebarOpen ? 'opacity-100' : 'opacity-0')}>
            AppLogo
          </span>
          {isSidebarOpen && (
            <Button variant="ghost" size="icon" onClick={toggleSidebar} className="hover:bg-transparent">
              <Icons.ChevronLeft className="h-5 w-5 text-text-secondary" />
            </Button>
          )}
        </div>
        <nav className="p-3 space-y-1 flex-grow">
          {sidebarItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  'flex items-center p-3 rounded-md transition-colors duration-200',
                  isActive
                    ? 'bg-primary text-white shadow-sm'
                    : 'text-text-secondary hover:bg-surface-hover hover:text-text',
                  isSidebarOpen ? 'justify-start' : 'justify-center' // Center items when collapsed
                )
              }
            >
              {/* Icon is always visible */}
              <item.icon className={cn('h-5 w-5', isSidebarOpen ? 'mr-3' : 'mr-0')} />
              {/* Label is only shown when sidebar is open */}
              {isSidebarOpen && (
                <span className="transition-opacity duration-300 opacity-100 flex items-center gap-2">
                  {item.label}
                  {item.badge && (
                    <span className="text-[10px] bg-primary/20 px-1.5 py-0.5 rounded-full font-semibold">
                      {item.badge}
                    </span>
                  )}
                </span>
              )}
            </NavLink>
          ))}
        </nav>
        
        {/* Logout Button at Bottom */}
        <div className="p-3 border-t border-border">
          <LogoutButton isSidebarOpen={isSidebarOpen} />
        </div>
      </aside>

      {/* Main Content Area */}
      <div
        className={cn(
          'flex-1 transition-all duration-300 ease-in-out',
          isSidebarOpen ? 'ml-64' : 'ml-20'
        )}
      >
        <header className="h-16 flex items-center justify-between px-6 border-b border-border bg-surface">
          <div className="flex items-center">
            {!isSidebarOpen && (
              <Button variant="ghost" size="icon" onClick={toggleSidebar} className="mr-4 hover:bg-transparent">
                <Icons.ChevronRight className="h-5 w-5 text-text-secondary" />
              </Button>
            )}
            <h1 className="text-lg font-semibold text-primary">{currentPageTitle}</h1>
          </div>
          <div className="flex items-center space-x-3">
            <Button variant="ghost" size="icon">
              <Icons.Search className="h-5 w-5 text-text-secondary" />
            </Button>
            <Button variant="ghost" size="icon">
              <Icons.Bell className="h-5 w-5 text-text-secondary" />
            </Button>
            <Button variant="ghost" size="icon" onClick={() => { /* Handle profile click */ }}>
              <Icons.User className="h-5 w-5 text-text-secondary" />
            </Button>
          </div>
        </header>
        <main className="p-6">
          <Outlet /> {/* Render the page content here */}
        </main>      </div>
    </div>
  );
};

export default SidebarLayout;
