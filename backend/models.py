from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random

db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False, index=True)
    author = db.Column(db.String(200), nullable=False, index=True)
    publisher = db.Column(db.String(100))
    publication_year = db.Column(db.Integer)
    genre = db.Column(db.String(50), index=True)
    pages = db.Column(db.Integer)
    description = db.Column(db.Text)
    cover_image_url = db.Column(db.String(500))
    location_code = db.Column(db.String(20))
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    loans = db.relationship('Loan', backref='book', lazy=True)
    reservations = db.relationship('Reservation', backref='book', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'isbn': self.isbn,
            'title': self.title,
            'author': self.author,
            'publisher': self.publisher,
            'publication_year': self.publication_year,
            'genre': self.genre,
            'pages': self.pages,
            'description': self.description,
            'cover_image_url': self.cover_image_url,
            'location_code': self.location_code,
            'total_copies': self.total_copies,
            'available_copies': self.available_copies,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Patron(db.Model):
    __tablename__ = 'patrons'
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), unique=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')
    membership_type = db.Column(db.String(20), default='standard')
    max_loans = db.Column(db.Integer, default=5)
    loan_period_days = db.Column(db.Integer, default=14)
    fine_balance = db.Column(db.Numeric(10, 2), default=0)
    join_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    loans = db.relationship('Loan', backref='patron', lazy=True)
    reservations = db.relationship('Reservation', backref='patron', lazy=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def active_loans(self):
        return [loan for loan in self.loans if loan.status == 'active']

    def to_dict(self):
        return {
            'id': self.id,
            'card_id': self.card_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'status': self.status,
            'membership_type': self.membership_type,
            'max_loans': self.max_loans,
            'loan_period_days': self.loan_period_days,
            'fine_balance': float(self.fine_balance),
            'join_date': self.join_date.isoformat() if self.join_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'active_loans_count': len(self.active_loans),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Loan(db.Model):
    __tablename__ = 'loans'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    patron_id = db.Column(db.Integer, db.ForeignKey('patrons.id'), nullable=False)
    loan_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date)
    renewal_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='active')
    fine_amount = db.Column(db.Numeric(10, 2), default=0)
    fine_paid = db.Column(db.Boolean, default=False)
    checked_out_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    checked_in_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    checkout_user = db.relationship('User', foreign_keys=[checked_out_by], backref='checkouts')
    checkin_user = db.relationship('User', foreign_keys=[checked_in_by], backref='checkins')

    @property
    def days_remaining(self):
        if self.status == 'returned':
            return None
        today = datetime.now().date()
        return (self.due_date - today).days

    @property
    def is_overdue(self):
        if self.status == 'returned':
            return False
        return datetime.now().date() > self.due_date

    def calculate_fine(self):
        if self.status == 'returned' and self.return_date and self.return_date > self.due_date:
            days = (self.return_date - self.due_date).days
            return days * 0.50
        elif self.status == 'active' and self.is_overdue:
            days = (datetime.now().date() - self.due_date).days
            return days * 0.50
        return 0

    def to_dict(self):
        days = self.days_remaining
        days_color = 'green'
        if days is not None:
            if days < 0:
                days_color = 'red'
            elif days <= 3:
                days_color = 'gold'
            elif days <= 7:
                days_color = 'orange'

        return {
            'id': self.id,
            'book_id': self.book_id,
            'book': self.book.to_dict() if self.book else None,
            'patron_id': self.patron_id,
            'patron': {
                'id': self.patron.id,
                'full_name': self.patron.full_name,
                'card_id': self.patron.card_id
            } if self.patron else None,
            'loan_date': self.loan_date.isoformat() if self.loan_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'renewal_count': self.renewal_count,
            'status': self.status,
            'fine_amount': float(self.fine_amount),
            'fine_paid': self.fine_paid,
            'days_remaining': days,
            'days_color': days_color,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    patron_id = db.Column(db.Integer, db.ForeignKey('patrons.id'), nullable=False)
    reservation_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')
    notification_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'book': self.book.to_dict() if self.book else None,
            'patron_id': self.patron_id,
            'patron': {
                'id': self.patron.id,
                'full_name': self.patron.full_name,
                'card_id': self.patron.card_id
            } if self.patron else None,
            'reservation_date': self.reservation_date.isoformat() if self.reservation_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'status': self.status,
            'notification_sent': self.notification_sent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(200))
    role = db.Column(db.String(20), default='librarian')
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ActivityLog(db.Model):
    __tablename__ = 'activity_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(50), nullable=False)
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='activities')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'details': self.details,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }