import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import { getMe } from '@/lib/api';

interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadUser = useCallback(async () => {
    const token = localStorage.getItem('libris_token');
    if (!token) {
      setIsLoading(false);
      return;
    }

    try {
      const cached = localStorage.getItem('libris_user');
      if (cached) {
        setUser(JSON.parse(cached));
      }
      const data = await getMe();
      setUser(data.user);
      localStorage.setItem('libris_user', JSON.stringify(data.user));
    } catch {
      localStorage.removeItem('libris_token');
      localStorage.removeItem('libris_user');
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const login = useCallback((token: string, userData: User) => {
    localStorage.setItem('libris_token', token);
    localStorage.setItem('libris_user', JSON.stringify(userData));
    setUser(userData);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('libris_token');
    localStorage.removeItem('libris_user');
    setUser(null);
  }, []);

  const refreshUser = useCallback(async () => {
    await loadUser();
  }, [loadUser]);

  return (
    <AuthContext.Provider value={{
      user,
      isLoading,
      isAuthenticated: !!user,
      login,
      logout,
      refreshUser,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}