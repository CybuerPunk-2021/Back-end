import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from . import etc
from .profile import make_profile
from .profile import get_profile
from .profile import delete_profile
from .visitbook import make_visitbook
from .visitbook import delete_visitbook

from pprint import pprint

if not firebase_admin._apps:
    cred = credentials.Certificate("./key/key.json")
    firebase_admin.initialize_app(cred,{'databaseURL' : 'https://decisive-sylph-308301-default-rtdb.firebaseio.com/'})

# USERINFO 데이터베이스 구조
"""
'USERINFO':
{
    'login_id':
    {
        'OAuth': 'OAuth 연동 정보',
        'auth_email': '이메일 주소',
        'login_pw': '해시된 비밀번호',
        'uid': 'uid 값'
    }
}
"""

def login(login_id, password):
    """
    입력받은 값으로 로그인 수행
    매개변수 password와 DB의 login_pw 내용과 일치하면 True, 아니면 False

    login_id(str) : 입력한 사용자 로그인 ID
    password(str) : 입력한 사용자 로그인 패스워드
    """
    exist_pw = db.reference('USERINFO').child(str(login_id)).child('login_pw').get()

    if exist_pw == etc.hash_password(password):
        return True
    else:
        return False

def get_all_userinfo():
    """
    DB에 있는 모든 계정의 정보를 불러오는 함수
    """
    return db.reference('USERINFO').get()

def get_userinfo(login_id):
    """
    유저의 로그인 아이디를 통해 유저의 로그인 정보를 받는 함수

    login_id(str) : 유저의 로그인 아이디
    """
    return db.reference('USERINFO').child(str(login_id)).get()

# def get_userinfo_using_uid(uid):

def get_user_uid(login_id):
    """
    유저의 로그인 아이디로 uid를 받는 함수

    login_id(str) : 유저의 로그인 아이디
    """
    return db.reference('USERINFO').child(str(login_id)).child('uid').get()

def get_id_using_email(email):
    """
    가입할 때 입력한 이메일 주소로 계정 로그인 아이디를 찾는 함수
    정보가 있으면 로그인 아이디와 userinfo를 반환, 없으면 False 반환

    email(str) : 찾고자 하는 계정의 이메일 주소 정보 
    """
    data = get_all_userinfo()
    for user in data:
        if data[user]['auth_email'] == email:
            return {user:data[user]}
    return False

def make_userinfo(login_id, login_pw, email, OAuth):
    """
    DB에 새로운 유저 로그인 정보를 생성
    생성에 성공하면 True, 실패하면 False를 반환

    login_id(str) : 유저의 로그인 아이디
    login_pw(str) : 유저의 로그인 비밀번호
    email(str) : 유저의 인증 이메일주소
    OAuth(str) : 계정 OAuth 연결 정보
    """
    # 현재 DB상에 해당 아이디의 사용자가 없으면 진행
    if get_userinfo(str(login_id)) is None:
        # uid 값 생성
        tmp_id = login_id

        # 생성한 uid가 현재 사용하지 않는 uid값이 나올 때까지 반복
        while True:
            tmp_id = tmp_id + '0'
            uid = etc.make_uid(str(tmp_id))

            if get_profile(uid) is None:
                break
        
        # password 해시화
        hash_pw = etc.hash_password(login_pw)

        # DB에 생성
        dir = db.reference('USERINFO').child(str(login_id))
        dir.set({
            'OAuth': OAuth,
            'auth_email': str(email),
            'login_pw': hash_pw,
            'uid': uid
        })

        # 유저 정보 생성 후 다른 데이터베이스 파일에 유저 구조 생성
        make_profile(uid, login_id)
        make_visitbook(uid)

        print("Producing " + login_id + " account success.")
        return True
    # 현재 DB상에 해당 아이디의 사용자가 있으면 중단  
    else:
        print("Already exist ID value.")
        return False

def modify_email(login_id, email):
    """
    유저 계정의 이메일 주소를 수정하는 함수

    login_id(str) : 유저의 로그인 아이디
    email(str) : 수정할 이메일 주소
    """
    dir = db.reference('USERINFO').child(str(login_id))
    dir.update({'auth_email':email})

def modify_pw(login_id, check_pw, new_pw):
    """
    유저 계정의 비밀번호를 수정하는 함수
    변경을 성공하면 True, 아니면 False 반환

    login_id(str) : 유저의 로그인 아이디
    check_pw(str) : 수정할 비밀번호
    new_pw(str) : 수정할 비밀번호
    """
    cur_user = get_userinfo(login_id)
    exist_pw = cur_user['login_pw']

    # 기존의 비밀번호가 맞는지 확인 후 변경
    if exist_pw == etc.hash_password(check_pw):
        dir = db.reference('USERINFO').child(str(login_id))
        dir.update({'login_pw':new_pw})
        print("Password is changed successfully.")
        return True
    else:
        print("Password is not matched.")
        return False

def delete_userinfo(login_id):
    """
    유저의 계정 정보를 삭제
    삭제를 성공하면 True, 아니면 False를 반환

    login_id(str) : 유저의 로그인 아이디
    """
    # 현재 DB상에 해당 아이디의 사용자가 있으면 진행
    if get_userinfo(str(login_id)) is not None:
        # 유저의 uid 값 불러오기
        uid = get_user_uid(login_id)

        # 프로필, 방명록 정보 삭제
        delete_visitbook(uid)
        delete_profile(uid)

        # DB에서 유저정보 삭제
        dir = db.reference('USERINFO').child(str(login_id))
        dir.delete()

        print("Delete " + login_id + " account.")
        return True
    # 현재 DB상에 해당 아이디의 사용자가 없으면 중단  
    else:
        print("There's no ID in USERINFO DB.")
        return False

"""
def make_index_rules():
    dir = db.reference()
    dir.set({
        "rules":{
            "USERINFO":{
                ".indexOn": ['uid', 'auth_email']
            }
        }
    })
"""
"""
def get_using_email(email):

    가입할 때 입력한 이메일 주소로 계정 로그인 아이디를 찾는 함수
    정보가 있으면 로그인 아이디와 userinfo를 반환, 없으면 False 반환

    email(str) : 찾고자 하는 계정의 이메일 주소 정보 

    dir = db.reference('USERINFO')
    data = dir.order_by_child('uid').get()
    #data = dir.order_by_child('auth_email').equal_to(email).get()
    return data
"""