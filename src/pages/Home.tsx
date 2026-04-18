import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import {
  BookOpen,
  BarChart3,
  Users,
  Gift,
  ArrowRight,
  Library,
  Clock,
} from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function Home() {
  const navigate = useNavigate()
  const { user } = useAuth()

  const features = [
    {
      icon: BookOpen,
      title: 'Browse Catalog',
      description: 'Explore thousands of books in our library collection',
      action: () => navigate('/catalog'),
    },
    {
      icon: BarChart3,
      title: 'Dashboard',
      description: 'View library statistics and recent activity',
      action: () => navigate('/dashboard'),
    },
    {
      icon: Users,
      title: 'Patron Management',
      description: 'Manage patrons and track their borrowing history',
      action: () => navigate('/dashboard'),
    },
    {
      icon: Gift,
      title: 'New Arrivals',
      description: 'Check out recently added books to the collection',
      action: () => navigate('/catalog'),
    },
  ]

  return (
    <div className="min-h-screen flex">
      {/* Left Panel - Decorative (Dark) */}
      <div className="hidden lg:flex lg:w-[45%] relative overflow-hidden" style={{ backgroundColor: 'var(--color-bg-dark)' }}>
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-20 left-20 w-64 h-64 rounded-full" style={{ backgroundColor: 'var(--color-accent-primary)' }} />
          <div className="absolute bottom-20 right-20 w-80 h-80 rounded-full" style={{ backgroundColor: 'var(--color-accent-secondary)' }} />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full" style={{ backgroundColor: 'var(--color-accent-quaternary)' }} />
        </div>

        <div className="relative z-10 flex flex-col justify-between p-12 w-full">
          <div>
            <div className="flex items-center gap-2.5 mb-12">
              <Library className="w-8 h-8" style={{ color: 'var(--color-accent-quaternary)' }} />
              <span className="text-2xl font-semibold" style={{ color: 'var(--color-text-inverse)', fontFamily: 'var(--font-display)' }}>
                Libris
              </span>
            </div>
            <h1 className="text-5xl font-bold mb-6 leading-tight" style={{ color: 'var(--color-text-inverse)', fontFamily: 'var(--font-display)' }}>
              Where Stories Find Their Readers
            </h1>
            <p className="text-lg mb-12" style={{ color: 'var(--color-text-inverse)' }}>
              A complete library management system designed to connect patrons with the books they love.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-6">
            {[
              { icon: BookOpen, label: 'Books', value: '2,800+' },
              { icon: Users, label: 'Patrons', value: '180+' },
              { icon: Clock, label: 'Active Loans', value: '400+' },
            ].map((item, index) => {
              const Icon = item.icon
              return (
                <div key={index} className="text-center">
                  <Icon className="w-8 h-8 mx-auto mb-4" style={{ color: 'var(--color-accent-quaternary)' }} />
                  <div className="text-2xl font-bold mb-1" style={{ color: 'var(--color-text-inverse)' }}>
                    {item.value}
                  </div>
                  <div className="text-sm" style={{ color: 'var(--color-text-inverse)', opacity: 0.8 }}>
                    {item.label}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Right Panel - Content (Light) */}
      <div className="flex-1 flex flex-col justify-center px-6 sm:px-8 lg:px-12 py-12" style={{ backgroundColor: 'var(--color-bg-primary)' }}>
        <div className="max-w-lg mx-auto w-full lg:mx-0">
          {user ? (
            <>
              <h2 className="text-3xl font-bold mb-4" style={{ color: 'var(--color-text-primary)', fontFamily: 'var(--font-display)' }}>
                Welcome back, {user.full_name || user.username}!
              </h2>
              <p className="text-lg mb-8" style={{ color: 'var(--color-text-secondary)' }}>
                Ready to manage your library?
              </p>
              <div className="flex gap-3 mb-8">
                <Button onClick={() => navigate('/catalog')} className="flex-1 text-white" style={{ backgroundColor: 'var(--color-accent-primary)' }}>
                  Browse Books <ArrowRight className="ml-2 w-4 h-4" />
                </Button>
                <Button onClick={() => navigate('/dashboard')} className="flex-1" style={{ backgroundColor: 'var(--color-bg-secondary)', color: 'var(--color-text-primary)' }}>
                  View Dashboard
                </Button>
              </div>
            </>
          ) : (
            <>
              <h2 className="text-3xl font-bold mb-3" style={{ color: 'var(--color-text-primary)', fontFamily: 'var(--font-display)' }}>
                Welcome to Libris
              </h2>
              <p className="text-lg mb-8" style={{ color: 'var(--color-text-secondary)' }}>
                Your complete library management solution
              </p>
              <div className="space-y-3 mb-8">
                <Button onClick={() => navigate('/login')} className="w-full text-white" style={{ backgroundColor: 'var(--color-accent-primary)' }}>
                  Sign In
                </Button>
              </div>
            </>
          )}

          {/* Features Grid */}
          <div className="mt-12 pt-8" style={{ borderTop: '1px solid var(--color-border)' }}>
            <h3 className="font-semibold mb-6" style={{ color: 'var(--color-text-primary)' }}>
              Key Features
            </h3>
            <div className="space-y-4">
              {features.map((feature, index) => {
                const Icon = feature.icon
                return (
                  <button
                    key={index}
                    onClick={feature.action}
                    className="w-full flex gap-3 p-3 rounded-lg transition-colors hover:bg-gray-100"
                  >
                    <Icon className="w-5 h-5 flex-shrink-0 mt-1" style={{ color: 'var(--color-accent-primary)' }} />
                    <div className="text-left">
                      <div className="font-medium" style={{ color: 'var(--color-text-primary)' }}>
                        {feature.title}
                      </div>
                      <div className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                        {feature.description}
                      </div>
                    </div>
                  </button>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
