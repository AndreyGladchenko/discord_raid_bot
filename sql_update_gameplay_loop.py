import ftplib
import io
import sqlite3
import time


ftp_server = "176.57.181.22"
ftp_username = "gpftp28482171051965233"
ftp_password = "0XSyZsTt"
port = 50021
ftp_directory = "/SCUM/Saved/SaveFiles/Logs"


def read_ftp_file():
    try:
        ftp = ftplib.FTP(timeout=30)
        ftp.connect(ftp_server, port)
        ftp.login(user=ftp_username, passwd=ftp_password)

        ftp.cwd(ftp_directory)
        file_list = []
        ftp.dir(file_list.append)

        gameplay_files = [file_name for file_name in
                          [file_info.split()[-1] for file_info in file_list]
                          if "gameplay" in file_name]
        file_name = str(gameplay_files[-1:][0])
        # file_name = "gameplay_20230308140059.log"
        with io.BytesIO() as file_buffer:
            ftp.retrbinary("RETR " + file_name, file_buffer.write)
            file_contents = file_buffer.getvalue()
            events = [line.split(" ") for line in file_contents.decode('utf-16').splitlines()]
            events = _map_events(events)
            update_events(events)

        ftp.quit()

    except Exception as e:
        print(f"Error: {e}")


def update_events(events):
    conn = sqlite3.connect('raid_events.db')

    for timestamp, values in events.items():
        existing_record = conn.execute('SELECT * FROM events_table WHERE timestamp=?', (timestamp,)).fetchone()
        if existing_record is None:
            conn.execute(
                'INSERT INTO events_table (timestamp, user, owner, success, attempts, object, lock_type, alert_sent) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (timestamp, values['user'], values['owner'], values['success'], values['attempts'], values['object'],
                 values['lock_type'], values.get('alert_sent', 0)))

    conn.commit()
    conn.close()


def _map_events(events):
    mapped_events = {}
    for event in events:
        print(event)
        event_meta = {
            'user': '',
            'owner': '',
            'success': '',
            'attempts': '',
            'object': '',
            'lock_type': '',
            'alert_sent': False
        }
        if event[0]:
            for string in event:
                if event[1] == '[LogTrap]' and event[2] == 'Triggered.':
                    if string.lower() == 'owner:':
                        event_meta['owner'] = event[event.index(string) + 1].lower()
                    elif string.lower() == 'user:':
                        event_meta['user'] = event[event.index(string) + 1].lower()
                    elif string.lower() == 'name:':
                        event_meta['object'] = ' '.join(event[event.index(string)+1:event.index('Owner:')]).strip('.')
                elif event[1] == '[LogMinigame]':
                    if string.lower() == 'user:':
                        event_meta['user'] = event[event.index(string) + 1].lower()
                    elif string.lower() == 'user' and event_meta['user']:
                        event_meta['owner'] = event[event.index(string) + 3].strip(').').lower()
                    elif string.lower() == 'success:':
                        event_meta['success'] = event[event.index(string) + 1].strip('.')
                    elif string.lower() == 'attempts:':
                        event_meta['attempts'] = event[event.index(string) + 1].strip('.')
                    elif string.lower() == 'object:':
                        event_meta['object'] = event[event.index(string) + 1].strip('.')
                    elif string.lower() == 'name:':
                        event_meta['object'] = event[event.index(string) + 1].strip('.')
                    elif string.lower() == 'type:':
                        event_meta['lock_type'] = event[event.index(string) + 1].strip('.')
        if event_meta['user'] and not event_meta['owner'] == 'location:':
            id_date = event[0].strip(':')
            mapped_events[id_date] = event_meta
    return mapped_events


while True:
    read_ftp_file()
    time.sleep(5)

