import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  getDashboardStats,
  getRecentActivity,
  getLoanChartData,
  getCategoryChartData,
} from '@/lib/api';
import {
  BookOpen,
  Clock,
  AlertTriangle,
  Users,
  ArrowUpRight,
  ArrowDownRight,
  Plus,
  RotateCcw,
  UserPlus,
  Bookmark,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

interface Stats {
  totalBooks: number;
  totalCopies: number;
  activeLoans: number;
  overdueItems: number;
  newPatrons: number;
}

interface Loan {
  id: number;
  book: { title: string } | null;
  patron: { full_name: string; card_id: string } | null;
  due_date: string;
  days_remaining: number | null;
  days_color: string;
  status: string;
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [recentLoans, setRecentLoans] = useState<Loan[]>([]);
  const [loanChart, setLoanChart] = useState<{ labels: string[]; data: number[] }>({ labels: [], data: [] });
  const [categoryChart, setCategoryChart] = useState<{ labels: string[]; data: number[]; colors: string[] }>({ labels: [], data: [], colors: [] });
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    try {
      const [statsData, activityData, loansChartData, catChartData] = await Promise.all([
        getDashboardStats(),
        getRecentActivity(),
        getLoanChartData(12),
        getCategoryChartData(),
      ]);
      setStats(statsData);
      setRecentLoans(activityData.recentLoans?.slice(0, 6) || []);
      setLoanChart(loansChartData);
      setCategoryChart(catChartData);
    } catch {
      // handled by api
    } finally {
      setLoading(false);
    }
  }

  const statusBadge = (status: string, daysColor?: string) => {
    if (status === 'overdue') return 'bg-[#8B2942] text-white';
    if (status === 'returned') return 'bg-[var(--color-bg-secondary)] text-[var(--color-text-secondary)]';
    if (daysColor === 'red') return 'bg-[#8B2942]/10 text-[#8B2942]';
    if (daysColor === 'gold' || daysColor === 'orange') return 'bg-[#D4A843]/15 text-[#B85C38]';
    return 'bg-[#4A6741]/10 text-[#4A6741]';
  };

  const statusLabel = (loan: Loan) => {
    if (loan.status === 'returned') return 'Returned';
    if (loan.status === 'overdue') return 'Overdue';
    if (loan.days_remaining !== null) {
      if (loan.days_remaining < 0) return `${Math.abs(loan.days_remaining)}d overdue`;
      if (loan.days_remaining <= 3) return `${loan.days_remaining}d left`;
      return 'On Time';
    }
    return 'Active';
  };

  const pieData = categoryChart.labels.map((label, i) => ({
    name: label,
    value: categoryChart.data[i],
    color: categoryChart.colors[i] || '#8B2942',
  }));

  const lineData = loanChart.labels.map((label, i) => ({
    month: label,
    loans: loanChart.data[i],
  }));

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="w-8 h-8 border-3 border-[var(--color-accent-primary)]/30 border-t-[var(--color-accent-primary)] rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1
          className="text-[clamp(1.5rem,3vw,2.25rem)] font-medium text-[var(--color-text-primary)]"
          style={{ fontFamily: 'var(--font-display)' }}
        >
          Dashboard
        </h1>
        <p className="text-[var(--color-text-secondary)] mt-1">
          Overview of your library's activity and statistics
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {[
          {
            icon: BookOpen,
            value: stats?.totalBooks?.toLocaleString() || '0',
            label: 'Total Books',
            trend: `${stats?.totalCopies || 0} copies`,
            trendUp: true,
            iconBg: 'bg-[#4A6741]/10',
            iconColor: 'text-[#4A6741]',
          },
          {
            icon: Clock,
            value: stats?.activeLoans?.toLocaleString() || '0',
            label: 'Active Loans',
            trend: '98% on time',
            trendUp: true,
            iconBg: 'bg-[#3A7D8C]/10',
            iconColor: 'text-[#3A7D8C]',
          },
          {
            icon: AlertTriangle,
            value: stats?.overdueItems?.toLocaleString() || '0',
            label: 'Overdue Items',
            trend: '-5 from last week',
            trendUp: true,
            iconBg: 'bg-[#8B2942]/10',
            iconColor: 'text-[#8B2942]',
          },
          {
            icon: Users,
            value: '189',
            label: 'New Patrons',
            trend: '+12 this month',
            trendUp: true,
            iconBg: 'bg-[#B85C38]/10',
            iconColor: 'text-[#B85C38]',
          },
        ].map((card, i) => (
          <div
            key={i}
            className="bg-white rounded-[10px] p-6 shadow-[0_1px_3px_rgba(45,42,38,0.08),0_4px_12px_rgba(45,42,38,0.06)] hover:shadow-[0_2px_6px_rgba(45,42,38,0.10),0_8px_24px_rgba(45,42,38,0.08)] transition-all duration-300"
          >
            <div className="flex items-start justify-between mb-4">
              <div className={`w-11 h-11 rounded-lg ${card.iconBg} flex items-center justify-center`}>
                <card.icon className={`w-5 h-5 ${card.iconColor}`} />
              </div>
            </div>
            <p
              className="text-[clamp(1.5rem,3vw,2rem)] font-medium text-[var(--color-text-primary)] leading-tight"
              style={{ fontFamily: 'var(--font-display)' }}
            >
              {card.value}
            </p>
            <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mt-1">
              {card.label}
            </p>
            <div className="flex items-center gap-1 mt-2">
              {card.trendUp ? (
                <ArrowUpRight className="w-3.5 h-3.5 text-[#4A6741]" />
              ) : (
                <ArrowDownRight className="w-3.5 h-3.5 text-[var(--color-accent-secondary)]" />
              )}
              <span className="text-xs text-[#4A6741] font-medium">{card.trend}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions + Recent Loans */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Recent Loans */}
        <div className="lg:col-span-2 bg-white rounded-[10px] shadow-[0_1px_3px_rgba(45,42,38,0.08),0_4px_12px_rgba(45,42,38,0.06)] overflow-hidden">
          <div className="px-6 py-4 border-b border-[var(--color-border)] flex items-center justify-between">
            <h3 className="font-medium text-[var(--color-text-primary)]">Recent Loans</h3>
            <button
              onClick={() => navigate('/loans')}
              className="text-xs text-[var(--color-accent-primary)] hover:underline font-medium"
            >
              View All
            </button>
          </div>
          <div className="divide-y divide-[var(--color-border)]">
            {recentLoans.map(loan => (
              <div
                key={loan.id}
                className="px-6 py-3.5 flex items-center justify-between hover:bg-[var(--color-bg-primary)]/50 transition-colors"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-[var(--color-text-primary)] truncate">
                    {loan.book?.title || 'Unknown Book'}
                  </p>
                  <p className="text-xs text-[var(--color-text-secondary)]">
                    {loan.patron?.full_name || 'Unknown'} · Card {loan.patron?.card_id}
                  </p>
                </div>
                <div className="flex items-center gap-3 ml-4">
                  <span className="text-xs text-[var(--color-text-muted)]">
                    {loan.due_date ? new Date(loan.due_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : ''}
                  </span>
                  <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${statusBadge(loan.status, loan.days_color)}`}>
                    {statusLabel(loan)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-[10px] shadow-[0_1px_3px_rgba(45,42,38,0.08),0_4px_12px_rgba(45,42,38,0.06)] p-6">
          <h3 className="font-medium text-[var(--color-text-primary)] mb-4">Quick Actions</h3>
          <div className="space-y-3">
            {[
              { icon: Plus, label: 'Check Out Book', primary: true, action: () => navigate('/checkout') },
              { icon: RotateCcw, label: 'Check In Book', primary: false, action: () => navigate('/loans') },
              { icon: UserPlus, label: 'Add New Patron', primary: false, action: () => navigate('/patrons') },
              { icon: Bookmark, label: 'Place Hold', primary: false, action: () => navigate('/reservations') },
            ].map((action, i) => (
              <button
                key={i}
                onClick={action.action}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                  action.primary
                    ? 'bg-[var(--color-accent-primary)] text-white hover:bg-[var(--color-accent-primary)]/90'
                    : 'border border-[var(--color-border)] text-[var(--color-text-primary)] hover:bg-[var(--color-bg-primary)]'
                }`}
              >
                <action.icon className="w-4 h-4" />
                {action.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Monthly Loans Chart */}
        <div className="bg-white rounded-[10px] shadow-[0_1px_3px_rgba(45,42,38,0.08),0_4px_12px_rgba(45,42,38,0.06)] p-6">
          <h3 className="font-medium text-[var(--color-text-primary)] mb-6">Monthly Loans</h3>
          <div className="h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={lineData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis
                  dataKey="month"
                  tick={{ fontSize: 11, fill: 'var(--color-text-muted)' }}
                  axisLine={{ stroke: 'var(--color-border)' }}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 11, fill: 'var(--color-text-muted)' }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  contentStyle={{
                    background: 'white',
                    border: '1px solid var(--color-border)',
                    borderRadius: '8px',
                    boxShadow: '0 4px 16px rgba(45,42,38,0.12)',
                    fontSize: '13px',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="loans"
                  stroke="var(--color-accent-primary)"
                  strokeWidth={2}
                  dot={{ r: 4, fill: 'var(--color-accent-primary)', strokeWidth: 0 }}
                  activeDot={{ r: 6 }}
                  fillOpacity={0.1}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Popular Categories */}
        <div className="bg-white rounded-[10px] shadow-[0_1px_3px_rgba(45,42,38,0.08),0_4px_12px_rgba(45,42,38,0.06)] p-6">
          <h3 className="font-medium text-[var(--color-text-primary)] mb-6">Popular Categories</h3>
          <div className="flex items-center gap-8">
            <div className="w-[200px] h-[200px] shrink-0">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={90}
                    paddingAngle={2}
                    dataKey="value"
                    stroke="none"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      background: 'white',
                      border: '1px solid var(--color-border)',
                      borderRadius: '8px',
                      boxShadow: '0 4px 16px rgba(45,42,38,0.12)',
                      fontSize: '13px',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex-1 space-y-3">
              {pieData.map((item, i) => (
                <div key={i} className="flex items-center gap-3">
                  <span
                    className="w-3 h-3 rounded-full shrink-0"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-sm text-[var(--color-text-primary)] flex-1">{item.name}</span>
                  <span className="text-sm font-medium text-[var(--color-text-secondary)]">{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}