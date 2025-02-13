import sqlite3

# Connect to (or create) the database
conn = sqlite3.connect('students.db')
cursor = conn.cursor()

# Create the students table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        rollnum TEXT PRIMARY KEY,
        name TEXT NOT NULL
    )
''')

# Optionally, insert some sample data
# cursor.execute("INSERT INTO students (rollnum, name) VALUES (?, ?)", ("12345", "John Doe"))
# conn.commit()

print("Database and table created successfully!")
conn.commit()
conn.close()