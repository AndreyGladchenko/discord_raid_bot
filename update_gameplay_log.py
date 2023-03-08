import ftplib
import io
import json
import sqlite3
import time

from sqlite_update_database import update_events

ftp_server = "176.57.181.22"
ftp_username = "gpftp28482171051965233"
ftp_password = "0XSyZsTt"
port = 50021
ftp_directory = "/SCUM/Saved/SaveFiles/Logs"
ftp_file = "gameplay_log.json"


# def write_json(new_data, filename='gameplay_log.json'):
#     print(new_data)
#     with open(filename, 'w+') as file:
#         try:
#             # Load the existing JSON data from the file
#             file_data = json.load(file)
#         except json.decoder.JSONDecodeError:
#             # If the file is empty or contains invalid JSON data, create a new empty object
#             file_data = {}
#         # file_data = json.load(file)
#         file_data.update(new_data)
#         json.dump(file_data, file, indent=4)


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
        # file_name = "gameplay_20230306200036.log"
        with io.BytesIO() as file_buffer:
            ftp.retrbinary("RETR " + file_name, file_buffer.write)
            file_contents = file_buffer.getvalue()
            events = [line.split(" ") for line in file_contents.decode('utf-16').splitlines()]
            events = _map_events(events)
            # write_json(_map_events(events))
            update_events(events)

        ftp.quit()

    except Exception as e:
        print(f"Error: {e}")


def _map_events(events):
    mapped_events = {}
    for event in events:
        event_meta = {
            'user': '',
            'owner': '',
            'success': '',
            'attempts': '',
            'object': '',
            'lock_type': '',
            'alert_sent': False
        }
        for string in event:
            if string.lower() == 'user:':
                event_meta['user'] = event[event.index(string) + 1].lower()
            elif string.lower() == 'user' and event[event.index(string) + 1].lower() == 'owner:':
                event_meta['owner'] = event[event.index(string) + 3].strip(').').lower()
            elif string.lower() == 'success:':
                event_meta['success'] = event[event.index(string) + 1].strip('.')
            elif string.lower() == 'attempts:':
                event_meta['attempts'] = event[event.index(string) + 1].strip('.')
            elif string.lower() == 'object:':
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

