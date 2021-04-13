import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from pprint import pprint

if not firebase_admin._apps:
    cred = credentials.Certificate("./key/key.json")
    firebase_admin.initialize_app(cred,{'databaseURL' : 'https://decisive-sylph-308301-default-rtdb.firebaseio.com/'})

# 기타 조작 함수

def get_all_data():
    """
    DB의 모든 데이터를 출력하는 함수
    """
    print("Are you sure? (if yes, input 'y' or 'Y'.)")
    response = input()

    if response is 'y' or 'Y' or '':
        dir = db.reference()
        return dir.get()