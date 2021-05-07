import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from .follow import get_user_following_num
from .follow import get_user_follower_num
from .follow import update_profile_following_num
from .follow import update_profile_follower_num
from .follow import delete_user_all_follow_info
from .snapshot import SnapshotObj
from .snapshot import get_user_latest_made_snapshot

from pprint import pprint

if not firebase_admin._apps:
    cred = credentials.Certificate("./key/key.json")
    firebase_admin.initialize_app(cred,{'databaseURL' : 'https://decisive-sylph-308301-default-rtdb.firebaseio.com/'})

# PROFILE 데이터베이스 구조
"""
'PROFILE':
{
    'uid':
    {
        'bg_image': '백그라운드 이미지, image_path',
        'introduction': '간단 소개글',
        'login_id': 'USERINFO의 로그인 아이디',
        'login_id_upper': 'USERINFO의 로그인 아이디 색인용 대문자 버전',
        'nickname': '닉네임',
        'nickname_upper': '닉네임 색인용 대문자 버전',
        'num_follower': 팔로워 수,
        'num_following': 팔로잉 수,
        'profile_image': '프로필 이미지, image_path',
        'snapshot_info':
        {
            'snapshot_intro': '스냅샷 코멘트',
            'like_num': 스냅샷 좋아요 수,
            'thumbnail': '스냅샷 썸네일 이미지, image_path',
            'timestamp': '스냅샷 생성 시기',
        }
    }
}
"""

def is_profile_exist(uid):
    """
    해당 uid 값을 가진 유저가 존재하는지 알려주는 함수
    해당 uid의 유저가 있다면 True, 없다면 False 반환

    uid(int) : 찾고자 하는 유저의 uid
    """
    dir = db.reference('PROFILE').child(str(uid))
    return dir.get() is not None

def is_profile_nickname_exist(nickname):
    """
    DB 상에 현재 입력한 닉네임을 가진 유저가 있는지 확인하는 함수
    DB에 해당 닉네임의 유저가 있으면 True, 없으면 False 반환

    nickname(str) : 찾고자 하는 닉네임 값
    """
    dir = db.reference('PROFILE')
    founded_info = dir.order_by_child('nickname').equal_to(nickname).get()

    return len(founded_info) > 0

def get_all_profile():
    """
    DB에 있는 모든 유저의 프로필 내용을 불러오는 함수
    """
    return db.reference('PROFILE').get()

# 유저 프로필
def get_profile(uid):
    """
    유저의 프로필 내용을 불러오는 함수
    유저 데이터가 존재하면 해당 프로필 정보를 반환, 없으면 None 반환

    uid(int) : 해당 프로필 유저의 uid
    """
    if is_profile_exist(str(uid)) is True:
        dir = db.reference('PROFILE').child(str(uid))

        # 팔로잉, 팔로워 수 동기화
        if dir.child('num_following').get() != get_user_following_num(uid):
            update_profile_following_num(uid)
        if dir.child('num_follower').get() != get_user_follower_num(uid):
            update_profile_follower_num(uid)
        return dir.get()
    else:
        return None

def get_profile_nickname(uid):
    """
    해당 유저의 닉네임을 받는 함수

    uid(int) : 해당 프로필 유저의 uid
    """
    return db.reference('PROFILE').child(str(uid)).child('nickname').get()

def search_profile_nickname(nickname):
    """
    해당 문자열을 포함하는 닉네임을 가진 유저를 검색하는 함수

    nickname(str) : 닉네임 검색 키워드
    """
    data = db.reference('PROFILE').order_by_child('nickname_upper').start_at(str(nickname.upper())).end_at(str(nickname.upper()) + '\uf8ff').get() or []
    return len(data)

def search_profile_login_id(login_id):
    """
    해당 문자열을 포함하는 로그인 아이디를 가진 유저를 검색하는 함수

    login_id(str) : 로그인 아이디 검색 키워드
    """
    data = db.reference('PROFILE').order_by_child('login_id_upper').start_at(str(login_id.upper())).end_at(str(login_id.upper()) + '\uf8ff').get() or []
    return len(data)

# 프로필 검색
def search_profile(input_string):
    """
    해당 문자열을 포함하는 닉네임, 로그인 아이디를 가진 유저를 검색하는 함수
    닉네임 검색 결과, 로그인 아이디 검색 결과를 각각 배열 2개의 인자로 return

    input_string(str) : 검색 키워드 문자열
    """
    return [search_profile_nickname(input_string), search_profile_login_id(input_string)]

