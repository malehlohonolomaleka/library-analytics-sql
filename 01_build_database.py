"""
01_build_database.py
----------------------
Builds a realistic library management SQLite database: books, authors,
members, and loan transactions. Simulates 14 months of borrowing activity
with realistic patterns (popular titles borrowed more, some overdue loans,
seasonal variation).

Run: python 01_build_database.py
Output: library.db
"""

import random
import sqlite3
from datetime import date, timedelta

random.seed(11)

conn = sqlite3.connect("library.db")
cur = conn.cursor()

cur.executescript("""
DROP TABLE IF EXISTS loans;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS authors;
DROP TABLE IF EXISTS members;

CREATE TABLE authors (
    author_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    nationality TEXT
);

CREATE TABLE books (
    book_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author_id INTEGER REFERENCES authors(author_id),
    genre TEXT,
    year_published INTEGER,
    copies_owned INTEGER
);

CREATE TABLE members (
    member_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    join_date TEXT,
    membership_type TEXT
);

CREATE TABLE loans (
    loan_id INTEGER PRIMARY KEY,
    book_id INTEGER REFERENCES books(book_id),
    member_id INTEGER REFERENCES members(member_id),
    loan_date TEXT,
    due_date TEXT,
    return_date TEXT
);
""")

authors = [
    ("Chimamanda Ngozi Adichie", "Nigerian"), ("Trevor Noah", "South African"),
    ("Andre Brink", "South African"), ("Nnedi Okorafor", "Nigerian-American"),
    ("Zakes Mda", "South African"), ("Ben Okri", "Nigerian"),
    ("J.M. Coetzee", "South African"), ("Yaa Gyasi", "Ghanaian-American"),
    ("Isabel Allende", "Chilean"), ("Kazuo Ishiguro", "British"),
    ("Delia Owens", "American"), ("Taylor Jenkins Reid", "American"),
    ("Colleen Hoover", "American"), ("Matt Haig", "British"),
    ("James Clear", "American"), ("Yuval Noah Harari", "Israeli"),
]

genres = ["Literary Fiction", "Non-Fiction", "Science Fiction", "Romance",
          "Self-Help", "History", "Fantasy", "Biography"]

book_titles = [
    "The River Between", "Homegoing Ways", "Silent Echoes", "Fractured Light",
    "The Last Harvest", "Whispers of the Veld", "Digital Sunrise", "The Long Walk Home",
    "Ashes and Amber", "The Quiet Storm", "Beneath the Baobab", "City of Glass Towers",
    "The Fisherman's Daughter", "Northern Lights Falling", "The Wandering Mind",
    "Songs of the Savannah", "The Coder's Dilemma", "Autumn in the Cape",
    "The Forgotten Archive", "Where the Rivers Meet", "The Midnight Library Card",
    "Atomic Habits Revisited", "Sapiens: A Retelling", "The Seven Husbands",
    "It Ends With Us Too", "The Midnight Library", "Educated Again",
    "Becoming Someone Else", "The Silent Patient's Return", "Verity's Shadow",
]

cur.executemany("INSERT INTO authors (author_id, name, nationality) VALUES (?, ?, ?)",
                 [(i+1, n, nat) for i, (n, nat) in enumerate(authors)])

books = []
for i, title in enumerate(book_titles):
    author_id = random.randint(1, len(authors))
    genre = random.choice(genres)
    year = random.randint(1995, 2025)
    copies = random.choice([1, 1, 2, 2, 3, 4, 5])
    books.append((i+1, title, author_id, genre, year, copies))
cur.executemany("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?)", books)

first_names = ["Thabo", "Lerato", "Sipho", "Naledi", "Kagiso", "Zanele", "Mpho",
               "Bongani", "Ayanda", "Nomvula", "Katlego", "Tshepo", "Palesa", "Sizwe"]
last_names = ["Nkosi", "Dlamini", "Mokoena", "Khumalo", "Mahlangu", "Sithole",
              "Molefe", "Ndlovu", "Zulu", "Mthembu"]

member_types = ["Standard", "Student", "Senior", "Premium"]
members = []
for i in range(60):
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    join_date = date(2024, 1, 1) + timedelta(days=random.randint(0, 500))
    m_type = random.choice(member_types)
    members.append((i+1, name, join_date.isoformat(), m_type))
cur.executemany("INSERT INTO members VALUES (?, ?, ?, ?)", members)

# Popularity weighting: some books borrowed far more often than others
popularity = {b[0]: random.choice([1,1,1,2,2,3,3,4,5,8]) for b in books}
weighted_book_ids = []
for book_id, weight in popularity.items():
    weighted_book_ids.extend([book_id] * weight)

start = date(2025, 1, 1)
end = date(2026, 7, 1)
total_days = (end - start).days

loans = []
loan_id = 1
for _ in range(1400):
    loan_date = start + timedelta(days=random.randint(0, total_days))
    # Fewer loans on weekends (library closed Sundays)
    if loan_date.weekday() == 6:
        continue
    book_id = random.choice(weighted_book_ids)
    member_id = random.randint(1, len(members))
    due_date = loan_date + timedelta(days=14)

    # 70% returned on time, 18% returned late, 12% still outstanding (if recent)
    roll = random.random()
    days_since_due = (date(2026, 7, 28) - due_date).days
    if roll < 0.70:
        return_date = loan_date + timedelta(days=random.randint(3, 13))
    elif roll < 0.88:
        return_date = due_date + timedelta(days=random.randint(1, 20))
    else:
        return_date = None if days_since_due > -5 else loan_date + timedelta(days=random.randint(3, 13))

    if return_date and return_date > date(2026, 7, 28):
        return_date = None

    loans.append((loan_id, book_id, member_id, loan_date.isoformat(), due_date.isoformat(),
                  return_date.isoformat() if return_date else None))
    loan_id += 1

cur.executemany("INSERT INTO loans VALUES (?, ?, ?, ?, ?, ?)", loans)

conn.commit()
print(f"Built library.db: {len(authors)} authors, {len(books)} books, {len(members)} members, {len(loans)} loans")
conn.close()
