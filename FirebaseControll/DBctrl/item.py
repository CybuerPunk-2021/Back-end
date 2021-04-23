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

# 아이템 목록

def get_all_item():
    """
    DB에 있는 모든 유저의 프로필 내용을 불러오는 함수
    """
    return db.reference('ITEM').get()

def add_category(category):
    dir = db.reference('ITEM')
    dir.push(str(category))

def add_item(category, item_name, iid, data_path, size):
    dir = db.reference('ITEM').child(str(category)).child(str(item_name))
    dir.update({
        'iid': iid,
        'data': data_path,
        'size': size
    })



# def add_item(category, )