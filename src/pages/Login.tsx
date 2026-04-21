import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/contexts/ToastContext';
import { login as loginApi } from '@/lib/api';
import { Library, BookOpen, Users, Clock } from 'lucide-react';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      showToast('Please enter both username and password', 'error');
      return;
    }

    setIsLoading(true);
    try {
      const data = await loginApi(username, password);
      login(data.token, data.user);
      showToast(`Welcome back, ${data.user.full_name || data.user.username}!`);
      navigate('/home');
    } catch (err: unknown) {
      const error = err as Error;
      showToast(error.message || 'Login failed', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const quickLogin = (user: string, pass: string) => {
    setUsername(user);
    setPassword(pass);
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Panel - Decorative */}
      <div className="hidden lg:flex lg:w-[45%] bg-[var(--color-bg-dark)] relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-20 w-64 h-64 rounded-full bg-[var(--color-accent-primary)] blur-3xl" />
          <div className="absolute bottom-20 right-20 w-80 h-80 rounded-full bg-[var(--color-accent-secondary)] blur-3xl" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full bg-[var(--color-accent-quaternary)] blur-3xl" />
        </div>

        <div className="relative z-10 flex flex-col justify-between p-12 w-full">
            <div className="flex items-center gap-3 mb-16">
              <Library className="w-8 h-8 text-[var(--color-accent-quaternary)]" />
              <span
                className="text-4xl font-large-bold text-[var(--color-text-inverse)] top-1.5"
                style={{ fontFamily: 'var(--font-display)' }}
                >
                Libris
              </span>
            </div>

            <div className="top text-5xl font-light text-[var(--color-text-inverse)] leading-[1.1] mb-6" style={{ fontFamily: 'var(--font-display)' }}>
            <h1
              className="text-5xl font-light text-[var(--color-text-inverse)] leading-[1.1] mb-6"
              style={{ fontFamily: 'var(--font-display)' }}
            >
              Where Stories<br />
              Find Their Readers
            </h1>
            <p className="text-[var(--color-text-inverse)] text-lg leading-relaxed max-w-md">
              A modern library management system designed to connect people with the books they love.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-6">
            <div className="flex flex-col items-center gap-2 p-4 rounded-xl bg-white/5 backdrop-blur-sm">
              <BookOpen className="w-6 h-6 text-[var(--color-accent-quaternary)]" />
              <span className="text-[var(--color-text-inverse)] text-lg font-semibold">2,800+</span>
              <span className="text-[var(--color-text-inverse)] text-xs uppercase tracking-wider">Books</span>
            </div>
            <div className="flex flex-col items-center gap-2 p-4 rounded-xl bg-white/5 backdrop-blur-sm">
              <Users className="w-6 h-6 text-[var(--color-accent-quaternary)]" />
              <span className="text-[var(--color-text-inverse)] text-lg font-semibold">180+</span>
              <span className="text-[var(--color-text-inverse)] text-xs uppercase tracking-wider">Patrons</span>
            </div>
            <div className="flex flex-col items-center gap-2 p-4 rounded-xl bg-white/5 backdrop-blur-sm">
              <Clock className="w-6 h-6 text-[var(--color-accent-quaternary)]" />
              <span className="text-[var(--color-text-inverse)] text-lg font-semibold">400+</span>
              <span className="text-[var(--color-text-inverse)] text-xs uppercase tracking-wider">Active Loans</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel - Login Form */}
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-[400px]">
          <div className="lg:hidden flex items-center gap-3 mb-10 justify-center">
            <Library className="w-7 h-7 text-[var(--color-accent-primary)]" />
            <span
              className="text-xl font-medium text-[var(--color-text-primary)]"
              style={{ fontFamily: 'var(--font-display)' }}
            >
              Libris
            </span>
          </div>

          <div className="mb-8">
            <h2
              className="text-3xl font-medium text-[var(--color-text-primary)] mb-2"
              style={{ fontFamily: 'var(--font-display)' }}
            >
              Welcome back
            </h2>
            <p className="text-[var(--color-text-secondary)]">
              Sign in to your librarian account
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1.5">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter your username"
                className="w-full h-11 px-4 rounded-lg border border-[var(--color-border)] bg-white text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--color-accent-primary)]/20 focus:border-[var(--color-accent-primary)] transition-all"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1.5">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="w-full h-11 px-4 rounded-lg border border-[var(--color-border)] bg-white text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--color-accent-primary)]/20 focus:border-[var(--color-accent-primary)] transition-all"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full h-11 bg-[var(--color-accent-primary)] hover:bg-[var(--color-accent-primary)]/90 text-white font-medium rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-[var(--color-border)]">
            <p className="text-xs text-[var(--color-text-muted)] mb-3 text-center uppercase tracking-wider">
              Quick Login
            </p>
            <div className="grid grid-cols-3 gap-2">
              {[
                { label: 'Admin', user: 'admin', pass: 'admin123' },
                { label: 'Sarah', user: 'sarah.chen', pass: 'lib123' },
                { label: 'James', user: 'james.wilson', pass: 'lib123' },
              ].map(item => (
                <button
                  key={item.user}
                  onClick={() => quickLogin(item.user, item.pass)}
                  className="px-3 py-2 text-xs font-medium rounded-lg border border-[var(--color-border)] text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-secondary)] hover:text-[var(--color-text-primary)] transition-all"
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
