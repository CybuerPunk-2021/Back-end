import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from pprint import pprint

if not firebase_admin._apps:
    cred = credentials.Certificate("./key/key.json")
    firebase_admin.initialize_app(cred,{'databaseURL' : 'https://decisive-sylph-308301-default-rtdb.firebaseio.com/'})

"""
'SNAPSHOT':
{
    'uid':
    {
        'timestamp':
        {
            'version': '스냅샷 버전',
            'snapshot_intro': '스냅샷 소개글',
            'thumbnail': '스냅샷 썸네일 이미지 경로',
            'like_user' : [좋아요 표시한 유저 uid,...],
            'item_list': 
            [
                {
                    'iid': 아이템 ID,
                    'position': [x, y, z], <아이템 위치>
                    'rotation': [x, y, z], <아이템 각도>
                    'scale': [x, y, z], <아이템 사이즈>
                },
                ...
            ]
        }
    }
}        
"""
class Item:
    def __init__(self, item_id, position = [0, 0, 0], scale = [0, 0, 0], rotation = [0, 0, 0]):
        self.item_id = item_id
        self.position = position
        self.scale = scale
        self.rotation = rotation
    
    def get_item(self):
        return {'item_id':self.item_id, 'position':self.position, 'scale':self.scale, 'rotation':self.rotation}

    def get_item_id(self):
        return self.item_id

    def get_position(self):
        return self.position

    def get_scale(self):
        return self.scale

    def get_rotation(self):
        return self.rotation

    def set_position(self, position):
        self.position = position
    
    def set_scale(self, scale):
        self.scale = scale

    def set_rotation(self, rotation):
        self.rotation = rotation

class Snapshot:
    def __init__(self, version, snapshot_intro, thumbnail, item_list = []):
        self.version = version
        self.snapshot_intro = snapshot_intro
        self.thumbnail = thumbnail
        self.like_user = []
        self.item_list = item_list

    def put_item(self, item_id, position, scale, rotation):
        new_item = Item(item_id, position, scale, rotation)
        self.item_list.append(new_item.get_item())
    
    def get_snapshot(self):
        return {'version':self.version, 'thumbnail':self.thumbnail, 'like_user':self.like_user, 'item_list':self.item_list}

def get_all_snapshot():
    """
    모든 스냅샷 정보를 불러오는 함수
    """
    return db.reference('SNAPSHOT').get()

# 스냅샷 생성
def make_new_snapshot(uid, timestamp, room_snapshot):
    """
    유저가 새 스냅샷을 생성하는 함수

    uid(int) : 스냅샷을 생성하는 유저의 uid
    timestamp(str) : 스냅샷 생성 타임스탬프, 이 값이 스냅샷의 메인 키가 된다.
    room_snapshot(Snapshot) : 스냅샷 정보 Snapshot 인스턴스
    """
    dir = db.reference('SNAPSHOT').child(str(uid)).child(str(timestamp))
    
    # parameter의 room_snapshot의 타입이 Snapshot일 경우 생성
    if type(room_snapshot) == Snapshot:
        dir.set(room_snapshot.get_snapshot())
        return True
    else:
        print("Invalid snapshot data.")
        return False

#def upgrade_snapshot_version(uid):

def get_snapshot_item(uid, timestamp):
    dir = db.reference('SNAPSHOT').child(str(uid)).child(str(timestamp)).child('item_list')
    return dir.get()

# 스냅샷 소개글 수정
def modify_snapshot_intro(uid, timestamp, modified_intro):
    """
    스냅샷 소개글을 수정하는 함수

    uid(int) : 스냅샷을 생성한 유저의 uid
    timestamp(str) : 스냅샷 타임스탬프 값
    modified_intro(str) : 수정할 소개글 내용
    """
    dir = db.reference('SNAPSHOT').child(str(uid)).child(str(timestamp))
    
    if dir.get() is not None:
        dir.update({'snapshot_intro':modified_intro})
        print("Modify snapshot introduction success.")
        return True
    else:
        print("There's no snapshot with that uid or timestamp.")
        return False

