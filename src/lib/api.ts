const API_BASE = import.meta.env.VITE_API_BASE || 'https://lms-xb2q.onrender.com/api';


function getToken(): string | null {
  return localStorage.getItem('libris_token');
}

async function apiRequest(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE}${endpoint}`;
  const token = getToken();
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((options.headers as Record<string, string>) || {}),
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(url, {
    ...options,
    headers,
  });
  
  if (response.status === 401) {
    localStorage.removeItem('libris_token');
    localStorage.removeItem('libris_user');
    window.location.href = '/login';
    throw new Error('Session expired');
  }
  
  const data = await response.json();
  
  if (!response.ok) {
    throw new Error(data.error || 'Something went wrong');
  }
  
  return data;
}

// Auth
export const login = (username: string, password: string) =>
  apiRequest('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) });

export const getMe = () =>
  apiRequest('/auth/me', { method: 'GET' });

// Dashboard
export const getDashboardStats = () =>
  apiRequest('/dashboard/stats', { method: 'GET' });

export const getRecentActivity = () =>
  apiRequest('/dashboard/activity', { method: 'GET' });

export const getLoanChartData = (months?: number) =>
  apiRequest(`/dashboard/charts/loans${months ? `?months=${months}` : ''}`, { method: 'GET' });

export const getCategoryChartData = () =>
  apiRequest('/dashboard/charts/categories', { method: 'GET' });

// Books
export const getBooks = (params?: Record<string, string>) => {
  const query = params ? '?' + new URLSearchParams(params).toString() : '';
  return apiRequest(`/books${query}`, { method: 'GET' });
};

export const getBook = (id: number) =>
  apiRequest(`/books/${id}`, { method: 'GET' });

export const createBook = (data: Record<string, unknown>) =>
  apiRequest('/books', { method: 'POST', body: JSON.stringify(data) });

export const updateBook = (id: number, data: Record<string, unknown>) =>
  apiRequest(`/books/${id}`, { method: 'PUT', body: JSON.stringify(data) });

export const deleteBook = (id: number) =>
  apiRequest(`/books/${id}`, { method: 'DELETE' });

export const getGenres = () =>
  apiRequest('/books/genres', { method: 'GET' });

// Patrons
export const getPatrons = (params?: Record<string, string>) => {
  const query = params ? '?' + new URLSearchParams(params).toString() : '';
  return apiRequest(`/patrons${query}`, { method: 'GET' });
};

export const getPatron = (id: number) =>
  apiRequest(`/patrons/${id}`, { method: 'GET' });

export const createPatron = (data: Record<string, unknown>) =>
  apiRequest('/patrons', { method: 'POST', body: JSON.stringify(data) });

export const updatePatron = (id: number, data: Record<string, unknown>) =>
  apiRequest(`/patrons/${id}`, { method: 'PUT', body: JSON.stringify(data) });

export const deletePatron = (id: number) =>
  apiRequest(`/patrons/${id}`, { method: 'DELETE' });

export const getPatronLoans = (id: number, status?: string) => {
  const query = status ? `?status=${status}` : '';
  return apiRequest(`/patrons/${id}/loans${query}`, { method: 'GET' });
};

export const getPatronFines = (id: number) =>
  apiRequest(`/patrons/${id}/fines`, { method: 'GET' });

// Loans
export const getLoans = (params?: Record<string, string>) => {
  const query = params ? '?' + new URLSearchParams(params).toString() : '';
  return apiRequest(`/loans${query}`, { method: 'GET' });
};

export const getLoan = (id: number) =>
  apiRequest(`/loans/${id}`, { method: 'GET' });

export const checkoutBooks = (patronId: number, bookIds: number[]) =>
  apiRequest('/loans/checkout', { method: 'POST', body: JSON.stringify({ patron_id: patronId, book_ids: bookIds }) });

export const checkinBook = (loanId?: number, bookId?: number) =>
  apiRequest('/loans/checkin', { method: 'POST', body: JSON.stringify(loanId ? { loan_id: loanId } : { book_id: bookId }) });

export const renewLoan = (id: number) =>
  apiRequest(`/loans/${id}/renew`, { method: 'POST' });

export const getOverdueLoans = () =>
  apiRequest('/loans/overdue', { method: 'GET' });

export const payFine = (loanId: number) =>
  apiRequest(`/loans/pay-fine/${loanId}`, { method: 'POST' });

// Reservations
export const getReservations = (params?: Record<string, string>) => {
  const query = params ? '?' + new URLSearchParams(params).toString() : '';
  return apiRequest(`/reservations${query}`, { method: 'GET' });
};

export const createReservation = (patronId: number, bookId: number) =>
  apiRequest('/reservations', { method: 'POST', body: JSON.stringify({ patron_id: patronId, book_id: bookId }) });

export const cancelReservation = (id: number) =>
  apiRequest(`/reservations/${id}/cancel`, { method: 'PUT' });

// Reports
export const getLoanReport = (from?: string, to?: string) => {
  const params = new URLSearchParams();
  if (from) params.append('from', from);
  if (to) params.append('to', to);
  const query = params.toString() ? `?${params.toString()}` : '';
  return apiRequest(`/reports/loans${query}`, { method: 'GET' });
};

export const getOverdueReport = () =>
  apiRequest('/reports/overdue', { method: 'GET' });

export const getPopularBooks = (from?: string, to?: string) => {
  const params = new URLSearchParams();
  if (from) params.append('from', from);
  if (to) params.append('to', to);
  const query = params.toString() ? `?${params.toString()}` : '';
  return apiRequest(`/reports/popular${query}`, { method: 'GET' });
};
