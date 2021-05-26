from firebase_admin import db

from .etc import make_uid
from .etc import hash_password
from .follow import delete_user_follow_info
from .profile import get_profile_nickname
from .profile import is_profile_nickname_exist
from .profile import delete_profile
from .visitbook import delete_visitbook

# USERINFO 데이터베이스 구조
"""
'USERINFO':
{
    'login_id':
    {
        'auth_email': '이메일 주소',
        'login_pw': '해시된 비밀번호',
        'uid': 'uid 값'
    }
}
"""

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

def get_login_id_using_uid(uid):
    """
    계정의 uid를 이용해 유저 정보를 얻는 함수
    정보가 있으면 해당 계정의 로그인 아이디 반환, 없으면 None 반환

    uid(int) : 찾고자 하는 계정의 uid 값
    """
    dir = db.reference('USERINFO')
    founded_info = list(dir.order_by_child('uid').equal_to(str(uid)).get())
    
    # 해당 uid의 유저 정보가 없으면 None 반환
    if len(founded_info) == 0:
        return None

    # 해당 uid의 유저 정보가 있으면 로그인 아이디 반환
    return founded_info[0]

def get_login_id_using_email(email):
    """
    가입할 때 입력한 이메일 주소로 계정 로그인 아이디를 찾는 함수
    정보가 있으면 해당 계정의 로그인 아이디 반환, 없으면 None 반환

    email(str) : 찾고자 하는 계정의 이메일 주소 정보 
    """
    dir = db.reference('USERINFO')
    founded_info = list(dir.order_by_child('auth_email').equal_to(str(email)).get())
    
    # 해당 이메일 주소로 인증한 유저 정보가 없으면 None 반환
    if len(founded_info) == 0:
        return None

    return founded_info[0]

def get_user_uid(login_id):
    """
    유저의 로그인 아이디로 uid를 받는 함수

    login_id(str) : 유저의 로그인 아이디
    """
    return db.reference('USERINFO').child(str(login_id)).child('uid').get()

# 계정 생성
def make_userinfo(login_id, login_pw, email, nickname):
    """
    DB에 새로운 유저 로그인 정보를 생성
    생성에 성공하면 True, 실패하면 False를 반환

    login_id(str) : 유저의 로그인 아이디
    login_pw(str) : 유저의 로그인 비밀번호
    email(str) : 유저의 인증 이메일주소
    """
    # 현재 DB상에 해당 아이디의 사용자가 있으면 중단
    if get_userinfo(str(login_id)) is not None:
        print("Already exist ID value.")
        return False

    # uid 값 생성
    tmp_id = login_id
    # 생성한 uid가 현재 사용하지 않는 uid값이 나올 때까지 반복
    while True:
        tmp_id = tmp_id + '0'
        uid = make_uid(str(tmp_id))

        if get_login_id_using_uid(int(uid)) is None:
            break
    
    # password 해시화
    hash_pw = hash_password(login_pw)

    # DB에 생성
    dir = db.reference('USERINFO').child(str(login_id))
    dir.set({
        'auth_email': str(email),
        'login_pw': hash_pw,
        'uid': uid,
        'nickname': nickname
    })

    print("Produce " + login_id + " account success.")
    return uid

# 이메일 주소 변경
def modify_email(login_id, email):
    """
    유저 계정의 이메일 주소를 수정하는 함수

    login_id(str) : 유저의 로그인 아이디
    email(str) : 수정할 이메일 주소
    """
    dir = db.reference('USERINFO').child(str(login_id))

    # 해당 로그인 아이디의 유저 계정 데이터가 없다면 False 반환
    if dir.get() is None:
        print("There's no " + login_id + " user.")
        return False

    # 이메일 주소 업데이트 후 True 반환
    dir.update({'auth_email':email})
    return True

