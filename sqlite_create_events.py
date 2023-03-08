import sqlite3

conn = sqlite3.connect('raid_events.db')

conn.execute('''CREATE TABLE IF NOT EXISTS events_table
         (timestamp TEXT PRIMARY KEY,
         user TEXT,
         owner TEXT,
         success TEXT,
         attempts TEXT,
         object TEXT,
         lock_type TEXT,
         alert_sent INTEGER);''')

conn.commit()
conn.close()

