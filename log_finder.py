import firebase_admin
from firebase_admin import db
from pprint import pprint

key_path = "./key/key.json"
if not firebase_admin._apps:
    cred = firebase_admin.credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred,{'databaseURL' : 'https://decisive-sylph-308301-default-rtdb.firebaseio.com/'})

def log_find_data(query):
    dir = db.reference('LOG')
    logs = dir.get()
    lst = []
    for log in logs:
        data = logs[log]['data']['content']
        result = True
        for q in query:
            if not q in data:
                result = False
                break
            if not data[q] == query[q]:
                result = False
        if result:
            lst.append(data)
    pprint(lst)

if __name__ == '__main__':
    query = {'action': 'snapshot_del'}
    log_find_data(query)