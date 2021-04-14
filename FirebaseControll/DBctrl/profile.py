import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

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
        'nickname': '닉네임',
        'num_follower': 팔로워 수,
        'num_following': 팔로잉 수,
        'profile_image': '프로필 이미지, image_path',
        'snapshot_info':
        {
            'comment': '스냅샷 코멘트',
            'like': 스냅샷 좋아요 수,
            'thumbnail': '스냅샷 썸네일 이미지, image_path',
            'timestamp': '스냅샷 생성 시기',
            'version': '스냅샷 버전'
        }
    }
}
"""

# 프로필

def get_all_profile():
    """
    DB에 있는 모든 유저의 프로필 내용을 불러오는 함수
    """
    return db.reference('PROFILE').get()

def get_profile(uid):
    """
    유저의 프로필 내용을 불러오는 함수
    유저 데이터가 존재하면 해당 프로필 정보를 반환, 없으면 None 반환

    uid(str) : 해당 프로필 유저의 uid
    """
    return db.reference('PROFILE').child(str(uid)).get()

def make_profile(uid, login_id):
    """
    해당 uid 값으로 초기 프로필 데이터를 세팅하는 함수

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
            'nickname': str(login_id),
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

def change_nickname(uid, new_name):
    """
    프로필 닉네임을 수정하는 함수

    uid(str) : 해당 프로필 유저의 uid
    new_name(str) : 변경할 닉네임 정보
    """

    dir = db.reference('PROFILE').child(str(uid))
    dir.update({'nickname':new_name})

def change_introduction(uid, new_intro):
    """
    프로필 간단 소개글을 수정하는 함수

    uid(str) : 해당 프로필 유저의 uid
    new_name(str) : 변경할 간단 소개글 정보
    """

    dir = db.reference('PROFILE').child(str(uid))
    dir.update({'introduction':new_intro})

def delete_profile(uid):
    """
    유저의 프로필 정보를 삭제
    삭제를 성공하면 True, 아니면 False를 반환

    login_id(str) : 유저의 로그인 아이디
    """
    # 현재 DB상에 해당 아이디의 사용자가 있으면 진행
    if get_userinfo(str(login_id)) is not None:
        # DB에서 삭제
        dir = db.reference('PROFILE').child(str(uid))
        dir.delete()

        print("Delete " + str(login_id) + "(uid : " + str(uid) + ") profile.")
        return True
    # 현재 DB상에 해당 아이디의 사용자가 없으면 중단  
    else:
        print("There's no UID in DB.")
        return False
