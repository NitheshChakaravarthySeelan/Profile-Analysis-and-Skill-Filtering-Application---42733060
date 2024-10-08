import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('profiles.db')
cursor = conn.cursor()
username = 'candidate'
password = 'candidate123'  
hashed_password = generate_password_hash(password)

cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
               (username, hashed_password, 'candidate'))

conn.commit()
conn.close()
