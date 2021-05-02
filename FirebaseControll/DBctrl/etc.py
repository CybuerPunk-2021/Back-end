import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from pprint import pprint
from hashlib import sha256
import datetime

if not firebase_admin._apps:
    cred = credentials.Certificate("../FirebaseControll/key/key.json")
    firebase_admin.initialize_app(cred,{'databaseURL' : 'https://decisive-sylph-308301-default-rtdb.firebaseio.com/'})

# 기타 조작 함수

def make_uid(login_id):
    """
    id 문자열을 이용해 uid 값을 생성하는 함수
    uid 생성에 sha256 함수를 사용

    login_id(str) : uid 값을 생성할 아이디 문자열
    """
    hashed_id = sha256(login_id.encode()).hexdigest()
    # hash값을 int 최대값으로 나눈 나머지 값을 사용
    uid = str(int(hashed_id, 16) % 2147483647)

    return uid

def hash_password(password):
    # 보안 이유로 사용하면 안 될 함수
    return sha256(password.encode()).hexdigest()
    
def timestamp():
    now = datetime.datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S')

def get_all_data():
    """
    DB의 모든 데이터를 출력하는 함수
    """
    print("Are you sure? (if yes, input 'y' or 'Y'.)")
    response = input()

    if response == 'y' or response == 'Y':
        dir = db.reference()
        return dir.get()
    else:
        return
