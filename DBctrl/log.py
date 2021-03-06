from os.path import exists
import json

"""
'LOG':
{
    'timestamp':
    {
        'data': { ~~~ },
        'IP' : xxx.xxx.xxx.xxx
    }
}
"""
path = "D:\\darak\\log"
if not exists(path):
    _log = {}
else:
    f = open(path)
    _log = json.load(f)

def get_all_log():
    return _log

def get_log(timestamp):
    return _log['log'][timestamp]

def add_log(timestamp, data, ip_address):
    _log['log'][timestamp] = {'data': data, 'IP': ip}

def add_error_log(timestamp, error_data, ip_address):
    _log['error'][timestamp] = {'data': data, 'IP': ip}

def search_log(from_time, to_time):
    # 검색 날짜가 to 시각이 from 시각보다 앞서면 False 출력
    if from_time > to_time:
        print("Invalid Datetime parameter.")
        return False

    dir = db.reference('LOG')
    data_range = dir.order_by_key().start_at(str(from_time)).end_at(str(to_time) + '\uf8ff')
    return data_range.get()

def delete_log(timestamp):
    dir = db.reference('LOG').child(timestamp)
    dir.delete()

def delete_all_log():
    dir = db.reference('LOG')
    dir.delete()

def save_log(path):
    f = open(path, 'w')
    log = get_all_log()
    f.write(str(log))
    f.close()