# 비밀번호 변경(로그인 아이디)
def modify_password_using_login_id(login_id, check_pw, new_pw):
    """
    로그인 아이디를 이용해 유저 계정의 비밀번호를 수정하는 함수
    변경을 성공하면 True, 아니면 False 반환

    login_id(str) : 유저의 로그인 아이디
    check_pw(str) : 수정할 비밀번호
    new_pw(str) : 수정할 비밀번호
    """
    cur_user = get_userinfo(login_id)

    # 해당 login ID의 유저가 없으면 False 반환
    if cur_user is None:  
        print("Invalid user login ID.")
        return False

    # 해당 login ID의 유저가 있으면 변경 진행
    exist_pw = cur_user['login_pw']
    
    # 기존의 비밀번호와 일치하지 않으면 False 반환
    if exist_pw != hash_password(check_pw):
        print("Password is not correct.")
        return False
    
    # 기존의 비밀번호와 일치하면 변경 후 True 반환
    dir = db.reference('USERINFO').child(str(login_id))
    dir.update({'login_pw':hash_password(new_pw)})
    print("Password is changed successfully.")
    return True

# 비밀번호 변경(유저 UID)
def modify_password_using_uid(uid, check_pw, new_pw):
    """
    유저의 uid를 이용해 유저 계정의 비밀번호를 수정하는 함수
    변경을 성공하면 True, 아니면 False 반환

    uid(int) : 유저의 uid
    check_pw(str) : 수정할 비밀번호
    new_pw(str) : 수정할 비밀번호
    """
    dir = db.reference('USERINFO')
    cur_user = dir.order_by_child('uid').equal_to(str(uid)).get()

    # 해당 uid의 유저가 없으면 False 반환
    if len(cur_user) == 0:
        print("Invalid user UID.")
        return False

    user_data = cur_user.popitem(last=True)
    exist_pw = user_data[1]['login_pw']

    # 비밀번호가 일치하지 않으면 False 반환
    if exist_pw != hash_password(check_pw):
        print("Password is not correct.")
        return False

    # 기존의 비밀번호가 맞는지 확인 후 변경
    dir = db.reference('USERINFO').child(str(user_data[0]))
    dir.update({'login_pw': hash_password(new_pw)})
    print("Password is changed successfully.")
    return True

# 유저 계정 삭제
def delete_userinfo(login_id):
    """
    유저의 계정 정보를 삭제
    삭제를 성공하면 True, 아니면 False를 반환

    login_id(str) : 유저의 로그인 아이디
    """
    # 현재 DB상에 해당 아이디의 사용자가 없으면 중단
    if get_userinfo(str(login_id)) is None:
        print("There's no ID in USERINFO DB.")
        return False

    # 유저의 uid 값 불러오기
    uid = get_user_uid(login_id)

    # 프로필, 방명록 정보 삭제
    delete_user_follow_info(uid)
    delete_visitbook(uid)
    delete_profile(uid)

    # DB에서 유저정보 삭제
    dir = db.reference('USERINFO').child(str(login_id))
    dir.delete()

    print("Delete " + login_id + " account.")
    return True

# 아이디, 이메일 중복체크
def check_id_nickname_dup(login_id, nickname):
    """
    로그인 ID와 이메일 주소 두 데이터가 현재 DB에 존재하는지 알려주는 함수
    
    데이터가 없으면 회원가입 가능, True 반환
    로그인 ID가 존재하면 -1 반환
    닉네임이 존재하면 -2 반환
    만약 두 데이터가 모두 중복이면 -1 반환 (ID 중복으로 우선 인식)

    login_id(str) : 중복 확인하고자 하는 로그인 ID
    nickname(str) : 중복 확인하고자 하는 닉네임 값
    """
    # DB에 해당 로그인 ID와 닉네임이 겹치는 게 없으면 True 반환
    if get_userinfo(login_id) is None:
        if is_profile_nickname_exist(nickname) is False:
            return True
        # 만약 DB에 같은 닉네임 값이 있으면 -2 반환
        else:
            return -2
    # 만약 DB에 같은 로그인 ID가 있으면 -1 반환
    else:    
        return -1

# 로그인 중 패스워드 검증
def login(login_id, password):
    """
    입력받은 값으로 로그인 수행
    매개변수 password와 DB의 login_pw와
    일치하면 ['유저 닉네임', uid]를, 불일치하면 False 반환

    login_id(str) : 입력한 사용자 로그인 ID
    password(str) : 입력한 사용자 로그인 패스워드
    """
    user_data = get_userinfo(login_id)
    exist_pw = user_data['login_pw']

    # 비밀번호가 일치하지 않는다면 False 반환
    if exist_pw != hash_password(password):
        return False

    # 비밀번호가 일치하면 닉네임, uid 정보 반환
    nickname = get_profile_nickname(user_data['uid'])
    return [nickname, user_data['uid']]
