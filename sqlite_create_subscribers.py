import sqlite3


conn = sqlite3.connect('raid_events.db')

conn.execute('''CREATE TABLE subscribers
             (user_id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL);''')

conn.commit()
conn.close()
