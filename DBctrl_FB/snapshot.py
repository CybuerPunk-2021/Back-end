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
            'size': 스냅샷 이미지 사이즈,
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

_snapshot = db.reference('SNAPSHOT').get()
if not _snapshot:
    _snapshot = {}


def get_all_snapshot():
    """
    DB에 저장된 모든 스냅샷 정보를 불러오는 함수
    """
    return _snapshot

def get_user_snapshot(uid):
    """
    DB에서 유저가 생성한 스냅샷 데이터를 얻는 함수

    uid(int) : 스냅샷 데이터를 얻을 유저의 uid
    """
    if str(uid) in _snapshot:
        return _snapshot[str(uid)]
    else:
        print(str(uid) + " user doesn't make snapshot yet.")
        return None

def get_snapshot(uid, timestamp):
    """
    DB에서 유저가 해당 시간대에 생성한 스냅샷 데이터를 얻는 함수

    uid(int) : 스냅샷 데이터를 얻을 유저의 uid
    timestamp(str) : 스냅샷 생성 타임스탬프
    """
    if str(uid) in _snapshot and timestamp in _snapshot[str(uid)]:
        return _snapshot[str(uid)][timestamp]
    else:
        print("There's no snapshot data which was made at " + str(timestamp) + ".")
        return None

def get_user_latest_snapshot(uid):
    """
    해당 유저가 제일 최근에 만든 스냅샷 정보를 얻는 함수

    uid(int) : 최근 스냅샷 데이터를 얻을 유저의 uid
    """
    if str(uid) not in _snapshot or len(_snapshot[str(uid)]) == 0:
        return None
    else:
        timestamp = max(_snapshot[str(uid)].keys())
        latest_snapshot = {'timestamp': timestamp, 'snapshot_intro': _snapshot[str(uid)][timestamp]['snapshot_intro']}
        if 'like_user' in _snapshot[str(uid)][timestamp]:
            latest_snapshot['like_user'] = _snapshot[str(uid)][timestamp]['like_user']
        return latest_snapshot

# 스냅샷 아이템 리스트
def get_snapshot_item(uid, timestamp):
    """
    DB에 저장된 해당 스냅샷의 아이템 목록 리스트를 얻는 함수

    uid(int) : 스냅샷 데이터를 얻을 유저의 uid
    timestamp(str) : 스냅샷 생성 타임스탬프
    """
    if str(uid) not in _snapshot or timestamp not in _snapshot[str(uid)] or 'item_list' not in _snapshot[str(uid)][timestamp]:
        print("There's no item in " + str(uid) + "'s " + str(timestamp) + " snapshot.")
        return None
    else:
        return _snapshot[str(uid)][timestamp]['item_list']

# DB에 저장된 스냅샷 소개글 얻는 함수
def get_snapshot_intro(uid, timestamp):
    """
    DB에 저장된 해당 스냅샷의 간단 소개글 데이터를 얻는 함수

    uid(int) : 스냅샷 데이터를 얻을 유저의 uid
    timestamp(str) : 스냅샷 생성 타임스탬프
    """
    if str(uid) in _snapshot and timestamp in _snapshot[str(uid)] and 'snapshot_intro' in _snapshot[str(uid)][timestamp]:
        return _snapshot[str(uid)][timestamp]['snapshot_intro']
    else:
        return None

# 임의의 유저가 스냅샷을 좋아요 했는지 확인하는 함수
def is_user_like_snapshot(cur_user_uid, snapshot_creator_uid, timestamp):
    """
    임의의 유저가 해당 프로필의 유저가 생성한 스냅샷에 좋아요 표시를 했는지 확인하는 함수

    cur_user_uid(int) : 스냅샷에 좋아요 표시를 했는지 확인하고자 하는 유저의 uid
    snapshot_creator_uid(int) : 해당 스냅샷을 생성한 유저의 uid
    timestamp(str) : 스냅샷 생성 타임스탬프
    """
    if str(snapshot_creator_uid) in _snapshot and timestamp in _snapshot[str(snapshot_creator_uid)] and 'like_user' in _snapshot[str(snapshot_creator_uid)][timestamp]:
        return cur_user_uid in _snapshot[str(snapshot_creator_uid)][timestamp]['like_user']
    else:
        return False

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
    if str(uid) not in _snapshot:
        _snapshot[str(uid)] = {}
    
    _snapshot[str(uid)][timestamp] = {
        'snapshot_intro': room_snapshot.get_snapshot_object_intro(),
        'thumbnail': room_snapshot.get_snapshot_object_thumbnail(),
        'item_list': room_snapshot.get_snapshot_object_item_list()
    }
    return timestamp