# 스냅샷 좋아요
def like_snapshot(uid, like_uid, timestamp):
    """
    스냅샷에 좋아요 표시를 남기는 기능 함수
    해당 스냅샷을 좋아요 표시를 남긴 유저의 uid를 리스트에 저장한다.

    uid(int) : 스냅샷 주인의 uid
    timestamp(str) : 스냅샷의 타임스탬프 값
    like_uid(int) : 스냅샷에 좋아요 표시를 남긴 유저의 uid
    """
    dir = db.reference('SNAPSHOT').child(str(uid)).child(str(timestamp))

    # 스냅샷 데이터가 없으면 False 반환
    if dir.get() is None:
        print("There's no snapshot with that uid or timestamp.")
        return False

    user_list = dir.child('like_user').get()
    # 스냅샷에 처음 좋아요 표시를 남기는 경우
    if user_list is None:
        dir.update({'like_user': [like_uid]})
        print(str(like_uid) + " likes " + str(uid) + "`s " +  str(timestamp) + " snapshot.")
        return True

    # 스냅샷에 이미 좋아요 수가 1 이상인 경우
    # 이미 해당 유저가 좋아요 표시를 남겼다면 작업 취소
    if like_uid in user_list:
        print(str(like_uid) + " user already likes " + str(uid) + "`s " +  str(timestamp) + " snapshot.")
        return False

    # 좋아요 표시를 안 남겼다면 작업 진행
    user_list.append(like_uid)
    dir.update({'like_user':user_list})
    print(str(like_uid) + " likes " + str(uid) + "`s " +  str(timestamp) + " snapshot.")
    return True

# 스냅샷 좋아요 취소
def unlike_snapshot(uid, unlike_uid, timestamp):
    """
    스냅샷에 남긴 좋아요 표시를 취소하는 함수
    해당 스냅샷을 좋아요 표시를 남긴 유저의 uid를 리스트에서 삭제한다.

    uid(int) : 스냅샷 주인의 uid
    timestamp(str) : 스냅샷의 타임스탬프 값
    like_uid(int) : 스냅샷에 좋아요 표시를 취소한 유저의 uid
    """
    dir = db.reference('SNAPSHOT').child(str(uid)).child(str(timestamp))

    # 스냅샷 데이터가 없으면 False 반환
    if dir.get() is None:
        print("There's no snapshot with that uid or timestamp.")
        return False

    user_list = dir.child('like_user').get()
    # 해당 스냅샷을 아무도 좋아요 표시를 남기지 않았다면 작업 취소
    if user_list is None:
        print("The user who likes "+ str(uid) + "`s " +  str(timestamp) + " snapshot doesn't exist.")
        return False

    # 좋아요 표시를 남겼다면 작업 진행
    if unlike_uid in user_list:
        user_list.remove(unlike_uid)
        dir.update({'like_user':user_list})
        print(str(unlike_uid) + " unlikes " + str(uid) + "`s " +  str(timestamp) + " snapshot.")
        return True
    
    # 해당 유저가 좋아요 표시를 남기지 않았다면 작업 취소
    print(str(unlike_uid) + " user doesn't like snapshot yet.")
    return False




# 스냅샷 좋아요 수
def get_snapshot_like_num(uid, timestamp):
    """
    해당 스냅샷의 좋아요 수를 얻는 함수

    uid(int) : 해당 스냅샷을 만든 유저 uid
    timestamp(str) : 스냅샷의 타임스탬프 값
    """
    user_list = db.reference('SNAPSHOT').child(str(uid)).child(str(timestamp)).child('like_user').get()
    
    if user_list is None:
        return 0
    else:
        return len(user_list)

# 스냅샷 삭제
def delete_snapshot(uid, timestamp):
    """
    유저가 생성한 스냅샷을 삭제하는 함수

    uid(int) : 스냅샷을 만든 유저의 uid
    timestamp(str) : 스냅샷의 타임스탬프 값
    """
    dir = db.reference('SNAPSHOT').child(str(uid)).child(str(timestamp))
    
    if dir.get() is not None:
        dir.delete()
        print("Delete " + str(uid) + ", " + str(timestamp) + " snapshot success.")
        return True
    else:
        print("There's no snapshot with that uid or timestamp.")
        return False