from firebase_admin import db

from .etc import check_list_3dim

# 아이템 객체 class
"""
ItemObj : 
{
    'category' : 아이템 카테고리 이름,
    'iid' : 아이템의 고유 id,
    'position': 아이템 위치,
    'rotation': 아이템 각도,
    'scale': 아이템 사이즈
}
"""
# 스냅샷 객체 class
"""
SnapshotObj : 
{
    'snapshot_intro': 스냅샷 간단 코멘트
    'thumbnail': 스냅샷 썸네일 이미지 경로
    'item_list': 스냅샷 내 배치된 아이템 객체 리스트
}
"""

# 아이템 객체 class
class ItemObj:
    def __init__(self, category, iid, position, scale, rotation):
        """
        아이템 객체 초기 생성
        position, scale, rotation은 [int, int, int] 형식에 맞춘 값이 아니라면 None으로 초기화

        category(str) : 아이템 카테고리 이름
        iid(int) : 아이템의 고유 id
        position([int, int, int]) : 아이템의 위치 좌표값
        scale([int, int, int]) : 아이템의 크기값
        rotation([int, int, int]) : 아이템 회전값
        """
        self.category = category
        self.iid = iid

        # position, scale, rotation parameter는 [int, int, int] 3차원 리스트여야 함
        if check_list_3dim(position) is False:
            self.position = None
        else:
            self.position = position
        
        if check_list_3dim(scale) is False:
            self.scale = None
        else:
            self.scale = scale

        if check_list_3dim(rotation) is False:
            self.rotation = None
        else:
            self.rotation = rotation

    def get_item(self):
        """
        아이템 객체 요소를 얻기 위한 함수
        딕셔너리 형식으로 반환한다.
        """
        if self is not None:
            return {
                'category': self.category,
                'iid':self.iid,
                'position':self.position,
                'scale':self.scale,
                'rotation':self.rotation
                }
        else:
            return None

    def get_iid(self):
        """
        아이템 객체의 아이템 고유 번호를 확인
        """
        return self.iid

    def get_position(self):
        """
        아이템 객체의 위치 좌표값 확인
        """
        return self.position

    def get_scale(self):
        """
        아이템 객체의 사이즈 크기 확인
        """
        return self.scale

    def get_rotation(self):
        """
        아이템 객체의 회전값 확인
        """
        return self.rotation

    def set_position(self, position):
        """
        아이템 객체의 위치 좌표값 설정(수정)

        position([int, int, int]) : 아이템의 위치 좌표값
        """
        # position parameter는 [int, int, int] 3차원 리스트여야 함
        if check_list_3dim(position) is False:
            return False
        self.position = position
        return True
    
    def set_scale(self, scale):
        """
        아이템 객체의 위치 좌표값 설정(수정)

        scale([int, int, int]) : 아이템의 크기값
        """
        # scale parameter는 [int, int, int] 3차원 리스트여야 함
        if check_list_3dim(scale) is False:
            return False
        self.scale = scale
        return True

    def set_rotation(self, rotation):
        """
        아이템 객체의 위치 좌표값 설정(수정)

        rotation([int, int, int]) : 아이템 회전값
        """
        # rotation parameter는 [int, int, int] 3차원 리스트여야 함
        if check_list_3dim(rotation) is False:
            return False
        self.rotation = rotation
        return True

# 스냅샷 객체 class
class SnapshotObj:
    def __init__(self, snapshot_intro, thumbnail, item_list = []):
        """
        스냅샷 객체 초기 생성

        snapshot_intro(str) : 스냅샷 간단 코멘트
        thumbnail(str) : 스냅샷 썸네일 이미지 경로
        item_list([ItemObj,...]) : 스냅샷 내 배치된 아이템 객체 리스트
        """    
        self.snapshot_intro = snapshot_intro
        self.thumbnail = thumbnail
        self.item_list = item_list

    def get_snapshot_object(self):
        """
        스냅샷 객체 내용 확인
        딕셔너리 형태로 반환한다.
        """
        return {'snapshot_intro':self.snapshot_intro, 'thumbnail':self.thumbnail, 'item_list':self.item_list}
    
    def get_snapshot_object_intro(self):
        """
        스냅샷 객체의 간단 코멘트 내용 확인
        """
        return self.snapshot_intro

    def get_snapshot_object_thumbnail(self):
        return self.thumbnail

    def get_snapshot_object_item_list(self):
        # 스냅샷 객체에 아이템이 없다면 None 반환
        if self.item_list is None:
            return None
        
        item_list = []
        for item in self.item_list:
            item_list.append(item)

        return item_list

    def put_item(self, item_obj):
        """
        스냅샷 객체에 아이템을 배치하는 함수
        아이템 객체를 스냅샷 객체의 self.item_list에 추가
        
        item_obj(ItemObj) : 추가할 아이템 객체
        """
        # item_obj의 타입이 ItemObj인지 확인
        if type(item_obj) is not ItemObj:
            print("'item_obj' type is not matched. Put ItemObj type object.")
            return False

        # item_obj가 빈 객체가 아닌지 확인
        if item_obj is None:
            print("Invalid item object.")
            return False
        
        # 아이템 객체의 position, scale, rotation 값이 올바르게 들어갔는지 확인
        # 3차원 list 값이 아니라면 False 반환, 종료
        if check_list_3dim(item_obj.get_position()) is False:
            print("Invalid position value")
            return False
        if check_list_3dim(item_obj.get_scale()) is False:
            print("Invalid scale value")
            return False
        if check_list_3dim(item_obj.get_rotation()) is False:
            print("Invalid rotation value")
            return False
        
        # 스냅샷 객체에 item_obj 아이템 객체를 리스트에 추가
        self.item_list.append(item_obj.get_item())