def make_profile(uid, login_id, nickname):
    """
    해당 uid 값으로 초기 프로필 데이터를 세팅하는 함수
    생성에 성공하면 True, 실패하면 False 반환

    uid(str) : 해당 프로필 유저의 uid
    login_id(str) : 해당 프로필 유저의 로그인 아이디
    """
    # 현재 DB상에 같은 uid 값이 없으면 진행
    if get_profile(str(uid)) is None:
        # DB에 생성
        dir = db.reference('PROFILE').child(str(uid))
        dir.set({
            'bg_image': None,
            'introduction': 'Hello',
            'login_id': str(login_id),
            'login_id_upper': str(login_id).upper(),
            'nickname': str(nickname),
            'nickname_upper': str(nickname).upper(),
            'num_follower': 0,
            'num_following': 0,
            'profile_image': None,
        })
        print("Setting " + login_id + " account's profile success.")
        return True
    # 현재 DB상에 같은 uid 값이 있으면 중단
    else:
        print("Already exist same UID.")
        return False

# 닉네임 변경
def modify_nickname(uid, new_name):
    """
    프로필 닉네임을 수정하는 함수
    수정을 성공하면 True, 실패하면 False 반환

    uid(str) : 해당 프로필 유저의 uid
    new_name(str) : 변경할 닉네임 정보
    """
    dir = db.reference('PROFILE').child(str(uid))
    # 유효한 유저의 uid 값일 때 진행
    if dir.get() is not None:
        # 다른 유저들이 사용하지 않는 닉네임일 때 변경
        if is_profile_nickname_exist(new_name) is False:
            dir.update({
                'nickname': new_name,
                'nickname_upper': new_name.upper()
                })
            return True
        else:
            print("Already used nickname value.")
            return False
    else:
        print("Invalid UID value.")
        return False

def modify_snapshot_preview(uid):
    """
    프로필 화면에 보여줄 스냅샷 정보를 제일 최근 만든 스냅샷 정보로 교체하는 함수

    uid(str) : 해당 프로필 유저의 uid
    """
    dir = db.reference('PROFILE').child(str(uid)).child('snapshot_info')
    # 제일 최근 생성한 스냅샷이 없다면 종료
    if get_user_latest_made_snapshot(uid) is None:
        return
    
    timestamp, snapshot_data = get_user_latest_made_snapshot(uid)
    # 현재 프로필의 최신 스냅샷 정보가 유지되고 있다면 종료 
    if dir.child('timestamp').get == timestamp
        return
    
    # 프로필에 이전 스냅샷 정보가 있다면 최신 스냅샷으로 교체
    dir.set({
        'snapshot_intro': snapshot_data['snapshot_intro'],
        'like_num': len(snapshot_data['like_uid'] or []),
        'thumbnail': snapshot_data['thumbnail'],
        'timestamp': timestamp,
    })
    return dir.child('timestamp').get()

# 간단 소개글 변경
def modify_introduction(uid, new_intro):
    """
    프로필 간단 소개글을 수정하는 함수
    수정을 성공하면 True, 실패하면 False 반환

    uid(str) : 해당 프로필 유저의 uid
    new_intro(str) : 변경할 간단 소개글 정보
    """
    dir = db.reference('PROFILE').child(str(uid))
    # 유효한 유저의 uid 값일 때 진행
    if dir.get() is not None:
        dir.update({'introduction':new_intro})
        return True
    else:
        print("Invalid UID value.")
        return False

def delete_profile(uid):
    """
    유저의 프로필 정보를 삭제
    삭제를 성공하면 True, 실패하면 False를 반환

    login_id(str) : 유저의 로그인 아이디
    """
    # 현재 DB상에 해당 uid의 데이터가 있으면 진행
    if get_profile(uid) is not None:
        # 프로필 삭제 전 유저의 팔로우 정보 삭제
        delete_user_all_follow_info(uid)

        # DB에서 삭제
        dir = db.reference('PROFILE').child(str(uid))
        loginID = dir.child('login_id').get()
        dir.delete()

        print("Delete profile.(uid : " + str(uid) + ", login ID : " + str(loginID) + ")")
        return True
    # 현재 DB상에 해당 uid의 데이터가 없으면 중단  
    else:
        print("There's no UID in PROFILE DB.")
        return False
