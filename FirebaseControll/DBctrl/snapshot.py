import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from .etc import check_list_3dim

from pprint import pprint

if not firebase_admin._apps:
    cred = credentials.Certificate("../FirebaseControll/key/key.json")
    firebase_admin.initialize_app(cred,{'databaseURL' : 'https://decisive-sylph-308301-default-rtdb.firebaseio.com/'})

# SNAPSHOT 데이터베이스 구조
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
class ItemObj:
    def __init__(self, item_id, position, scale, rotation):
        # position, scale, rotation parameter는 [int, int, int] 3차원 리스트여야 함
        self.item_id = item_id

        if check_list_3dim(position) is False:
            self.position = [None, None, None]
        else:
            self.position = position
        
        if check_list_3dim(scale) is False:
            self.scale = [None, None, None]
        else:
            self.scale = scale

        if check_list_3dim(rotation) is False:
            self.rotation = [None, None, None]
        else:
            self.rotation = rotation

    def get_item(self):
        if self is not None:
            return {'item_id':self.item_id, 'position':self.position, 'scale':self.scale, 'rotation':self.rotation}
        else:
            return None

    def get_item_id(self):
        return self.item_id

    def get_position(self):
        return self.position

    def get_scale(self):
        return self.scale

    def get_rotation(self):
        return self.rotation

    def set_position(self, position):
        # position parameter는 [int, int, int] 3차원 리스트여야 함
        if check_list_3dim(position) is False:
            return False
        self.position = position
        return True
    
    def set_scale(self, scale):
        # scale parameter는 [int, int, int] 3차원 리스트여야 함
        if check_list_3dim(scale) is False:
            return False
        self.scale = scale
        return True

    def set_rotation(self, rotation):
        # rotation parameter는 [int, int, int] 3차원 리스트여야 함
        if check_list_3dim(rotation) is False:
            return False
        self.rotation = rotation
        return True

class SnapshotObj:
    def __init__(self, version, snapshot_intro, thumbnail, item_list = []):
        self.version = version
        self.snapshot_intro = snapshot_intro
        self.thumbnail = thumbnail
        self.item_list = item_list

    def get_snapshot_object_version(self):
        return self.version
    
    def get_snapshot_object_intro(self):
        return self.snapshot_intro

    def put_item(self, item_obj):
        # item_obj의 타입이 ItemObj인지 확인
        if type(item_obj) is not ItemObj:
            print("'item_obj' type is not matched. Put ItemObj type object.")
            return False

        # item_obj가 빈 객체가 아닌지 확인
        if new_item is None:
            print("Invalid item object.")
            return False
        
        # 스냅샷 객체에 item_obj 아이템 객체를 리스트에 추가
        self.item_list.append(new_item.get_item())
    
    """
    def put_item_old(self, item_id, position, scale, rotation):
        new_item = ItemObj(item_id, position, scale, rotation)
        if new_item is not None:
            self.item_list.append(new_item.get_item())
            return True
        else:
            return False
    """
    
    def get_snapshot_object(self):
        return {'version':self.version, 'thumbnail':self.thumbnail, 'like_user':self.like_user, 'item_list':self.item_list}

def get_all_snapshot():
    """
    모든 스냅샷 정보를 불러오는 함수
    """
    return db.reference('SNAPSHOT').get()

def get_user_snapshot(uid):
    """
    유저가 생성한 스냅샷 데이터를 얻는 함수

    uid(int) : 스냅샷 데이터를 얻을 유저의 uid
    """
    dir = db.reference('SNAPSHOT').child(str(uid))

    # 유저의 스냅샷 데이터가 없으면 None 반환
    if dir.get() is None:
        print(str(uid) + " user doesn't make snapshot yet.")
        return None
    else:
        return dir.get()

def get_snapshot(uid, timestamp):
    """
    유저가 해당 시간대에 생성한 스냅샷 데이터를 얻는 함수

    uid(int) : 스냅샷 데이터를 얻을 유저의 uid
    timestamp(str) : 스냅샷 생성 타임스탬프
    """
    dir = db.reference('SNAPSHOT').child(str(uid)).child(str(timestamp))

    # 유저의 스냅샷 데이터가 없으면 None 반환
    if dir.get() is None:
        print("There's no snapshot data which was made at " + str(timestamp) + ".")
        return None
    else:
        return dir.get()

# 스냅샷 아이템 리스트
def get_snapshot_item(uid, timestamp):
    """
    해당 스냅샷의 아이템 목록 리스트를 얻는 함수

    uid(int) : 스냅샷 데이터를 얻을 유저의 uid
    timestamp(str) : 스냅샷 생성 타임스탬프
    """
    dir = db.reference('SNAPSHOT').child(str(uid)).child(str(timestamp)).child('item_list')
    if dir.get() is None:
        print("There's no item in " + str(uid) + "'s " + str(timestamp) + " snapshot.")
        return None
    else:
        return dir.get()

# 스냅샷 생성
def make_new_snapshot(uid, timestamp, room_snapshot):
    """
    유저가 새 스냅샷을 생성하는 함수
    해당 함수 사용 시 room_snapshot parameter는 SnapshotObj 객체를 넣어야 한다.
    DB 저장 성공 시 스냅샷 버전 반환, 실패 시 False 반환

    uid(int) : 스냅샷을 생성하는 유저의 uid
    timestamp(str) : 스냅샷 생성 타임스탬프, 이 값이 스냅샷의 메인 키가 된다.
    room_snapshot(SnapshotObj) : 스냅샷 정보 Snapshot 인스턴스
    """
    dir = db.reference('SNAPSHOT').child(str(uid)).child(str(timestamp))
    
    # parameter의 room_snapshot의 타입이 Snapshot일 경우 생성
    if type(room_snapshot) == Snapshot:
        dir.set(room_snapshot.get_snapshot())
        return dir.child('version').get()
    else:
        print("Invalid snapshot data.")
        return False

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
        print(str(like_uid) + " likes " + str(uid) + "'s " +  str(timestamp) + " snapshot.")
        return True

    # 스냅샷에 이미 좋아요 수가 1 이상인 경우
    # 이미 해당 유저가 좋아요 표시를 남겼다면 작업 취소
    if like_uid in user_list:
        print(str(like_uid) + " user already likes " + str(uid) + "`s " +  str(timestamp) + " snapshot.")
        return False

    # 좋아요 표시를 안 남겼다면 작업 진행
    user_list.append(like_uid)
    dir.update({'like_user':user_list})
    print(str(like_uid) + " likes " + str(uid) + "'s " +  str(timestamp) + " snapshot.")
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
