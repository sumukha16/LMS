import { Routes, Route } from 'react-router'
import { AuthProvider } from './contexts/AuthContext'
import { ToastProvider } from './contexts/ToastContext'
import Home from './pages/Home'
import Login from './pages/Login'
import Catalog from './pages/Catalog'
import Dashboard from './pages/Dashboard'

export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/home" element={<Home />} />
          <Route path="/catalog" element={<Catalog />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </ToastProvider>
    </AuthProvider>
  )
}
