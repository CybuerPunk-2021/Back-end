from firebase_admin import db

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

def get_all_log():
    return db.reference('LOG').get()

def get_log(timestamp):
    return db.reference('LOG').child(timestamp)

def add_log(timestamp, data, ip_address):
    dir = db.reference('LOG').child(timestamp)
    dir.set({
        'data': data,
        'IP': ip_address
        })

def add_error_log(timestamp, error_data, ip_address):
    dir = db.reference('ERROR').child(timestamp)
    dir.set({
        'data': error_data,
        'IP': ip_address
        })

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