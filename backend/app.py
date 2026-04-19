import os
import sys
import random
from datetime import datetime, timedelta, date
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import or_, func, extract

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models import db, Book, Patron, Loan, Reservation, User, ActivityLog

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///libris.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'libris-secret-key-2024-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

CORS(app)
jwt = JWTManager(app)
db.init_app(app)

# =============================================================================
# SEED DATA
# =============================================================================

def seed_data():
    # Clear existing data
    db.session.query(ActivityLog).delete()
    db.session.query(Reservation).delete()
    db.session.query(Loan).delete()
    db.session.query(Patron).delete()
    db.session.query(Book).delete()
    db.session.query(User).delete()
    db.session.commit()

    # Create users
    admin = User(username='admin', email='admin@libris.lib', full_name='System Administrator', role='admin')
    admin.set_password('admin123')
    
    librarian1 = User(username='sarah.chen', email='sarah@libris.lib', full_name='Sarah Chen', role='librarian')
    librarian1.set_password('lib123')
    
    librarian2 = User(username='james.wilson', email='james@libris.lib', full_name='James Wilson', role='librarian')
    librarian2.set_password('lib123')
    
    db.session.add_all([admin, librarian1, librarian2])
    db.session.commit()

    # Create patrons
    patrons_data = [
        {'card_id': 'P001', 'first_name': 'Emma', 'last_name': 'Thompson', 'email': 'emma.t@email.com', 'phone': '555-0101', 'address': '42 Maple Street, Springfield', 'status': 'active', 'membership_type': 'standard'},
        {'card_id': 'P002', 'first_name': 'Oliver', 'last_name': 'Martinez', 'email': 'oliver.m@email.com', 'phone': '555-0102', 'address': '18 Oak Avenue, Springfield', 'status': 'active', 'membership_type': 'student'},
        {'card_id': 'P003', 'first_name': 'Sophia', 'last_name': 'Anderson', 'email': 'sophia.a@email.com', 'phone': '555-0103', 'address': '7 Pine Road, Springfield', 'status': 'active', 'membership_type': 'standard'},
        {'card_id': 'P004', 'first_name': 'Liam', 'last_name': 'Johnson', 'email': 'liam.j@email.com', 'phone': '555-0104', 'address': '33 Cedar Lane, Springfield', 'status': 'active', 'membership_type': 'senior'},
        {'card_id': 'P005', 'first_name': 'Ava', 'last_name': 'Williams', 'email': 'ava.w@email.com', 'phone': '555-0105', 'address': '21 Birch Drive, Springfield', 'status': 'active', 'membership_type': 'standard'},
        {'card_id': 'P006', 'first_name': 'Noah', 'last_name': 'Brown', 'email': 'noah.b@email.com', 'phone': '555-0106', 'address': '56 Elm Street, Springfield', 'status': 'active', 'membership_type': 'student'},
        {'card_id': 'P007', 'first_name': 'Isabella', 'last_name': 'Davis', 'email': 'isabella.d@email.com', 'phone': '555-0107', 'address': '9 Willow Way, Springfield', 'status': 'active', 'membership_type': 'standard'},
        {'card_id': 'P008', 'first_name': 'Mason', 'last_name': 'Miller', 'email': 'mason.m@email.com', 'phone': '555-0108', 'address': '44 Spruce Court, Springfield', 'status': 'suspended', 'membership_type': 'standard'},
        {'card_id': 'P009', 'first_name': 'Mia', 'last_name': 'Wilson', 'email': 'mia.w@email.com', 'phone': '555-0109', 'address': '15 Ash Boulevard, Springfield', 'status': 'active', 'membership_type': 'staff'},
        {'card_id': 'P010', 'first_name': 'Lucas', 'last_name': 'Moore', 'email': 'lucas.m@email.com', 'phone': '555-0110', 'address': '28 Redwood Circle, Springfield', 'status': 'active', 'membership_type': 'standard'},
        {'card_id': 'P011', 'first_name': 'Charlotte', 'last_name': 'Taylor', 'email': 'charlotte.t@email.com', 'phone': '555-0111', 'address': '61 Hickory Place, Springfield', 'status': 'active', 'membership_type': 'student'},
        {'card_id': 'P012', 'first_name': 'Ethan', 'last_name': 'Thomas', 'email': 'ethan.t@email.com', 'phone': '555-0112', 'address': '3 Dogwood Terrace, Springfield', 'status': 'active', 'membership_type': 'standard'},
        {'card_id': 'P013', 'first_name': 'Amelia', 'last_name': 'Jackson', 'email': 'amelia.j@email.com', 'phone': '555-0113', 'address': '72 Magnolia Ave, Springfield', 'status': 'active', 'membership_type': 'standard'},
        {'card_id': 'P014', 'first_name': 'Alexander', 'last_name': 'White', 'email': 'alex.w@email.com', 'phone': '555-0114', 'address': '19 Cypress Street, Springfield', 'status': 'active', 'membership_type': 'senior'},
        {'card_id': 'P015', 'first_name': 'Harper', 'last_name': 'Harris', 'email': 'harper.h@email.com', 'phone': '555-0115', 'address': '38 Juniper Road, Springfield', 'status': 'active', 'membership_type': 'student'},
        {'card_id': 'P016', 'first_name': 'Daniel', 'last_name': 'Martin', 'email': 'daniel.m@email.com', 'phone': '555-0116', 'address': '55 Fir Lane, Springfield', 'status': 'active', 'membership_type': 'standard'},
        {'card_id': 'P017', 'first_name': 'Evelyn', 'last_name': 'Garcia', 'email': 'evelyn.g@email.com', 'phone': '555-0117', 'address': '12 Poplar Drive, Springfield', 'status': 'active', 'membership_type': 'standard'},
        {'card_id': 'P018', 'first_name': 'Matthew', 'last_name': 'Rodriguez', 'email': 'matthew.r@email.com', 'phone': '555-0118', 'address': '47 Sycamore Way, Springfield', 'status': 'expired', 'membership_type': 'standard'},
        {'card_id': 'P019', 'first_name': 'Abigail', 'last_name': 'Lopez', 'email': 'abigail.l@email.com', 'phone': '555-0119', 'address': '24 Chestnut Court, Springfield', 'status': 'active', 'membership_type': 'student'},
        {'card_id': 'P020', 'first_name': 'Henry', 'last_name': 'Lee', 'email': 'henry.l@email.com', 'phone': '555-0120', 'address': '89 Walnut Street, Springfield', 'status': 'active', 'membership_type': 'standard'},
    ]

    patrons = []
    for p in patrons_data:
        patron = Patron(
            card_id=p['card_id'],
            first_name=p['first_name'],
            last_name=p['last_name'],
            email=p['email'],
            phone=p['phone'],
            address=p['address'],
            status=p['status'],
            membership_type=p['membership_type'],
            max_loans=7 if p['membership_type'] == 'staff' else (3 if p['membership_type'] == 'student' else 5),
            loan_period_days=21 if p['membership_type'] == 'staff' else 14,
            join_date=date(2023, random.randint(1, 12), random.randint(1, 28)),
            expiry_date=date(2025, 12, 31)
        )
        patrons.append(patron)
    
    db.session.add_all(patrons)
    db.session.commit()

    # Create books
    books_data = [
        {'isbn': '978031645', 'title': 'The Last Garden', 'author': 'Eleanor Vance', 'publisher': 'Riverhead Books', 'publication_year': 2023, 'genre': 'Fiction', 'pages': 342, 'description': 'A haunting literary novel about loss, memory, and the healing power of nature. Set in a decaying Victorian estate, the story follows a botanist who returns to her childhood home to discover secrets buried in the overgrown gardens.', 'cover_image_url': '/assets/book_covers/cover_01.jpg', 'location_code': 'FIC-A12', 'total_copies': 3, 'available_copies': 1},
        {'isbn': '978039388', 'title': 'Quantum Worlds', 'author': 'Dr. Elara Vance', 'publisher': 'W.W. Norton', 'publication_year': 2024, 'genre': 'Science', 'pages': 416, 'description': 'An accessible yet rigorous exploration of quantum mechanics and its philosophical implications. Dr. Vance takes readers on a journey through parallel universes, entanglement, and the nature of reality itself.', 'cover_image_url': '/assets/book_covers/cover_02.jpg', 'location_code': 'SCI-B03', 'total_copies': 2, 'available_copies': 2},
        {'isbn': '978052555', 'title': 'Empires of Sand', 'author': 'Marcus Halid', 'publisher': 'Viking Press', 'publication_year': 2022, 'genre': 'History', 'pages': 528, 'description': 'A sweeping historical narrative that traces the rise and fall of ancient desert civilizations from Mesopotamia to the Sahara. Rich with archaeological detail and vivid storytelling.', 'cover_image_url': '/assets/book_covers/cover_03.jpg', 'location_code': 'HIS-C07', 'total_copies': 4, 'available_copies': 2},
        {'isbn': '978006289', 'title': 'The Silent Key', 'author': 'Eleanor Vance', 'publisher': 'HarperCollins', 'publication_year': 2024, 'genre': 'Mystery', 'pages': 298, 'description': 'A atmospheric mystery set in Victorian London. When a renowned pianist is found dead, Detective Inspector Blackwood must follow a trail of cryptic clues left by the victim through the foggy streets of the city.', 'cover_image_url': '/assets/book_covers/cover_04.jpg', 'location_code': 'MYS-A08', 'total_copies': 3, 'available_copies': 1},
        {'isbn': '978031641', 'title': "Milo's Moon Adventure", 'author': 'Luna Lovegood', 'publisher': 'Little Brown', 'publication_year': 2023, 'genre': "Children's", 'pages': 48, 'description': 'A heartwarming children\'s book about a brave little mouse who builds a rocket and travels to the moon. Beautifully illustrated, this tale teaches children about courage, friendship, and following their dreams.', 'cover_image_url': '/assets/book_covers/cover_05.jpg', 'location_code': 'CHI-D01', 'total_copies': 5, 'available_copies': 3},
        {'isbn': '978030026', 'title': 'Impressionist Light', 'author': 'Claire Monet', 'publisher': 'Yale University Press', 'publication_year': 2024, 'genre': 'Art', 'pages': 256, 'description': 'A stunning visual journey through the world of Impressionist painting. Features high-quality reproductions and expert commentary on the techniques and lives of Monet, Renoir, Degas, and their contemporaries.', 'cover_image_url': '/assets/book_covers/cover_06.jpg', 'location_code': 'ART-E04', 'total_copies': 2, 'available_copies': 1},
        {'isbn': '978059323', 'title': 'Feasts of the Mediterranean', 'author': 'Sofia Marinelli', 'publisher': 'Penguin Random House', 'publication_year': 2023, 'genre': 'Cooking', 'pages': 384, 'description': 'A comprehensive cookbook celebrating the diverse cuisines of the Mediterranean. From Spanish tapas to Greek mezze, Turkish kebabs to Moroccan tagines, this book is a culinary journey through sun-drenched shores.', 'cover_image_url': '/assets/book_covers/cover_07.jpg', 'location_code': 'COO-F02', 'total_copies': 3, 'available_copies': 2},
        {'isbn': '978125027', 'title': 'Red Terminal', 'author': 'J.P. Alston', 'publisher': 'St. Martin\'s Press', 'publication_year': 2024, 'genre': 'Thriller', 'pages': 432, 'description': 'A high-octane thriller set in the Moscow Metro. When a hacker discovers a plot to crash the entire subway system, they have 24 hours to navigate the underground labyrinth and prevent a catastrophe.', 'cover_image_url': '/assets/book_covers/cover_08.jpg', 'location_code': 'THR-A15', 'total_copies': 3, 'available_copies': 1},
        {'isbn': '978006297', 'title': 'Whispers in Rain', 'author': 'Elara Vance', 'publisher': 'Harper Perennial', 'publication_year': 2022, 'genre': 'Poetry', 'pages': 128, 'description': 'A luminous poetry collection that explores themes of love, loss, and the quiet beauty of everyday moments. Vance\'s delicate verse captures the melancholy and magic of rain-soaked landscapes.', 'cover_image_url': '/assets/book_covers/cover_09.jpg', 'location_code': 'POE-G01', 'total_copies': 2, 'available_copies': 2},
        {'isbn': '978037460', 'title': 'The Architect of Dreams', 'author': 'Elara Vance', 'publisher': 'Farrar, Straus and Giroux', 'publication_year': 2023, 'genre': 'Biography', 'pages': 512, 'description': 'The definitive biography of a visionary architect who shaped the skyline of early 20th century America. Drawing on previously unpublished letters and drawings, this book reveals the man behind the monuments.', 'cover_image_url': '/assets/book_covers/cover_10.jpg', 'location_code': 'BIO-H06', 'total_copies': 2, 'available_copies': 0},
        {'isbn': '978076539', 'title': 'Throne of Ash', 'author': 'L.M. Frost', 'publisher': 'Tor Books', 'publication_year': 2024, 'genre': 'Fantasy', 'pages': 688, 'description': 'An epic fantasy saga of war, dragons, and ancient magic. When the Obsidian Throne is shattered, three unlikely heroes must gather the fragments before the Shadow King rises to claim them all.', 'cover_image_url': '/assets/book_covers/cover_11.jpg', 'location_code': 'FAN-A22', 'total_copies': 4, 'available_copies': 2},
        {'isbn': '978059365', 'title': 'The Focus Habit', 'author': 'Dr. Anna Lee', 'publisher': 'Crown Publishing', 'publication_year': 2023, 'genre': 'Self-Help', 'pages': 240, 'description': 'A science-based guide to developing deep focus in a distracted world. Dr. Lee combines cognitive psychology research with practical exercises to help readers reclaim their attention and achieve their goals.', 'cover_image_url': '/assets/book_covers/cover_12.jpg', 'location_code': 'SEL-I03', 'total_copies': 3, 'available_copies': 3},
        {'isbn': '978163557', 'title': 'Paths Less Taken', 'author': 'Alistair Finch', 'publisher': 'National Geographic', 'publication_year': 2024, 'genre': 'Travel', 'pages': 320, 'description': 'A photographic journey to the world\'s most remote and beautiful destinations. Finch shares stories from his travels through the Himalayas, Patagonia, the Sahara, and beyond, with breathtaking landscape photography.', 'cover_image_url': '/assets/book_covers/cover_13.jpg', 'location_code': 'TRA-J02', 'total_copies': 2, 'available_copies': 1},
        {'isbn': '978059349', 'title': 'Letters from Lisbon', 'author': 'Sofia Guerra', 'publisher': 'Knopf', 'publication_year': 2023, 'genre': 'Romance', 'pages': 368, 'description': 'A sweeping romance told through letters exchanged between a Portuguese ceramicist and an American journalist in 1950s Lisbon. Rich with the sights, sounds, and flavors of Portugal.', 'cover_image_url': '/assets/book_covers/cover_14.jpg', 'location_code': 'ROM-A18', 'total_copies': 3, 'available_copies': 1},
        {'isbn': '978026204', 'title': 'Code and Consciousness', 'author': 'Alex Thompson', 'publisher': 'MIT Press', 'publication_year': 2024, 'genre': 'Technology', 'pages': 448, 'description': 'A provocative examination of artificial intelligence and the nature of consciousness. Thompson argues that understanding machine intelligence requires us to fundamentally rethink what it means to be conscious.', 'cover_image_url': '/assets/book_covers/cover_15.jpg', 'location_code': 'TEC-K01', 'total_copies': 2, 'available_copies': 2},
        {'isbn': '978069122', 'title': 'The Examined Life', 'author': 'Aristotle', 'publisher': 'Princeton University Press', 'publication_year': 2024, 'genre': 'Philosophy', 'pages': 384, 'description': 'A new translation and commentary on Aristotle\'s ethical writings, making ancient wisdom accessible to modern readers. Essential reading for anyone interested in living a thoughtful, purposeful life.', 'cover_image_url': '/assets/book_covers/cover_16.jpg', 'location_code': 'PHI-L04', 'total_copies': 3, 'available_copies': 1},
        {'isbn': '978160309', 'title': 'Starlight City', 'author': 'Alex Chen', 'publisher': 'Image Comics', 'publication_year': 2024, 'genre': 'Graphic Novel', 'pages': 176, 'description': 'A cyberpunk graphic novel set in a neon-lit megacity of 2089. A street-level hacker discovers a conspiracy that reaches the highest towers of the corporate elite. Stunning full-color artwork on every page.', 'cover_image_url': '/assets/book_covers/cover_17.jpg', 'location_code': 'GRA-M01', 'total_copies': 4, 'available_copies': 2},
        {'isbn': '978039386', 'title': 'Forest Echoes', 'author': 'Isabella Reed', 'publisher': 'W.W. Norton', 'publication_year': 2023, 'genre': 'Nature', 'pages': 288, 'description': 'A meditative exploration of old-growth forests and their hidden ecosystems. Reed combines scientific observation with lyrical prose to reveal the complex, interconnected world beneath the canopy.', 'cover_image_url': '/assets/book_covers/cover_18.jpg', 'location_code': 'NAT-N02', 'total_copies': 2, 'available_copies': 2},
        {'isbn': '978006315', 'title': 'The Quiet Leader', 'author': 'Anna Harvard', 'publisher': 'Harper Business', 'publication_year': 2024, 'genre': 'Business', 'pages': 272, 'description': 'A refreshing take on leadership that celebrates introverted strengths. Harvard profiles successful leaders who lead with listening, thoughtfulness, and quiet determination, offering a new model for the modern workplace.', 'cover_image_url': '/assets/book_covers/cover_19.jpg', 'location_code': 'BUS-O03', 'total_copies': 3, 'available_copies': 3},
        {'isbn': '978059318', 'title': 'Salt Water and Stories', 'author': 'Amelia Chen', 'publisher': 'Penguin Press', 'publication_year': 2023, 'genre': 'Memoir', 'pages': 304, 'description': 'A poignant memoir of growing up in a fishing village on the coast of Maine. Chen weaves together family history, maritime tradition, and personal reflection into a lyrical narrative about home and belonging.', 'cover_image_url': '/assets/book_covers/cover_20.jpg', 'location_code': 'MEM-P05', 'total_copies': 2, 'available_copies': 0},
        {'isbn': '978014044', 'title': 'Pride and Prejudice', 'author': 'Jane Austen', 'publisher': 'Penguin Classics', 'publication_year': 1813, 'genre': 'Fiction', 'pages': 432, 'description': 'The classic romantic novel following Elizabeth Bennet as she navigates issues of manners, upbringing, morality, education, and marriage in the society of the landed gentry of early 19th-century England.', 'cover_image_url': '/assets/book_covers/cover_01.jpg', 'location_code': 'FIC-A01', 'total_copies': 5, 'available_copies': 3},
        {'isbn': '978045152', 'title': '1984', 'author': 'George Orwell', 'publisher': 'Signet Classic', 'publication_year': 1949, 'genre': 'Fiction', 'pages': 328, 'description': 'A dystopian social science fiction novel and cautionary tale about the dangers of totalitarianism, mass surveillance, and repressive regimentation of persons and behaviours within society.', 'cover_image_url': '/assets/book_covers/cover_08.jpg', 'location_code': 'FIC-A02', 'total_copies': 4, 'available_copies': 2},
        {'isbn': '978074327', 'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 'publisher': 'Scribner', 'publication_year': 1925, 'genre': 'Fiction', 'pages': 180, 'description': 'A novel set in the Jazz Age that tells the story of the mysteriously wealthy Jay Gatsby and his love for the beautiful Daisy Buchanan, of lavish parties on Long Island.', 'cover_image_url': '/assets/book_covers/cover_09.jpg', 'location_code': 'FIC-A03', 'total_copies': 4, 'available_copies': 1},
        {'isbn': '978006112', 'title': 'To Kill a Mockingbird', 'author': 'Harper Lee', 'publisher': 'Harper Perennial', 'publication_year': 1960, 'genre': 'Fiction', 'pages': 281, 'description': 'A novel about the serious issues of rape and racial inequality, told through the eyes of young Scout Finch in Depression-era Alabama.', 'cover_image_url': '/assets/book_covers/cover_12.jpg', 'location_code': 'FIC-A04', 'total_copies': 4, 'available_copies': 2},
        {'isbn': '978014243', 'title': 'Moby Dick', 'author': 'Herman Melville', 'publisher': 'Penguin Classics', 'publication_year': 1851, 'genre': 'Fiction', 'pages': 635, 'description': 'The narrative of the sailor Ishmael and the obsessive quest of Captain Ahab for revenge on Moby Dick, the giant white sperm whale that on the ship\'s previous voyage bit off Ahab\'s leg at the knee.', 'cover_image_url': '/assets/book_covers/cover_20.jpg', 'location_code': 'FIC-A05', 'total_copies': 3, 'available_copies': 2},
        {'isbn': '978030747', 'title': 'The Catcher in the Rye', 'author': 'J.D. Salinger', 'publisher': 'Little, Brown', 'publication_year': 1951, 'genre': 'Fiction', 'pages': 234, 'description': 'A controversial novel about teenage angst and alienation, narrated by Holden Caulfield, a seventeen-year-old boy who has just been expelled from prep school.', 'cover_image_url': '/assets/book_covers/cover_05.jpg', 'location_code': 'FIC-A06', 'total_copies': 3, 'available_copies': 1},
        {'isbn': '9780140449', 'title': 'War and Peace', 'author': 'Leo Tolstoy', 'publisher': 'Penguin Classics', 'publication_year': 1869, 'genre': 'Fiction', 'pages': 1225, 'description': 'A literary work that mixes fictional narrative with chapters on history and philosophy. It follows the histories of five aristocratic families during the French invasion of Russia.', 'cover_image_url': '/assets/book_covers/cover_03.jpg', 'location_code': 'FIC-A07', 'total_copies': 2, 'available_copies': 1},
        {'isbn': '978054792', 'title': 'The Hobbit', 'author': 'J.R.R. Tolkien', 'publisher': 'Houghton Mifflin', 'publication_year': 1937, 'genre': 'Fantasy', 'pages': 310, 'description': 'A children\'s fantasy novel that follows the quest of home-loving Bilbo Baggins to win a share of the treasure guarded by the dragon Smaug.', 'cover_image_url': '/assets/book_covers/cover_11.jpg', 'location_code': 'FAN-A01', 'total_copies': 5, 'available_copies': 3},
        {'isbn': '978055359', 'title': 'A Brief History of Time', 'author': 'Stephen Hawking', 'publisher': 'Bantam', 'publication_year': 1988, 'genre': 'Science', 'pages': 212, 'description': 'A popular-science book on cosmology that explores profound questions about the universe, black holes, the Big Bang, and the nature of time itself.', 'cover_image_url': '/assets/book_covers/cover_02.jpg', 'location_code': 'SCI-B01', 'total_copies': 3, 'available_copies': 2},
        {'isbn': '978067976', 'title': 'Sapiens', 'author': 'Yuval Noah Harari', 'publisher': 'Harper Perennial', 'publication_year': 2015, 'genre': 'History', 'pages': 464, 'description': 'A bold, sweeping narrative of humanity\'s creation and evolution that explores the ways in which biology and history have defined us and enhanced our understanding of what it means to be human.', 'cover_image_url': '/assets/book_covers/cover_03.jpg', 'location_code': 'HIS-C01', 'total_copies': 4, 'available_copies': 2},
        {'isbn': '978014311', 'title': 'Thinking, Fast and Slow', 'author': 'Daniel Kahneman', 'publisher': 'Farrar, Straus and Giroux', 'publication_year': 2011, 'genre': 'Psychology', 'pages': 499, 'description': 'A groundbreaking tour of the mind that explains the two systems that drive the way we think. System 1 is fast, intuitive, and emotional; System 2 is slower, more deliberative, and more logical.', 'cover_image_url': '/assets/book_covers/cover_12.jpg', 'location_code': 'PSY-Q02', 'total_copies': 3, 'available_copies': 1},
        {'isbn': '978145164', 'title': 'Steve Jobs', 'author': 'Walter Isaacson', 'publisher': 'Simon & Schuster', 'publication_year': 2011, 'genre': 'Biography', 'pages': 656, 'description': 'The exclusive biography of Steve Jobs, based on more than forty interviews with Jobs conducted over two years, as well as interviews with family members, friends, competitors, and colleagues.', 'cover_image_url': '/assets/book_covers/cover_10.jpg', 'location_code': 'BIO-H01', 'total_copies': 3, 'available_copies': 1},
        {'isbn': '978031601', 'title': 'The Alchemist', 'author': 'Paulo Coelho', 'publisher': 'HarperOne', 'publication_year': 1988, 'genre': 'Fiction', 'pages': 197, 'description': 'A philosophical book about a shepherd boy named Santiago who travels from his homeland in Spain to the Egyptian desert in search of treasure buried in the Pyramids.', 'cover_image_url': '/assets/book_covers/cover_14.jpg', 'location_code': 'FIC-A09', 'total_copies': 4, 'available_copies': 2},
        {'isbn': '978006231', 'title': 'Becoming', 'author': 'Michelle Obama', 'publisher': 'Crown', 'publication_year': 2018, 'genre': 'Memoir', 'pages': 448, 'description': 'The memoir of former First Lady Michelle Obama, chronicling the experiences that have shaped her, from her childhood on the South Side of Chicago to her years as an executive and her time at the White House.', 'cover_image_url': '/assets/book_covers/cover_16.jpg', 'location_code': 'MEM-P01', 'total_copies': 3, 'available_copies': 1},
    ]

    books = []
    for b in books_data:
        book = Book(**b)
        books.append(book)
    
    db.session.add_all(books)
    db.session.commit()

    # Create loans - mix of active, overdue, and recent returns
    today = datetime.now().date()
    
    # Active loans (various due dates)
    active_loans = [
        {'book_id': 1, 'patron_id': 1, 'loan_date': today - timedelta(days=5), 'due_date': today + timedelta(days=9), 'status': 'active', 'checked_out_by': 2},
        {'book_id': 4, 'patron_id': 2, 'loan_date': today - timedelta(days=2), 'due_date': today + timedelta(days=12), 'status': 'active', 'checked_out_by': 2},
        {'book_id': 6, 'patron_id': 3, 'loan_date': today - timedelta(days=10), 'due_date': today + timedelta(days=4), 'status': 'active', 'checked_out_by': 2},
        {'book_id': 8, 'patron_id': 4, 'loan_date': today - timedelta(days=1), 'due_date': today + timedelta(days=13), 'status': 'active', 'checked_out_by': 2},
        {'book_id': 13, 'patron_id': 5, 'loan_date': today - timedelta(days=7), 'due_date': today + timedelta(days=7), 'status': 'active', 'checked_out_by': 2},
        {'book_id': 14, 'patron_id': 6, 'loan_date': today - timedelta(days=3), 'due_date': today + timedelta(days=11), 'status': 'active', 'checked_out_by': 2},
        {'book_id': 16, 'patron_id': 7, 'loan_date': today - timedelta(days=12), 'due_date': today + timedelta(days=2), 'status': 'active', 'checked_out_by': 2},
        {'book_id': 21, 'patron_id': 9, 'loan_date': today - timedelta(days=4), 'due_date': today + timedelta(days=10), 'status': 'active', 'checked_out_by': 2},
        {'book_id': 23, 'patron_id': 10, 'loan_date': today - timedelta(days=8), 'due_date': today + timedelta(days=6), 'status': 'active', 'checked_out_by': 2},
        {'book_id': 26, 'patron_id': 11, 'loan_date': today - timedelta(days=6), 'due_date': today + timedelta(days=8), 'status': 'active', 'checked_out_by': 2},
        {'book_id': 27, 'patron_id': 12, 'loan_date': today - timedelta(days=9), 'due_date': today + timedelta(days=5), 'status': 'active', 'checked_out_by': 2},
        {'book_id': 30, 'patron_id': 13, 'loan_date': today - timedelta(days=11), 'due_date': today + timedelta(days=3), 'status': 'active', 'checked_out_by': 2},
        {'book_id': 31, 'patron_id': 15, 'loan_date': today - timedelta(days=3), 'due_date': today + timedelta(days=11), 'status': 'active', 'checked_out_by': 2},
        {'book_id': 32, 'patron_id': 17, 'loan_date': today - timedelta(days=5), 'due_date': today + timedelta(days=9), 'status': 'active', 'checked_out_by': 2},
        {'book_id': 10, 'patron_id': 20, 'loan_date': today - timedelta(days=1), 'due_date': today + timedelta(days=13), 'status': 'active', 'checked_out_by': 2},
        {'book_id': 33, 'patron_id': 1, 'loan_date': today - timedelta(days=15), 'due_date': today - timedelta(days=1), 'status': 'active', 'checked_out_by': 2},
    ]

    # Overdue loans
    overdue_loans = [
        {'book_id': 20, 'patron_id': 8, 'loan_date': today - timedelta(days=25), 'due_date': today - timedelta(days=11), 'status': 'overdue', 'fine_amount': 5.50, 'checked_out_by': 2},
        {'book_id': 25, 'patron_id': 14, 'loan_date': today - timedelta(days=30), 'due_date': today - timedelta(days=16), 'status': 'overdue', 'fine_amount': 8.00, 'checked_out_by': 2},
        {'book_id': 28, 'patron_id': 16, 'loan_date': today - timedelta(days=20), 'due_date': today - timedelta(days=6), 'status': 'overdue', 'fine_amount': 3.00, 'checked_out_by': 2},
        {'book_id': 29, 'patron_id': 18, 'loan_date': today - timedelta(days=22), 'due_date': today - timedelta(days=8), 'status': 'overdue', 'fine_amount': 4.00, 'checked_out_by': 2},
        {'book_id': 22, 'patron_id': 19, 'loan_date': today - timedelta(days=18), 'due_date': today - timedelta(days=4), 'status': 'overdue', 'fine_amount': 2.00, 'checked_out_by': 2},
    ]

    # Returned loans
    returned_loans = [
        {'book_id': 1, 'patron_id': 3, 'loan_date': today - timedelta(days=30), 'due_date': today - timedelta(days=16), 'return_date': today - timedelta(days=14), 'status': 'returned', 'checked_out_by': 2, 'checked_in_by': 2},
        {'book_id': 7, 'patron_id': 5, 'loan_date': today - timedelta(days=20), 'due_date': today - timedelta(days=6), 'return_date': today - timedelta(days=7), 'status': 'returned', 'checked_out_by': 2, 'checked_in_by': 2},
        {'book_id': 11, 'patron_id': 7, 'loan_date': today - timedelta(days=35), 'due_date': today - timedelta(days=21), 'return_date': today - timedelta(days=18), 'status': 'returned', 'checked_out_by': 2, 'checked_in_by': 2},
        {'book_id': 15, 'patron_id': 9, 'loan_date': today - timedelta(days=25), 'due_date': today - timedelta(days=11), 'return_date': today - timedelta(days=10), 'status': 'returned', 'checked_out_by': 2, 'checked_in_by': 2},
        {'book_id': 19, 'patron_id': 11, 'loan_date': today - timedelta(days=40), 'due_date': today - timedelta(days=26), 'return_date': today - timedelta(days=20), 'status': 'returned', 'checked_out_by': 2, 'checked_in_by': 2},
        {'book_id': 24, 'patron_id': 13, 'loan_date': today - timedelta(days=28), 'due_date': today - timedelta(days=14), 'return_date': today - timedelta(days=12), 'status': 'returned', 'checked_out_by': 2, 'checked_in_by': 2},
        {'book_id': 12, 'patron_id': 15, 'loan_date': today - timedelta(days=22), 'due_date': today - timedelta(days=8), 'return_date': today - timedelta(days=9), 'status': 'returned', 'fine_amount': 0.50, 'checked_out_by': 2, 'checked_in_by': 2},
        {'book_id': 17, 'patron_id': 17, 'loan_date': today - timedelta(days=32), 'due_date': today - timedelta(days=18), 'return_date': today - timedelta(days=15), 'status': 'returned', 'checked_out_by': 2, 'checked_in_by': 2},
        {'book_id': 2, 'patron_id': 2, 'loan_date': today - timedelta(days=15), 'due_date': today - timedelta(days=1), 'return_date': today - timedelta(days=3), 'status': 'returned', 'fine_amount': 1.00, 'checked_out_by': 2, 'checked_in_by': 2},
        {'book_id': 9, 'patron_id': 4, 'loan_date': today - timedelta(days=18), 'due_date': today - timedelta(days=4), 'return_date': today - timedelta(days=5), 'status': 'returned', 'fine_amount': 0.50, 'checked_out_by': 2, 'checked_in_by': 2},
    ]

    all_loans = active_loans + overdue_loans + returned_loans
    loans = []
    for l in all_loans:
        loan = Loan(**l)
        loans.append(loan)
    
    db.session.add_all(loans)
    db.session.commit()

    # Update patron fine balances
    for patron in Patron.query.all():
        total_fines = db.session.query(func.sum(Loan.fine_amount)).filter(
            Loan.patron_id == patron.id,
            Loan.fine_paid == False,
            Loan.status.in_(['overdue', 'returned'])
        ).scalar() or 0
        patron.fine_balance = total_fines
    
    db.session.commit()

    # Create reservations
    reservations_data = [
        {'book_id': 10, 'patron_id': 3, 'reservation_date': today - timedelta(days=2), 'status': 'ready', 'expiry_date': today + timedelta(days=1)},
        {'book_id': 20, 'patron_id': 5, 'reservation_date': today - timedelta(days=5), 'status': 'pending'},
        {'book_id': 10, 'patron_id': 7, 'reservation_date': today - timedelta(days=1), 'status': 'pending'},
        {'book_id': 25, 'patron_id': 9, 'reservation_date': today - timedelta(days=3), 'status': 'pending'},
        {'book_id': 33, 'patron_id': 11, 'reservation_date': today - timedelta(days=1), 'status': 'pending'},
        {'book_id': 22, 'patron_id': 13, 'reservation_date': today - timedelta(days=4), 'status': 'pending'},
        {'book_id': 28, 'patron_id': 15, 'reservation_date': today - timedelta(days=2), 'status': 'pending'},
        {'book_id': 29, 'patron_id': 17, 'reservation_date': today - timedelta(days=1), 'status': 'pending'},
    ]

    for r in reservations_data:
        reservation = Reservation(**r)
        db.session.add(reservation)
    
    db.session.commit()

    # Create activity log entries
    activities = [
        {'user_id': 2, 'action': 'checkout', 'entity_type': 'loan', 'entity_id': 1, 'details': 'Checked out "The Last Garden" to Emma Thompson'},
        {'user_id': 2, 'action': 'checkout', 'entity_type': 'loan', 'entity_id': 2, 'details': 'Checked out "The Silent Key" to Oliver Martinez'},
        {'user_id': 2, 'action': 'checkin', 'entity_type': 'loan', 'entity_id': 17, 'details': 'Checked in "Impressionist Light" from Sophia Anderson'},
        {'user_id': 2, 'action': 'checkin', 'entity_type': 'loan', 'entity_id': 18, 'details': 'Checked in "Feasts of the Mediterranean" from Ava Williams'},
        {'user_id': 2, 'action': 'renew', 'entity_type': 'loan', 'entity_id': 3, 'details': 'Renewed loan for "Throne of Ash"'},
        {'user_id': 2, 'action': 'create_patron', 'entity_type': 'patron', 'entity_id': 20, 'details': 'Added new patron: Henry Lee'},
        {'user_id': 2, 'action': 'update_book', 'entity_type': 'book', 'entity_id': 5, 'details': 'Updated book: "Milo\'s Moon Adventure" - added 2 copies'},
        {'user_id': 2, 'action': 'checkout', 'entity_type': 'loan', 'entity_id': 26, 'details': 'Checked out "1984" to Mia Wilson'},
    ]

    for a in activities:
        activity = ActivityLog(**a)
        db.session.add(activity)
    
    db.session.commit()
    print("Seed data created successfully!")


# =============================================================================
# AUTHENTICATION ROUTES
# =============================================================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 403
    
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    access_token = create_access_token(identity=str(user.id))
    return jsonify({'token': access_token, 'user': user.to_dict()}), 200


@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': user.to_dict()}), 200


# =============================================================================
# DASHBOARD ROUTES
# =============================================================================

@app.route('/api/dashboard/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    total_books = Book.query.count()
    total_copies = db.session.query(func.sum(Book.total_copies)).scalar() or 0
    active_loans = Loan.query.filter(Loan.status.in_(['active'])).count()
    overdue_items = Loan.query.filter_by(status='overdue').count()
    new_patrons = Patron.query.filter(Patron.join_date >= date.today() - timedelta(days=30)).count()
    
    return jsonify({
        'totalBooks': total_books,
        'totalCopies': int(total_copies),
        'activeLoans': active_loans,
        'overdueItems': overdue_items,
        'newPatrons': new_patrons
    }), 200


@app.route('/api/dashboard/activity', methods=['GET'])
@jwt_required()
def get_recent_activity():
    recent_loans = Loan.query.order_by(Loan.created_at.desc()).limit(10).all()
    return jsonify({
        'recentLoans': [loan.to_dict() for loan in recent_loans]
    }), 200


@app.route('/api/dashboard/charts/loans', methods=['GET'])
@jwt_required()
def get_loan_chart_data():
    months = int(request.args.get('months', 12))
    labels = []
    data = []
    
    for i in range(months - 1, -1, -1):
        month_date = datetime.now() - timedelta(days=i * 30)
        labels.append(month_date.strftime('%b %Y'))
        
        month_start = date(month_date.year, month_date.month, 1)
        if month_date.month == 12:
            month_end = date(month_date.year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(month_date.year, month_date.month + 1, 1) - timedelta(days=1)
        
        count = Loan.query.filter(
            Loan.loan_date >= month_start,
            Loan.loan_date <= month_end
        ).count()
        data.append(count)
    
    return jsonify({'labels': labels, 'data': data}), 200


@app.route('/api/dashboard/charts/categories', methods=['GET'])
@jwt_required()
def get_category_chart_data():
    results = db.session.query(Book.genre, func.count(Book.id)).group_by(Book.genre).all()
    
    labels = []
    data = []
    colors = ['#8B2942', '#B85C38', '#4A6741', '#D4A843', '#6B4C7A', '#3A7D8C', '#8B6914', '#2D5A3D']
    
    for genre, count in results:
        labels.append(genre)
        data.append(count)
    
    return jsonify({
        'labels': labels,
        'data': data,
        'colors': colors[:len(labels)]
    }), 200


# =============================================================================
# BOOK ROUTES
# =============================================================================

@app.route('/api/books', methods=['GET'])
@jwt_required()
def get_books():
    q = request.args.get('q', '')
    genre = request.args.get('genre', '')
    availability = request.args.get('availability', '')
    sort = request.args.get('sort', 'title')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    
    query = Book.query
    
    if q:
        query = query.filter(
            or_(
                Book.title.ilike(f'%{q}%'),
                Book.author.ilike(f'%{q}%'),
                Book.isbn.ilike(f'%{q}%')
            )
        )
    
    if genre:
        query = query.filter(Book.genre == genre)
    
    if availability == 'available':
        query = query.filter(Book.available_copies > 0)
    elif availability == 'checked_out':
        query = query.filter(Book.available_copies == 0)
    
    # Sorting
    if sort == 'title':
        query = query.order_by(Book.title)
    elif sort == 'author':
        query = query.order_by(Book.author)
    elif sort == 'year':
        query = query.order_by(Book.publication_year.desc())
    elif sort == 'newest':
        query = query.order_by(Book.created_at.desc())
    
    total = query.count()
    books = query.offset((page - 1) * limit).limit(limit).all()
    
    return jsonify({
        'books': [book.to_dict() for book in books],
        'total': total,
        'page': page,
        'totalPages': (total + limit - 1) // limit
    }), 200


@app.route('/api/books/<int:book_id>', methods=['GET'])
@jwt_required()
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify({'book': book.to_dict()}), 200


@app.route('/api/books', methods=['POST'])
@jwt_required()
def create_book():
    data = request.get_json()
    
    book = Book(
        isbn=data.get('isbn'),
        title=data.get('title'),
        author=data.get('author'),
        publisher=data.get('publisher'),
        publication_year=data.get('publication_year'),
        genre=data.get('genre'),
        pages=data.get('pages'),
        description=data.get('description'),
        cover_image_url=data.get('cover_image_url', '/assets/book_covers/cover_01.jpg'),
        location_code=data.get('location_code'),
        total_copies=data.get('total_copies', 1),
        available_copies=data.get('total_copies', 1)
    )
    
    db.session.add(book)
    db.session.commit()
    
    # Log activity
    user_id = int(get_jwt_identity())
    activity = ActivityLog(
        user_id=user_id,
        action='create_book',
        entity_type='book',
        entity_id=book.id,
        details=f'Added new book: "{book.title}"'
    )
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({'book': book.to_dict()}), 201


@app.route('/api/books/<int:book_id>', methods=['PUT'])
@jwt_required()
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    
    book.isbn = data.get('isbn', book.isbn)
    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)
    book.publisher = data.get('publisher', book.publisher)
    book.publication_year = data.get('publication_year', book.publication_year)
    book.genre = data.get('genre', book.genre)
    book.pages = data.get('pages', book.pages)
    book.description = data.get('description', book.description)
    book.cover_image_url = data.get('cover_image_url', book.cover_image_url)
    book.location_code = data.get('location_code', book.location_code)
    book.total_copies = data.get('total_copies', book.total_copies)
    book.available_copies = data.get('available_copies', book.available_copies)
    book.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify({'book': book.to_dict()}), 200


@app.route('/api/books/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({'success': True}), 200


@app.route('/api/books/genres', methods=['GET'])
@jwt_required()
def get_genres():
    genres = db.session.query(Book.genre).distinct().all()
    return jsonify({'genres': [g[0] for g in genres if g[0]]}), 200


# =============================================================================
# PATRON ROUTES
# =============================================================================

@app.route('/api/patrons', methods=['GET'])
@jwt_required()
def get_patrons():
    q = request.args.get('q', '')
    status = request.args.get('status', '')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    
    query = Patron.query
    
    if q:
        query = query.filter(
            or_(
                Patron.first_name.ilike(f'%{q}%'),
                Patron.last_name.ilike(f'%{q}%'),
                Patron.card_id.ilike(f'%{q}%'),
                Patron.email.ilike(f'%{q}%')
            )
        )
    
    if status:
        query = query.filter(Patron.status == status)
    
    total = query.count()
    patrons = query.order_by(Patron.last_name, Patron.first_name).offset((page - 1) * limit).limit(limit).all()
    
    return jsonify({
        'patrons': [patron.to_dict() for patron in patrons],
        'total': total,
        'page': page,
        'totalPages': (total + limit - 1) // limit
    }), 200


@app.route('/api/patrons/<int:patron_id>', methods=['GET'])
@jwt_required()
def get_patron(patron_id):
    patron = Patron.query.get_or_404(patron_id)
    return jsonify({'patron': patron.to_dict()}), 200


@app.route('/api/patrons', methods=['POST'])
@jwt_required()
def create_patron():
    data = request.get_json()
    
    patron = Patron(
        card_id=data.get('card_id'),
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        email=data.get('email'),
        phone=data.get('phone'),
        address=data.get('address'),
        status=data.get('status', 'active'),
        membership_type=data.get('membership_type', 'standard'),
        max_loans=data.get('max_loans', 5),
        loan_period_days=data.get('loan_period_days', 14),
        join_date=date.today(),
        expiry_date=date.today() + timedelta(days=365)
    )
    
    db.session.add(patron)
    db.session.commit()
    
    # Log activity
    user_id = int(get_jwt_identity())
    activity = ActivityLog(
        user_id=user_id,
        action='create_patron',
        entity_type='patron',
        entity_id=patron.id,
        details=f'Added new patron: {patron.full_name}'
    )
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({'patron': patron.to_dict()}), 201


@app.route('/api/patrons/<int:patron_id>', methods=['PUT'])
@jwt_required()
def update_patron(patron_id):
    patron = Patron.query.get_or_404(patron_id)
    data = request.get_json()
    
    patron.first_name = data.get('first_name', patron.first_name)
    patron.last_name = data.get('last_name', patron.last_name)
    patron.email = data.get('email', patron.email)
    patron.phone = data.get('phone', patron.phone)
    patron.address = data.get('address', patron.address)
    patron.status = data.get('status', patron.status)
    patron.membership_type = data.get('membership_type', patron.membership_type)
    patron.max_loans = data.get('max_loans', patron.max_loans)
    
    db.session.commit()
    return jsonify({'patron': patron.to_dict()}), 200


@app.route('/api/patrons/<int:patron_id>', methods=['DELETE'])
@jwt_required()
def delete_patron(patron_id):
    patron = Patron.query.get_or_404(patron_id)
    db.session.delete(patron)
    db.session.commit()
    return jsonify({'success': True}), 200


@app.route('/api/patrons/<int:patron_id>/loans', methods=['GET'])
@jwt_required()
def get_patron_loans(patron_id):
    patron = Patron.query.get_or_404(patron_id)
    status = request.args.get('status', '')
    
    query = Loan.query.filter_by(patron_id=patron_id)
    if status:
        query = query.filter_by(status=status)
    
    loans = query.order_by(Loan.loan_date.desc()).all()
    return jsonify({'loans': [loan.to_dict() for loan in loans]}), 200


@app.route('/api/patrons/<int:patron_id>/fines', methods=['GET'])
@jwt_required()
def get_patron_fines(patron_id):
    patron = Patron.query.get_or_404(patron_id)
    fines = Loan.query.filter(
        Loan.patron_id == patron_id,
        Loan.fine_amount > 0,
        Loan.fine_paid == False
    ).all()
    
    total = sum(float(loan.fine_amount) for loan in fines)
    return jsonify({
        'fines': [loan.to_dict() for loan in fines],
        'total': total
    }), 200


# =============================================================================
# LOAN ROUTES
# =============================================================================

@app.route('/api/loans', methods=['GET'])
@jwt_required()
def get_loans():
    status = request.args.get('status', '')
    patron_id = request.args.get('patron_id', '')
    book_id = request.args.get('book_id', '')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    
    query = Loan.query
    
    if status:
        query = query.filter(Loan.status == status)
    
    if patron_id:
        query = query.filter(Loan.patron_id == int(patron_id))
    
    if book_id:
        query = query.filter(Loan.book_id == int(book_id))
    
    total = query.count()
    loans = query.order_by(Loan.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    return jsonify({
        'loans': [loan.to_dict() for loan in loans],
        'total': total,
        'page': page,
        'totalPages': (total + limit - 1) // limit
    }), 200


@app.route('/api/loans/<int:loan_id>', methods=['GET'])
@jwt_required()
def get_loan(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    return jsonify({'loan': loan.to_dict()}), 200


@app.route('/api/loans/checkout', methods=['POST'])
@jwt_required()
def checkout_books():
    data = request.get_json()
    patron_id = data.get('patron_id')
    book_ids = data.get('book_ids', [])
    
    if not patron_id or not book_ids:
        return jsonify({'error': 'Patron ID and book IDs are required'}), 400
    
    patron = Patron.query.get_or_404(patron_id)
    user_id = int(get_jwt_identity())
    
    # Check patron status
    if patron.status != 'active':
        return jsonify({'error': f'Patron account is {patron.status}'}), 400
    
    # Check fine balance
    if float(patron.fine_balance) >= 10.00:
        return jsonify({'error': f'Patron has outstanding fines of ${float(patron.fine_balance):.2f}. Maximum allowed is $10.00'}), 400
    
    # Check max loans
    current_loans = Loan.query.filter(
        Loan.patron_id == patron_id,
        Loan.status.in_(['active', 'overdue'])
    ).count()
    
    if current_loans + len(book_ids) > patron.max_loans:
        return jsonify({'error': f'Patron can only borrow {patron.max_loans - current_loans} more books'}), 400
    
    success_count = 0
    failed_books = []
    created_loans = []
    
    for book_id in book_ids:
        book = Book.query.get(book_id)
        if not book:
            failed_books.append({'id': book_id, 'reason': 'Book not found'})
            continue
        
        if book.available_copies <= 0:
            failed_books.append({'id': book_id, 'title': book.title, 'reason': 'No copies available'})
            continue
        
        # Check if book is reserved by someone else
        existing_reservation = Reservation.query.filter(
            Reservation.book_id == book_id,
            Reservation.status == 'pending',
            Reservation.patron_id != patron_id
        ).first()
        
        if existing_reservation:
            failed_books.append({'id': book_id, 'title': book.title, 'reason': 'Book has pending reservations'})
            continue
        
        # Create loan
        loan_date = date.today()
        due_date = loan_date + timedelta(days=patron.loan_period_days)
        
        loan = Loan(
            book_id=book_id,
            patron_id=patron_id,
            loan_date=loan_date,
            due_date=due_date,
            status='active',
            checked_out_by=user_id
        )
        
        book.available_copies -= 1
        db.session.add(loan)
        db.session.commit()
        
        created_loans.append(loan.to_dict())
        success_count += 1
    
    return jsonify({
        'loans': created_loans,
        'successCount': success_count,
        'failCount': len(failed_books),
        'failedBooks': failed_books
    }), 200


@app.route('/api/loans/checkin', methods=['POST'])
@jwt_required()
def checkin_book():
    data = request.get_json()
    loan_id = data.get('loan_id')
    book_id = data.get('book_id')
    user_id = int(get_jwt_identity())
    
    if loan_id:
        loan = Loan.query.get_or_404(loan_id)
    elif book_id:
        loan = Loan.query.filter(
            Loan.book_id == book_id,
            Loan.status.in_(['active', 'overdue'])
        ).first()
        if not loan:
            return jsonify({'error': 'No active loan found for this book'}), 404
    else:
        return jsonify({'error': 'Loan ID or Book ID is required'}), 400
    
    # Update loan
    loan.return_date = date.today()
    loan.checked_in_by = user_id
    
    # Calculate fine if overdue
    if loan.due_date and loan.return_date > loan.due_date:
        days_overdue = (loan.return_date - loan.due_date).days
        loan.fine_amount = days_overdue * 0.50
        loan.status = 'returned'
    else:
        loan.status = 'returned'
    
    # Update book availability
    book = Book.query.get(loan.book_id)
    if book:
        book.available_copies += 1
    
    # Update patron fine balance
    patron = Patron.query.get(loan.patron_id)
    if patron and float(loan.fine_amount) > 0:
        patron.fine_balance = float(patron.fine_balance) + float(loan.fine_amount)
    
    db.session.commit()
    
    return jsonify({'loan': loan.to_dict()}), 200


@app.route('/api/loans/<int:loan_id>/renew', methods=['POST'])
@jwt_required()
def renew_loan(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    
    if loan.status != 'active':
        return jsonify({'error': 'Only active loans can be renewed'}), 400
    
    if loan.renewal_count >= 2:
        return jsonify({'error': 'Maximum renewals (2) reached'}), 400
    
    # Check if book has pending reservations from other patrons
    pending_reservation = Reservation.query.filter(
        Reservation.book_id == loan.book_id,
        Reservation.status == 'pending',
        Reservation.patron_id != loan.patron_id
    ).first()
    
    if pending_reservation:
        return jsonify({'error': 'Book has pending reservations from other patrons'}), 400
    
    patron = Patron.query.get(loan.patron_id)
    if patron and float(patron.fine_balance) > 0:
        return jsonify({'error': 'Patron has outstanding fines'}), 400
    
    # Renew
    loan.due_date = loan.due_date + timedelta(days=patron.loan_period_days)
    loan.renewal_count += 1
    db.session.commit()
    
    return jsonify({'loan': loan.to_dict()}), 200


@app.route('/api/loans/overdue', methods=['GET'])
@jwt_required()
def get_overdue_loans():
    # First update any active loans that are now overdue
    today = date.today()
    overdue_active = Loan.query.filter(
        Loan.status == 'active',
        Loan.due_date < today
    ).all()
    
    for loan in overdue_active:
        loan.status = 'overdue'
        days = (today - loan.due_date).days
        loan.fine_amount = days * 0.50
    
    db.session.commit()
    
    loans = Loan.query.filter_by(status='overdue').order_by(Loan.due_date).all()
    return jsonify({
        'loans': [loan.to_dict() for loan in loans],
        'total': len(loans)
    }), 200


@app.route('/api/loans/pay-fine/<int:loan_id>', methods=['POST'])
@jwt_required()
def pay_fine(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    
    if loan.fine_paid or float(loan.fine_amount) <= 0:
        return jsonify({'error': 'No outstanding fine for this loan'}), 400
    
    loan.fine_paid = True
    patron = Patron.query.get(loan.patron_id)
    if patron:
        patron.fine_balance = max(0, float(patron.fine_balance) - float(loan.fine_amount))
    
    db.session.commit()
    return jsonify({'loan': loan.to_dict(), 'message': 'Fine paid successfully'}), 200


# =============================================================================
# RESERVATION ROUTES
# =============================================================================

@app.route('/api/reservations', methods=['GET'])
@jwt_required()
def get_reservations():
    status = request.args.get('status', '')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    
    query = Reservation.query
    if status:
        query = query.filter(Reservation.status == status)
    
    total = query.count()
    reservations = query.order_by(Reservation.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    return jsonify({
        'reservations': [r.to_dict() for r in reservations],
        'total': total,
        'page': page,
        'totalPages': (total + limit - 1) // limit
    }), 200


@app.route('/api/reservations', methods=['POST'])
@jwt_required()
def create_reservation():
    data = request.get_json()
    patron_id = data.get('patron_id')
    book_id = data.get('book_id')
    
    if not patron_id or not book_id:
        return jsonify({'error': 'Patron ID and Book ID are required'}), 400
    
    patron = Patron.query.get_or_404(patron_id)
    book = Book.query.get_or_404(book_id)
    
    if book.available_copies > 0:
        return jsonify({'error': 'Book is available for checkout, no need to reserve'}), 400
    
    # Check if patron already has a pending reservation for this book
    existing = Reservation.query.filter(
        Reservation.book_id == book_id,
        Reservation.patron_id == patron_id,
        Reservation.status == 'pending'
    ).first()
    
    if existing:
        return jsonify({'error': 'Patron already has a pending reservation for this book'}), 400
    
    reservation = Reservation(
        book_id=book_id,
        patron_id=patron_id,
        reservation_date=date.today(),
        status='pending'
    )
    
    db.session.add(reservation)
    db.session.commit()
    
    return jsonify({'reservation': reservation.to_dict()}), 201


@app.route('/api/reservations/<int:reservation_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    reservation.status = 'cancelled'
    db.session.commit()
    return jsonify({'reservation': reservation.to_dict()}), 200


# =============================================================================
# REPORT ROUTES
# =============================================================================

@app.route('/api/reports/loans', methods=['GET'])
@jwt_required()
def get_loan_report():
    from_date = request.args.get('from')
    to_date = request.args.get('to')
    
    query = Loan.query
    if from_date:
        query = query.filter(Loan.loan_date >= datetime.strptime(from_date, '%Y-%m-%d').date())
    if to_date:
        query = query.filter(Loan.loan_date <= datetime.strptime(to_date, '%Y-%m-%d').date())
    
    loans = query.order_by(Loan.loan_date.desc()).all()
    
    total_loans = len(loans)
    active_loans = len([l for l in loans if l.status == 'active'])
    returned_loans = len([l for l in loans if l.status == 'returned'])
    overdue_loans = len([l for l in loans if l.status == 'overdue'])
    total_fines = sum(float(l.fine_amount) for l in loans)
    
    return jsonify({
        'summary': {
            'totalLoans': total_loans,
            'activeLoans': active_loans,
            'returnedLoans': returned_loans,
            'overdueLoans': overdue_loans,
            'totalFines': total_fines
        },
        'loans': [loan.to_dict() for loan in loans]
    }), 200


@app.route('/api/reports/overdue', methods=['GET'])
@jwt_required()
def get_overdue_report():
    loans = Loan.query.filter_by(status='overdue').order_by(Loan.due_date).all()
    
    total_fines = sum(float(l.fine_amount) for l in loans)
    
    return jsonify({
        'totalOverdue': len(loans),
        'totalFines': total_fines,
        'loans': [loan.to_dict() for loan in loans]
    }), 200


@app.route('/api/reports/popular', methods=['GET'])
@jwt_required()
def get_popular_books():
    from_date = request.args.get('from')
    to_date = request.args.get('to')
    
    query = db.session.query(
        Book.id,
        Book.title,
        Book.author,
        Book.genre,
        Book.cover_image_url,
        func.count(Loan.id).label('loan_count')
    ).join(Loan, Book.id == Loan.book_id)
    
    if from_date:
        query = query.filter(Loan.loan_date >= datetime.strptime(from_date, '%Y-%m-%d').date())
    if to_date:
        query = query.filter(Loan.loan_date <= datetime.strptime(to_date, '%Y-%m-%d').date())
    
    results = query.group_by(Book.id).order_by(func.count(Loan.id).desc()).limit(20).all()
    
    books = []
    for r in results:
        books.append({
            'id': r.id,
            'title': r.title,
            'author': r.author,
            'genre': r.genre,
            'cover_image_url': r.cover_image_url,
            'loan_count': r.loan_count
        })
    
    return jsonify({'books': books}), 200


# =============================================================================
# MAIN
# =============================================================================

@app.route('/')
def index():
    return jsonify({'message': 'Libris API is running'}), 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if Book.query.count() == 0:
            seed_data()

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
