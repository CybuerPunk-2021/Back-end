import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from pprint import pprint

if not firebase_admin._apps:
    cred = credentials.Certificate("./key/key.json")
    firebase_admin.initialize_app(cred,{'databaseURL' : 'https://decisive-sylph-308301-default-rtdb.firebaseio.com/'})

"""
def make_user(login_id, login_pw, email):
    dir = db.reference('USERINFO')
"""

def login(login_id, password):
    """
    입력받은 값으로 로그인 수행
    매개변수 password와 DB의 login_pw 내용과 일치하면 True, 아니면 False

    login_id(str) : 입력한 사용자 로그인 ID
    password(str) : 입력한 사용자 로그인 패스워드
    """
    pwstring = db.reference('USERINFO/' + login_id + '/login_pw').get()

    if pwstring == password:
        return True
    else:
        return False

"""
def change_pw(login_id, new_pw):
    dir = db.reference('USERINFO/' + login_id)
"""
