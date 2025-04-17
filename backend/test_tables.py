import sqlite3

# Ensure you're using the correct database path
db_path = "SummAIze.db"  # Update if necessary
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Fetch all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Print the tables
print("Tables in database:", tables)

conn.close()
