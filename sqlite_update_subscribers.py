import sqlite3

db_name = 'raid_events.db'


def add_user(user_id, username):
    conn = sqlite3.connect(db_name)

    conn.execute('''
        INSERT INTO subscribers (user_id, username) 
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET username = excluded.username
    ''', (user_id, username))

    conn.commit()
    conn.close()
