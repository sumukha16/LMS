import { useState, useEffect, useCallback } from 'react';
import {
  getBooks,
  getGenres,
  createBook,
  updateBook,
  deleteBook,
} from '@/lib/api';
import { useToast } from '@/contexts/ToastContext';
import {
  Search,
  Filter,
  Grid3X3,
  List,
  Plus,
  X,
  ChevronLeft,
  ChevronRight,
  Edit3,
  Trash2,
  CheckCircle,
  XCircle,
  BookOpen,
} from 'lucide-react';

interface Book {
  id: number;
  isbn: string;
  title: string;
  author: string;
  publisher: string;
  publication_year: number;
  genre: string;
  pages: number;
  description: string;
  cover_image_url: string;
  location_code: string;
  total_copies: number;
  available_copies: number;
}

export default function Catalog() {
  const [books, setBooks] = useState<Book[]>([]);
  const [genres, setGenres] = useState<string[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('');
  const [availability, setAvailability] = useState('');
  const [sort, setSort] = useState('title');
  const [loading, setLoading] = useState(true);
  const [detailBook, setDetailBook] = useState<Book | null>(null);
  const [editBook, setEditBook] = useState<Book | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const { showToast } = useToast();

  const loadBooks = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = { page: page.toString(), limit: '20', sort };
      if (searchQuery) params.q = searchQuery;
      if (selectedGenre) params.genre = selectedGenre;
      if (availability) params.availability = availability;
      const data = await getBooks(params);
      setBooks(data.books);
      setTotal(data.total);
      setTotalPages(data.totalPages);
    } catch {
      // handled by api
    } finally {
      setLoading(false);
    }
  }, [page, searchQuery, selectedGenre, availability, sort]);

  useEffect(() => {
    loadBooks();
    getGenres().then(data => setGenres(data.genres)).catch(() => {});
  }, [loadBooks]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadBooks();
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this book?')) return;
    try {
      await deleteBook(id);
      showToast('Book deleted successfully');
      loadBooks();
    } catch (err: unknown) {
      const error = err as Error;
      showToast(error.message, 'error');
    }
  };

  const handleSave = async (bookData: Record<string, unknown>) => {
    try {
      if (editBook) {
        await updateBook(editBook.id, bookData);
        showToast('Book updated successfully');
      } else {
        await createBook(bookData);
        showToast('Book created successfully');
      }
      setShowAddModal(false);
      setEditBook(null);
      loadBooks();
    } catch (err: unknown) {
      const error = err as Error;
      showToast(error.message, 'error');
    }
  };

  const availabilityDot = (book: Book) => {
    if (book.available_copies > 0) return 'bg-[#4A6741]';
    return 'bg-[#8B2942]';
  };

  const emptyBookForm = {
    isbn: '',
    title: '',
    author: '',
    publisher: '',
    publication_year: new Date().getFullYear(),
    genre: '',
    pages: 0,
    description: '',
    cover_image_url: '/assets/book_covers/cover_01.jpg',
    location_code: '',
    total_copies: 1,
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1
            className="text-[clamp(1.5rem,3vw,2.25rem)] font-medium text-[var(--color-text-primary)]"
            style={{ fontFamily: 'var(--font-display)' }}
          >
            Catalog
          </h1>
          <p className="text-[var(--color-text-secondary)] mt-1">
            {total} books in the library
          </p>
        </div>
        <button
          onClick={() => { setEditBook(null); setShowAddModal(true); }}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-[var(--color-accent-primary)] text-white rounded-lg text-sm font-medium hover:bg-[var(--color-accent-primary)]/90 transition-all"
        >
          <Plus className="w-4 h-4" />
          Add Book
        </button>
      </div>

      {/* Search & Filters */}
      <div className="bg-white rounded-[10px] shadow-[0_1px_3px_rgba(45,42,38,0.08)] p-4">
        <form onSubmit={handleSearch} className="flex flex-col lg:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--color-text-muted)]" />
            <input
              type="text"
              placeholder="Search by title, author, ISBN..."
              value={searchQuery}
              onChange={(e) => { setSearchQuery(e.target.value); setPage(1); }}
              className="w-full h-10 pl-10 pr-4 rounded-lg border border-[var(--color-border)] text-sm text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:border-[var(--color-accent-primary)] transition-all"
            />
          </div>
          <div className="flex gap-2 flex-wrap">
            <select
              value={selectedGenre}
              onChange={(e) => { setSelectedGenre(e.target.value); setPage(1); }}
              className="h-10 px-3 rounded-lg border border-[var(--color-border)] text-sm text-[var(--color-text-primary)] bg-white focus:outline-none focus:border-[var(--color-accent-primary)]"
            >
              <option value="">All Genres</option>
              {genres.map(g => (
                <option key={g} value={g}>{g}</option>
              ))}
            </select>
            <select
              value={availability}
              onChange={(e) => { setAvailability(e.target.value); setPage(1); }}
              className="h-10 px-3 rounded-lg border border-[var(--color-border)] text-sm text-[var(--color-text-primary)] bg-white focus:outline-none focus:border-[var(--color-accent-primary)]"
            >
              <option value="">All</option>
              <option value="available">Available</option>
              <option value="checked_out">Checked Out</option>
            </select>
            <select
              value={sort}
              onChange={(e) => { setSort(e.target.value); setPage(1); }}
              className="h-10 px-3 rounded-lg border border-[var(--color-border)] text-sm text-[var(--color-text-primary)] bg-white focus:outline-none focus:border-[var(--color-accent-primary)]"
            >
              <option value="title">Title</option>
              <option value="author">Author</option>
              <option value="year">Year</option>
              <option value="newest">Newest</option>
            </select>
            <div className="flex rounded-lg border border-[var(--color-border)] overflow-hidden">
              <button
                type="button"
                onClick={() => setViewMode('grid')}
                className={`p-2.5 transition-colors ${viewMode === 'grid' ? 'bg-[var(--color-bg-secondary)] text-[var(--color-text-primary)]' : 'text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]'}`}
              >
                <Grid3X3 className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={() => setViewMode('list')}
                className={`p-2.5 transition-colors ${viewMode === 'list' ? 'bg-[var(--color-bg-secondary)] text-[var(--color-text-primary)]' : 'text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]'}`}
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* Book Grid/List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-3 border-[var(--color-accent-primary)]/30 border-t-[var(--color-accent-primary)] rounded-full animate-spin" />
        </div>
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-5">
          {books.map(book => (
            <div
              key={book.id}
              onClick={() => setDetailBook(book)}
              className="bg-white rounded-[10px] overflow-hidden shadow-[0_1px_3px_rgba(45,42,38,0.08),0_4px_12px_rgba(45,42,38,0.06)] hover:shadow-[0_2px_6px_rgba(45,42,38,0.10),0_8px_24px_rgba(45,42,38,0.08)] hover:-translate-y-0.5 transition-all duration-300 cursor-pointer group"
            >
              <div className="relative aspect-[2/3] overflow-hidden">
                <img
                  src={book.cover_image_url}
                  alt={book.title}
                  className="w-full h-full object-cover group-hover:scale-[1.03] transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-all duration-300 flex items-center justify-center opacity-0 group-hover:opacity-100">
                  <span className="px-4 py-2 bg-white/90 backdrop-blur-sm rounded-lg text-sm font-medium text-[var(--color-text-primary)]">
                    View Details
                  </span>
                </div>
              </div>
              <div className="p-3.5">
                <h3 className="text-sm font-medium text-[var(--color-text-primary)] truncate">{book.title}</h3>
                <p className="text-xs text-[var(--color-text-secondary)] mt-0.5 truncate">{book.author}</p>
                <div className="flex items-center gap-2 mt-2">
                  <span className="text-[10px] px-2 py-0.5 bg-[var(--color-bg-secondary)] rounded-full text-[var(--color-text-secondary)] uppercase tracking-wider">
                    {book.genre}
                  </span>
                  <span className={`w-2 h-2 rounded-full ${availabilityDot(book)}`} />
                  <span className="text-[10px] text-[var(--color-text-muted)]">
                    {book.available_copies}/{book.total_copies}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-[10px] shadow-[0_1px_3px_rgba(45,42,38,0.08)] overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[var(--color-border)]">
                <th className="text-left px-6 py-3 text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider">Book</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider">Author</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider hidden md:table-cell">Genre</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider">Status</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider hidden sm:table-cell">Location</th>
                <th className="text-right px-6 py-3 text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--color-border)]">
              {books.map(book => (
                <tr
                  key={book.id}
                  onClick={() => setDetailBook(book)}
                  className="hover:bg-[var(--color-bg-primary)]/50 transition-colors cursor-pointer"
                >
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <img
                        src={book.cover_image_url}
                        alt={book.title}
                        className="w-10 h-14 object-cover rounded"
                      />
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-[var(--color-text-primary)] truncate">{book.title}</p>
                        <p className="text-xs text-[var(--color-text-muted)]">{book.publication_year}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-[var(--color-text-secondary)]">{book.author}</td>
                  <td className="px-6 py-4 hidden md:table-cell">
                    <span className="text-xs px-2 py-1 bg-[var(--color-bg-secondary)] rounded-full text-[var(--color-text-secondary)]">
                      {book.genre}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${availabilityDot(book)}`} />
                      <span className="text-sm text-[var(--color-text-secondary)]">
                        {book.available_copies > 0 ? `${book.available_copies} available` : 'Out'}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-[var(--color-text-muted)] hidden sm:table-cell">{book.location_code}</td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-1">
                      <button
                        onClick={(e) => { e.stopPropagation(); setEditBook(book); setShowAddModal(true); }}
                        className="p-1.5 rounded-md hover:bg-[var(--color-bg-secondary)] text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] transition-colors"
                      >
                        <Edit3 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); handleDelete(book.id); }}
                        className="p-1.5 rounded-md hover:bg-[#8B2942]/10 text-[var(--color-text-muted)] hover:text-[#8B2942] transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="p-2 rounded-lg border border-[var(--color-border)] text-[var(--color-text-secondary)] disabled:opacity-40 hover:bg-[var(--color-bg-secondary)] transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
            const p = i + 1;
            return (
              <button
                key={p}
                onClick={() => setPage(p)}
                className={`w-9 h-9 rounded-lg text-sm font-medium transition-colors ${
                  page === p
                    ? 'bg-[var(--color-accent-primary)] text-white'
                    : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-secondary)]'
                }`}
              >
                {p}
              </button>
            );
          })}
          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="p-2 rounded-lg border border-[var(--color-border)] text-[var(--color-text-secondary)] disabled:opacity-40 hover:bg-[var(--color-bg-secondary)] transition-colors"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Book Detail Modal */}
      {detailBook && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-[rgba(58,31,45,0.5)] backdrop-blur-sm" onClick={() => setDetailBook(null)} />
          <div className="relative bg-white rounded-[10px] shadow-xl w-full max-w-[700px] max-h-[90vh] overflow-auto">
            <button
              onClick={() => setDetailBook(null)}
              className="absolute top-4 right-4 p-2 rounded-lg hover:bg-[var(--color-bg-secondary)] transition-colors z-10"
            >
              <X className="w-5 h-5 text-[var(--color-text-secondary)]" />
            </button>
            <div className="flex flex-col md:flex-row">
              <div className="md:w-[40%] p-6">
                <img
                  src={detailBook.cover_image_url}
                  alt={detailBook.title}
                  className="w-full aspect-[2/3] object-cover rounded-lg shadow-md"
                />
              </div>
              <div className="md:w-[60%] p-6 pt-2 md:pt-6">
                <h2
                  className="text-2xl font-medium text-[var(--color-text-primary)] leading-tight"
                  style={{ fontFamily: 'var(--font-display)' }}
                >
                  {detailBook.title}
                </h2>
                <p className="text-base text-[var(--color-text-secondary)] mt-1" style={{ fontFamily: 'var(--font-display)' }}>
                  {detailBook.author}
                </p>
                <div className="flex items-center gap-2 mt-3">
                  {detailBook.available_copies > 0 ? (
                    <span className="inline-flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full bg-[#4A6741]/10 text-[#4A6741] font-medium">
                      <CheckCircle className="w-3.5 h-3.5" />
                      Available ({detailBook.available_copies}/{detailBook.total_copies})
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full bg-[#8B2942]/10 text-[#8B2942] font-medium">
                      <XCircle className="w-3.5 h-3.5" />
                      Checked Out
                    </span>
                  )}
                </div>
                <div className="grid grid-cols-2 gap-3 mt-5">
                  {[
                    { label: 'ISBN', value: detailBook.isbn },
                    { label: 'Publisher', value: detailBook.publisher },
                    { label: 'Year', value: detailBook.publication_year?.toString() },
                    { label: 'Pages', value: detailBook.pages?.toString() },
                    { label: 'Genre', value: detailBook.genre },
                    { label: 'Location', value: detailBook.location_code },
                  ].map(item => (
                    <div key={item.label}>
                      <p className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider">{item.label}</p>
                      <p className="text-sm text-[var(--color-text-primary)] font-medium">{item.value || 'N/A'}</p>
                    </div>
                  ))}
                </div>
                {detailBook.description && (
                  <div className="mt-5">
                    <p className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Description</p>
                    <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed line-clamp-4">{detailBook.description}</p>
                  </div>
                )}
                <div className="flex gap-3 mt-6">
                  <button
                    onClick={() => { setDetailBook(null); }}
                    className="flex-1 h-10 bg-[var(--color-accent-primary)] text-white rounded-lg text-sm font-medium hover:bg-[var(--color-accent-primary)]/90 transition-all"
                  >
                    Check Out
                  </button>
                  <button
                    onClick={() => { setDetailBook(null); setEditBook(detailBook); setShowAddModal(true); }}
                    className="h-10 px-4 border border-[var(--color-border)] text-[var(--color-text-primary)] rounded-lg text-sm font-medium hover:bg-[var(--color-bg-primary)] transition-all"
                  >
                    Edit
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add/Edit Book Modal */}
      {showAddModal && (
        <BookFormModal
          book={editBook}
          genres={genres}
          onSave={handleSave}
          onClose={() => { setShowAddModal(false); setEditBook(null); }}
        />
      )}
    </div>
  );
}

function BookFormModal({
  book,
  genres,
  onSave,
  onClose,
}: {
  book: Book | null;
  genres: string[];
  onSave: (data: Record<string, unknown>) => void;
  onClose: () => void;
}) {
  const [formData, setFormData] = useState({
    isbn: book?.isbn || '',
    title: book?.title || '',
    author: book?.author || '',
    publisher: book?.publisher || '',
    publication_year: book?.publication_year || new Date().getFullYear(),
    genre: book?.genre || '',
    pages: book?.pages || 0,
    description: book?.description || '',
    cover_image_url: book?.cover_image_url || '/assets/book_covers/cover_01.jpg',
    location_code: book?.location_code || '',
    total_copies: book?.total_copies || 1,
    available_copies: book?.available_copies || 1,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  const updateField = (field: string, value: unknown) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-[rgba(58,31,45,0.5)] backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-white rounded-[10px] shadow-xl w-full max-w-[600px] max-h-[90vh] overflow-auto">
        <div className="sticky top-0 bg-white border-b border-[var(--color-border)] px-6 py-4 flex items-center justify-between">
          <h2 className="text-lg font-medium text-[var(--color-text-primary)]">
            {book ? 'Edit Book' : 'Add New Book'}
          </h2>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-[var(--color-bg-secondary)] transition-colors">
            <X className="w-5 h-5 text-[var(--color-text-secondary)]" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1.5">Title *</label>
              <input
                type="text"
                required
                value={formData.title}
                onChange={e => updateField('title', e.target.value)}
                className="w-full h-10 px-3 rounded-lg border border-[var(--color-border)] text-sm focus:outline-none focus:border-[var(--color-accent-primary)]"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1.5">Author *</label>
              <input
                type="text"
                required
                value={formData.author}
                onChange={e => updateField('author', e.target.value)}
                className="w-full h-10 px-3 rounded-lg border border-[var(--color-border)] text-sm focus:outline-none focus:border-[var(--color-accent-primary)]"
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1.5">ISBN *</label>
              <input
                type="text"
                required
                value={formData.isbn}
                onChange={e => updateField('isbn', e.target.value)}
                className="w-full h-10 px-3 rounded-lg border border-[var(--color-border)] text-sm focus:outline-none focus:border-[var(--color-accent-primary)]"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1.5">Publisher</label>
              <input
                type="text"
                value={formData.publisher}
                onChange={e => updateField('publisher', e.target.value)}
                className="w-full h-10 px-3 rounded-lg border border-[var(--color-border)] text-sm focus:outline-none focus:border-[var(--color-accent-primary)]"
              />
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1.5">Year</label>
              <input
                type="number"
                value={formData.publication_year}
                onChange={e => updateField('publication_year', parseInt(e.target.value))}
                className="w-full h-10 px-3 rounded-lg border border-[var(--color-border)] text-sm focus:outline-none focus:border-[var(--color-accent-primary)]"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1.5">Pages</label>
              <input
                type="number"
                value={formData.pages}
                onChange={e => updateField('pages', parseInt(e.target.value))}
                className="w-full h-10 px-3 rounded-lg border border-[var(--color-border)] text-sm focus:outline-none focus:border-[var(--color-accent-primary)]"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1.5">Copies</label>
              <input
                type="number"
                value={formData.total_copies}
                onChange={e => {
                  const val = parseInt(e.target.value);
                  updateField('total_copies', val);
                  updateField('available_copies', val);
                }}
                className="w-full h-10 px-3 rounded-lg border border-[var(--color-border)] text-sm focus:outline-none focus:border-[var(--color-accent-primary)]"
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1.5">Genre</label>
              <select
                value={formData.genre}
                onChange={e => updateField('genre', e.target.value)}
                className="w-full h-10 px-3 rounded-lg border border-[var(--color-border)] text-sm focus:outline-none focus:border-[var(--color-accent-primary)]"
              >
                <option value="">Select Genre</option>
                {genres.map(g => (
                  <option key={g} value={g}>{g}</option>
                ))}
                <option value="Fiction">Fiction</option>
                <option value="Non-Fiction">Non-Fiction</option>
                <option value="Science">Science</option>
                <option value="History">History</option>
                <option value="Art">Art</option>
                <option value="Children's">Children&apos;s</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1.5">Location</label>
              <input
                type="text"
                value={formData.location_code}
                onChange={e => updateField('location_code', e.target.value)}
                placeholder="e.g. FIC-A12"
                className="w-full h-10 px-3 rounded-lg border border-[var(--color-border)] text-sm focus:outline-none focus:border-[var(--color-accent-primary)]"
              />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1.5">Description</label>
            <textarea
              value={formData.description}
              onChange={e => updateField('description', e.target.value)}
              rows={3}
              className="w-full px-3 py-2 rounded-lg border border-[var(--color-border)] text-sm focus:outline-none focus:border-[var(--color-accent-primary)] resize-none"
            />
          </div>
          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 h-10 border border-[var(--color-border)] text-[var(--color-text-primary)] rounded-lg text-sm font-medium hover:bg-[var(--color-bg-primary)] transition-all"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 h-10 bg-[var(--color-accent-primary)] text-white rounded-lg text-sm font-medium hover:bg-[var(--color-accent-primary)]/90 transition-all"
            >
              {book ? 'Update Book' : 'Add Book'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}