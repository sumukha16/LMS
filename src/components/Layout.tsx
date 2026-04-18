import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import {
  LayoutDashboard,
  BookOpen,
  Users,
  Clock,
  Bookmark,
  BarChart3,
  Settings,
  LogOut,
  Search,
  Bell,
  Menu,
  X,
  Library
} from 'lucide-react';

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
  { icon: BookOpen, label: 'Catalog', path: '/catalog' },
  { icon: Users, label: 'Patrons', path: '/patrons' },
  { icon: Clock, label: 'Loans', path: '/loans' },
  { icon: Bookmark, label: 'Reservations', path: '/reservations' },
  { icon: BarChart3, label: 'Reports', path: '/reports' },
  { icon: Settings, label: 'Settings', path: '/settings' },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/catalog?q=${encodeURIComponent(searchQuery.trim())}`);
      setSearchQuery('');
    }
  };

  return (
    <div className="min-h-screen bg-[var(--color-bg-primary)]">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 h-[60px] bg-[var(--color-bg-dark)] border-b border-[var(--color-border-dark)]">
        <div className="flex items-center justify-between h-full px-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-1.5 rounded-md hover:bg-white/10 transition-colors"
            >
              {sidebarOpen ? (
                <X className="w-5 h-5 text-[var(--color-text-inverse)]" />
              ) : (
                <Menu className="w-5 h-5 text-[var(--color-text-inverse)]" />
              )}
            </button>
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-2.5 hover:opacity-80 transition-opacity"
            >
              <Library className="w-6 h-6 text-[var(--color-accent-quaternary)]" />
              <span
                className="text-[1.25rem] font-medium text-[var(--color-text-inverse)] tracking-tight"
                style={{ fontFamily: 'var(--font-display)' }}
              >
                Libris
              </span>
            </button>
          </div>

          <div className="flex-1 max-w-md mx-4 hidden sm:block">
            <form onSubmit={handleSearch} className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--color-text-inverse)]/50" />
              <input
                type="text"
                placeholder="Search books, patrons..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full h-9 pl-9 pr-4 rounded-lg bg-white/10 border border-white/10 text-sm text-[var(--color-text-inverse)] placeholder:text-[var(--color-text-inverse)]/40 focus:outline-none focus:border-[var(--color-accent-quaternary)]/50 focus:bg-white/15 transition-all"
              />
            </form>
          </div>

          <div className="flex items-center gap-3">
            <button className="relative p-2 rounded-lg hover:bg-white/10 transition-colors">
              <Bell className="w-[18px] h-[18px] text-[var(--color-text-inverse)]/70" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-[var(--color-accent-primary)] rounded-full" />
            </button>
            <div className="flex items-center gap-2.5 pl-2 border-l border-white/10">
              <div className="w-7 h-7 rounded-full bg-[var(--color-accent-primary)] flex items-center justify-center text-[var(--color-text-inverse)] text-xs font-semibold">
                {user?.full_name?.split(' ').map(n => n[0]).join('') || 'U'}
              </div>
              <span className="text-sm text-[var(--color-text-inverse)]/80 hidden md:block max-w-[120px] truncate">
                {user?.full_name || user?.username}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Sidebar */}
      <aside
        className={`fixed top-[60px] left-0 bottom-0 w-[220px] bg-[var(--color-bg-dark)] z-40 transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <nav className="flex flex-col h-full py-4">
          <div className="flex-1 px-3 space-y-1">
            {navItems.map(item => {
              const isActive = location.pathname === item.path;
              return (
                <button
                  key={item.path}
                  onClick={() => {
                    navigate(item.path);
                    setSidebarOpen(false);
                  }}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm transition-all duration-200 ${
                    isActive
                      ? 'bg-[rgba(139,41,66,0.15)] text-[var(--color-text-inverse)] border-l-[3px] border-[var(--color-accent-primary)]'
                      : 'text-[var(--color-text-inverse)]/70 hover:bg-[rgba(246,244,240,0.05)] border-l-[3px] border-transparent'
                  }`}
                >
                  <item.icon className="w-5 h-5 shrink-0" />
                  <span className="font-medium">{item.label}</span>
                </button>
              );
            })}
          </div>

          <div className="px-3 pt-4 border-t border-white/10">
            <button
              onClick={logout}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm text-[var(--color-text-inverse)]/70 hover:bg-[rgba(246,244,240,0.05)] transition-all"
            >
              <LogOut className="w-5 h-5 shrink-0" />
              <span className="font-medium">Sign Out</span>
            </button>
          </div>
        </nav>
      </aside>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <main className="pt-[60px] lg:pl-[220px] min-h-screen">
        <div className="p-6 max-w-[1280px] mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
}