# SNAPSHOT 데이터베이스 구조
"""
'SNAPSHOT':
{
    'uid':
    {
        'timestamp':
        {
            'snapshot_intro': '스냅샷 소개글',
            'thumbnail': '스냅샷 썸네일 이미지 경로',
            'like_user': [좋아요 표시한 유저 uid,...],
            'item_list': 
            [
                {
                    'category': 아이템 카테고리 이름
                    'iid': 아이템의 고유 id,
                    'position': [x, y, z], <아이템 위치>
                    'rotation': [x, y, z], <아이템 각도>
                    'scale': [x, y, z], <아이템 사이즈>
                },
                ...
            ]
        },
        ...
    }
}        
"""

def get_all_snapshot():
    """
    DB에 저장된 모든 스냅샷 정보를 불러오는 함수
    """
    return db.reference('SNAPSHOT').get()

def get_user_snapshot(uid):
    """
    DB에서 유저가 생성한 스냅샷 데이터를 얻는 함수

    uid(int) : 스냅샷 데이터를 얻을 유저의 uid
    """
    dir = db.reference('SNAPSHOT').child(str(uid))

    # 유저의 스냅샷 데이터가 없으면 None 반환
    if dir.get() is None:
        print(str(uid) + " user doesn't make snapshot yet.")
        return None
    return dir.get()

def get_snapshot(uid, timestamp):
    """
    DB에서 유저가 해당 시간대에 생성한 스냅샷 데이터를 얻는 함수

    uid(int) : 스냅샷 데이터를 얻을 유저의 uid
    timestamp(str) : 스냅샷 생성 타임스탬프
    """
    dir = db.reference('SNAPSHOT').child(str(uid)).child(str(timestamp))

    # 유저의 스냅샷 데이터가 없으면 None 반환
    if dir.get() is None:
        print("There's no snapshot data which was made at " + str(timestamp) + ".")
        return None
    return dir.get()

def get_user_latest_made_snapshot(uid):
    """
    해당 유저가 제일 최근에 만든 스냅샷 정보를 얻는 함수

    uid(int) : 최근 스냅샷 데이터를 얻을 유저의 uid
    """
    return db.reference('SNAPSHOT').child(str(uid)).order_by_value().limit_to_last(1).get() or {}

# 스냅샷 아이템 리스트
def get_snapshot_item(uid, timestamp):
    """
    DB에 저장된 해당 스냅샷의 아이템 목록 리스트를 얻는 함수

    uid(int) : 스냅샷 데이터를 얻을 유저의 uid
    timestamp(str) : 스냅샷 생성 타임스탬프
    """
    dir = db.reference('SNAPSHOT').child(str(uid)).child(str(timestamp)).child('item_list')
    if dir.get() is None:
        print("There's no item in " + str(uid) + "'s " + str(timestamp) + " snapshot.")
        return None
    else:
        return dir.get()

# DB에 저장된 스냅샷 소개글 얻는 함수
def get_snapshot_intro(uid, timestamp):
    """
    DB에 저장된 해당 스냅샷의 간단 소개글 데이터를 얻는 함수

    uid(int) : 스냅샷 데이터를 얻을 유저의 uid
    timestamp(str) : 스냅샷 생성 타임스탬프
    """
    return db.reference('SNAPSHOT').child(str(uid)).child(str(timestamp)).child('snapshot_intro').get()

# 임의의 유저가 스냅샷을 좋아요 했는지 확인하는 함수
def is_user_like_snapshot(cur_user_uid, snapshot_creator_uid, timestamp):
    """
    임의의 유저가 해당 프로필의 유저가 생성한 스냅샷에 좋아요 표시를 했는지 확인하는 함수

    cur_user_uid(int) : 스냅샷에 좋아요 표시를 했는지 확인하고자 하는 유저의 uid
    snapshot_creator_uid(int) : 해당 스냅샷을 생성한 유저의 uid
    timestamp(str) : 스냅샷 생성 타임스탬프
    """
    like_uid_list = db.reference('SNAPSHOT').child(str(snapshot_creator_uid)).child(str(timestamp)).child('like_user').get()
    # 만약 해당 스냅샷이 좋아요가 없다면 False 반환
    if like_uid_list is None:
        return False
    # cur_user가 좋아요를 눌렀는지 True/False 반환
    return cur_user_uid in like_uid_list

