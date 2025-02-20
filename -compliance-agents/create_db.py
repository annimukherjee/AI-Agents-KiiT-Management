import sqlite3

# Connect to your SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('students.db')
cursor = conn.cursor()

# Create the students table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    name TEXT,
    rollnum INTEGER
)
''')

# List of students to insert
students = [
    ('Mayur Gogoi', 2205568),
    ('Bhaskar Lalwani', 2205460),
    ('Mohit Gupta', 2205569),
    ('Ishaan Mukherjee', 2205557),
    ('Aniruddha Mukherjee', 2205533)
]

# Insert multiple students using executemany
cursor.executemany('INSERT INTO students (name, rollnum) VALUES (?, ?)', students)

# Commit the changes and close the connection
conn.commit()
conn.close()