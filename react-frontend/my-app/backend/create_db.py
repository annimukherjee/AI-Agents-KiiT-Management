import sqlite3
import random

# Connect to your SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('students.db')
cursor = conn.cursor()

# Create the students table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    roll_no TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    cgpa REAL NOT NULL,
    college_rank INTEGER NOT NULL,
    leaves_available INTEGER NOT NULL,
    noc TEXT CHECK(noc IN ('Yes', 'No')), 
    bonafide_certificate TEXT CHECK(bonafide_certificate IN ('Yes', 'No')), 
    rank_generation TEXT CHECK(rank_generation IN ('Yes', 'No')), 
    scholarship_certificate TEXT CHECK(scholarship_certificate IN ('Yes', 'No')),
    attendance REAL NOT NULL
)
''')

# List of students to insert with random attendance percentages
students = [
    ('2205967', 'Amandeep', 8.6, 3, 5, 'No', 'No', 'No', 'No', round(random.uniform(60, 100), 2)),
    ('2205533', 'Aniruddha', 9.8, 1, 5, 'No', 'No', 'No', 'No', round(random.uniform(60, 100), 2)),
    ('2205460', 'Bhaskar', 8.4, 5, 5, 'No', 'No', 'No', 'No', round(random.uniform(60, 100), 2)),
    ('2205568', 'Mayur', 9.1, 2, 5, 'No', 'No', 'No', 'No', round(random.uniform(60, 100), 2)),
    ('2205557', 'Ishaan', 8.9, 4, 5, 'No', 'No', 'No', 'No', round(random.uniform(60, 100), 2))
]

# Insert multiple students using executemany
cursor.executemany('''
INSERT OR IGNORE INTO students (roll_no, name, cgpa, college_rank, leaves_available, noc, bonafide_certificate, rank_generation, scholarship_certificate, attendance) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', students)

# Commit the changes and close the connection
conn.commit()
conn.close()