def update_profile_snapshot_preview(uid):
    """
    프로필 화면에 보여줄 스냅샷 정보를 제일 최근 만든 스냅샷 정보로 교체하는 함수

    uid(str) : 해당 프로필 유저의 uid
    """
    dir = db.reference('PROFILE').child(str(uid)).child('snapshot_info')
    latest_snapshot = get_user_latest_made_snapshot(uid)
    # 제일 최근 생성한 스냅샷이 없다면 종료
    if len(latest_snapshot) == 0:
        dir.delete()
        return

    data = latest_snapshot.popitem(last=True)
    timestamp, snapshot_data = data[0], data[1]
    
    # 현재 프로필의 최신 스냅샷 정보가 유지되고 있다면 종료
    if dir.child('timestamp').get() == timestamp:
        return

    if 'like_uid' in snapshot_data:
        like_num = len(snapshot_data['like_uid'])
    else:
        like_num = 0
    
    # 프로필에 이전 스냅샷 정보가 있다면 최신 스냅샷으로 교체
    dir.set({
        'snapshot_intro': snapshot_data['snapshot_intro'],
        'like_num': like_num,
        'timestamp': timestamp,
    })
    return timestamp

# 스냅샷 생성
def save_snapshot(uid, timestamp, room_snapshot):
    """
    유저가 새 스냅샷을 DB에 저장하는 함수
    해당 함수 사용 시 room_snapshot parameter는 SnapshotObj 객체를 넣어야 한다.
    DB 저장 성공 시 스냅샷 버전 반환, 실패 시 False 반환

    uid(int) : 스냅샷을 생성하는 유저의 uid
    timestamp(str) : 스냅샷 생성 타임스탬프, 이 값이 스냅샷의 메인 키가 된다.
    room_snapshot(SnapshotObj) : 스냅샷 정보 Snapshot 인스턴스
    """
    # parameter의 room_snapshot의 타입이 SnapshotObj이 아닐 경우 중지, False 반환
    if type(room_snapshot) != SnapshotObj:
        print("Invalid type of snapshot data. Put SnapshotObj type.")
        return False

    # 올바른 정보를 입력했다면 DB에 저장, 해당 스냅샷의 버전 값 반환
    dir = db.reference('SNAPSHOT').child(str(uid)).child(str(timestamp))
    dir.set({
        'snapshot_intro': room_snapshot.get_snapshot_object_intro(),
        'thumbnail': room_snapshot.get_snapshot_object_thumbnail(),
        'item_list': room_snapshot.get_snapshot_object_item_list()
    })

    # 유저의 프로필 내 최신 스냅샷 정보 동기화
    update_profile_snapshot_preview(uid)

    return timestamp

# 스냅샷 소개글 수정
def modify_snapshot_intro(uid, timestamp, modified_intro):
    """
    스냅샷 소개글을 수정하는 함수

    uid(int) : 스냅샷을 생성한 유저의 uid
    timestamp(str) : 스냅샷 타임스탬프 값
    modified_intro(str) : 수정할 소개글 내용
    """
    dir = db.reference('SNAPSHOT').child(str(uid)).child(str(timestamp))
    
    # 해당 시각에 생성된 스냅샷이 없다면 False 반환
    if dir.get() is None:
        print("There's no snapshot with that uid or timestamp.")
        return False
    
    dir.update({'snapshot_intro':modified_intro})
    
    # 유저의 프로필 내 최신 스냅샷 정보 동기화
    update_profile_snapshot_preview(uid)

    print("Modify snapshot introduction success.")
    return True

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
        print(str(like_uid) + " user already likes " + str(uid) + "'s " +  str(timestamp) + " snapshot.")
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
        print("The user who likes "+ str(uid) + "'s " +  str(timestamp) + " snapshot doesn't exist.")
        return False

    # 좋아요 표시를 남겼다면 작업 진행
    if unlike_uid in user_list:
        user_list.remove(unlike_uid)
        dir.update({'like_user':user_list})
        print(str(unlike_uid) + " unlikes " + str(uid) + "'s " +  str(timestamp) + " snapshot.")
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
    user_list = db.reference('SNAPSHOT').child(str(uid)).child(str(timestamp)).child('like_user').get() or []
    
    return len(user_list)

# 스냅샷 삭제
def delete_snapshot(uid, timestamp):
    """
    유저가 생성한 스냅샷을 DB에서 삭제하는 함수

    uid(int) : 스냅샷을 만든 유저의 uid
    timestamp(str) : 스냅샷의 타임스탬프 값
    """
    dir = db.reference('SNAPSHOT').child(str(uid)).child(str(timestamp))
    
    if dir.get() is not None:
        # SNAPSHOT에서 해당 스냅샷 삭제
        dir.delete()

        # 유저의 프로필 내 최신 스냅샷 정보 동기화
        update_profile_snapshot_preview(uid)

        print("Delete " + str(uid) + ", " + str(timestamp) + " snapshot success.")
        return True
    else:
        print("There's no snapshot with that uid or timestamp.")
        return False
