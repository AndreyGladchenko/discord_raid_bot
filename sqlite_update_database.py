import sqlite3

db_name = 'raid_events.db'


def update_events(events):
    conn = sqlite3.connect(db_name)

    for timestamp, values in events.items():
        existing_record = conn.execute('SELECT * FROM events_table WHERE timestamp=?', (timestamp,)).fetchone()
        # if existing_record is not None:
        #     conn.execute(
        #         'UPDATE events_table SET user=?, owner=?, success=?, attempts=?, object=?, lock_type=?, alert_sent=COALESCE(?, alert_sent) WHERE timestamp=?',
        #         (values['user'], values['owner'], values['success'], values['attempts'], values['object'],
        #          values['lock_type'], values.get('alert_sent'), timestamp))
        # else:
        if existing_record is None:
            conn.execute(
                'INSERT INTO events_table (timestamp, user, owner, success, attempts, object, lock_type, alert_sent) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (timestamp, values['user'], values['owner'], values['success'], values['attempts'], values['object'],
                 values['lock_type'], values.get('alert_sent', 0)))

    conn.commit()
    conn.close()


def add_user(user_id, username):
    conn = sqlite3.connect(db_name)

    conn.execute('INSERT INTO subscribers (user_id, username) VALUES (?, ?)', (user_id, username))

    conn.commit()
    conn.close()