# 스냅샷 소개글 수정
def modify_snapshot_intro(uid, timestamp, modified_intro):
    """
    스냅샷 소개글을 수정하는 함수

    uid(int) : 스냅샷을 생성한 유저의 uid
    timestamp(str) : 스냅샷 타임스탬프 값
    modified_intro(str) : 수정할 소개글 내용
    """
    if str(uid) in _snapshot and timestamp in _snapshot[str(uid)]:
        _snapshot[str(uid)][timestamp]['snapshot_intro'] = modified_intro
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

    # 스냅샷 데이터가 없으면 False 반환
    if str(uid) not in _snapshot or timestamp not in _snapshot[str(uid)]:
        print("There's no snapshot with that uid or timestamp.")
        return False

    # 스냅샷에 처음 좋아요 표시를 남기는 경우
    if 'like_user' not in _snapshot[str(uid)][timestamp]:
        _snapshot[str(uid)][timestamp]['like_user'] = [like_uid]

        print(str(like_uid) + " likes " + str(uid) + "'s " +  str(timestamp) + " snapshot.")
        return True
    # 스냅샷에 이미 좋아요 수가 1 이상인 경우
    else:
        # 이미 해당 유저가 좋아요 표시를 남겼다면 작업 취소
        if like_uid in _snapshot[str(uid)][timestamp]['like_user']:
            print(str(like_uid) + " user already likes " + str(uid) + "'s " +  str(timestamp) + " snapshot.")
            return False
        # 좋아요 표시를 안 남겼다면 작업 진행
        else:
            _snapshot[str(uid)][timestamp]['like_user'].append(like_uid)
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
    # 스냅샷 데이터가 없으면 False 반환
    if str(uid) not in _snapshot or timestamp not in _snapshot[str(uid)]:
        print("There's no snapshot with that uid or timestamp.")
        return False

    # 해당 스냅샷을 아무도 좋아요 표시를 남기지 않았다면 작업 취소
    if 'like_user' not in _snapshot[str(uid)][timestamp]:
        print("The user who likes "+ str(uid) + "'s " +  str(timestamp) + " snapshot doesn't exist.")
        return False

    # 해당 유저가 좋아요 표시를 남기지 않았다면 작업 취소
    if unlike_uid not in _snapshot[str(uid)][timestamp]['like_user']:
        print(str(unlike_uid) + " user doesn't like snapshot yet.")
        return False
    
    # 좋아요 표시를 남겼다면 작업 진행
    _snapshot[str(uid)][timestamp]['like_user'].remove(unlike_uid)
    print(str(unlike_uid) + " unlikes " + str(uid) + "'s " +  str(timestamp) + " snapshot.")
    return True

# 스냅샷 좋아요 수
def get_snapshot_like_num(uid, timestamp):
    """
    해당 스냅샷의 좋아요 수를 얻는 함수

    uid(int) : 해당 스냅샷을 만든 유저 uid
    timestamp(str) : 스냅샷의 타임스탬프 값
    """
    if str(uid) in _snapshot and timestamp in _snapshot[str(uid)] and 'like_user' in _snapshot[str(uid)][timestamp]:
        return len(_snapshot[str(uid)][timestamp]['like_user'])
    else:
        return 0

# 스냅샷 삭제
def delete_snapshot(uid, timestamp):
    """
    유저가 생성한 스냅샷을 DB에서 삭제하는 함수

    uid(int) : 스냅샷을 만든 유저의 uid
    timestamp(str) : 스냅샷의 타임스탬프 값
    """
    if str(uid) in _snapshot and timestamp in _snapshot[str(uid)]:
        del _snapshot[str(uid)][timestamp]
        print("Delete " + str(uid) + ", " + str(timestamp) + " snapshot success.")
        return True
        if len(_snapshot[str(uid)]) == 0:
            del _snapshot[str(uid)]
    else:
        print("There's no snapshot with that uid or timestamp.")
        return False

def modify_snapshot_size(uid, timestamp, size):
    """
    스냅샷의 이미지 사이즈 변경
    uid(int) : 스냅샷을 만든 유저의 uid
    timestamp(str) : 스냅샷의 타임스탬프 값
    size(int) : 스냅샷 이미지의 사이즈
    """
    if str(uid) in _snapshot and timestamp in _snapshot[str(uid)]:
        _snapshot[str(uid)][timestamp]['size'] = size
        return True
    else:
        print("There's no snapshot with that uid or timestamp.")
        return False

def get_snapshot_size(uid, timestamp):
    """
    스냅샷 이미지의 사이즈 가져오기
    uid(int) : 스냅샷을 만든 유저의 uid
    timestamp(str) : 스냅샷의 타임스탬프 값
    """
    if str(uid) in _snapshot and timestamp in _snapshot[str(uid)] and 'size' in _snapshot[str(uid)][timestamp]:
        return _snapshot[str(uid)][timestamp]['size']
    else:
        return 0

def save():
    dir = db.reference('SNAPSHOT')
    dir.update(_snapshot)