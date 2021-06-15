from firebase_admin import db

from .profile import increase_follower_num
from .profile import increase_following_num
from .profile import decrease_follower_num
from .profile import decrease_following_num


_follow = db.reference("FOLLOW").get()
if not _follow:
    _follow = {}

# FOLLOW 데이터베이스 구조
"""
'FOLLOW':
{
    'uid':
    {
        'follower':
        {
            'follower_uid': 'timestamp',
            ...
        },
        'following':
        {
            'following_uid': 'timestamp',
            ...
        },
    },
    ...
}
"""

def get_all_follow_info():
    """
    모든 유저의 FOLLOW DB 내 팔로잉, 팔로워 리스트의 relation id를 얻는 함수
    """
    return _follow

def get_user_follow_info(uid):
    """
    해당 유저의 FOLLOW DB 내 팔로잉, 팔로워 relation id 리스트를 얻는 함수

    uid(int) : 유저의 uid
    """
    return _follow[str(uid)]

# 팔로잉 목록
def get_user_following_uid_list(uid):
    """
    해당 유저가 팔로우하는 유저들의 uid 목록 리스트를 받는 함수

    uid(int) : 팔로잉 목록을 찾고자 하는 유저의 uid
    """
    if str(uid) in _follow and 'following' in _follow[str(uid)]:
        return list(_follow[str(uid)]['following'].keys())
    else:
        return []

# 팔로워 목록
def get_user_follower_uid_list(uid):
    """
    해당 유저를 팔로우하는 유저들의 uid 목록 리스트를 받는 함수

    uid(int) : 팔로워 목록을 찾고자 하는 유저의 uid
    """
    if str(uid) in _follow and 'follower' in _follow[str(uid)]:
        return list(_follow[str(uid)]['follower'].keys())
    else:
        return []

def add_user_in_following_list(list_host_uid, list_add_uid, timestamp):
    """
    팔로잉 관계 형성 시 host 유저의 팔로잉 목록에 add 유저를 넣는 함수

    list_host_uid(int) : 목록 소유자의 uid
    list_add_uid(int) : 목록에 추가할 유저의 uid
    timestamp(str) : 팔로우 관계 형성 시각
    """

    if str(list_host_uid) not in _follow:
        _follow[str(list_host_uid)] = {}
    if 'following' not in _follow[str(list_host_uid)]:
        _follow[str(list_host_uid)]['following'] = {}

    # 이미 from이 to를 팔로잉하고 있다면 False 출력
    if str(list_add_uid) in _follow[str(list_host_uid)]['following']:
        print(str(list_host_uid) + " user already following " + str(list_add_uid) + " user.")
        return False
    else:
        # from이 to를 팔로우하고 있지 않다면 데이터 입력
        _follow[str(list_host_uid)]['following'][str(list_add_uid)] = timestamp
        # 유저가 추가된 목록의 유저의 팔로잉 수 증가
        increase_following_num(list_host_uid)
        return True

def add_user_in_follower_list(list_host_uid, list_add_uid, timestamp):
    """
    팔로잉 관계 형성 시 host 유저의 팔로워 목록에 add 유저를 넣는 함수

    list_host_uid(int) : 목록 소유자의 uid
    list_add_uid(int) : 목록에 추가할 유저의 uid
    timestamp(str) : 팔로우 관계 형성 시각
    """
    if str(list_host_uid) not in _follow:
        _follow[str(list_host_uid)] = {}
    if 'follower' not in _follow[str(list_host_uid)]:
        _follow[str(list_host_uid)]['follower'] = {}

    # 이미 from이 to를 팔로잉하고 있다면 False 출력
    if str(list_add_uid) in _follow[str(list_host_uid)]['follower']:
        print(str(list_host_uid) + " user already follower " + str(list_add_uid) + " user.")
        return False
    else:
        # from이 to를 팔로우하고 있지 않다면 데이터 입력
        _follow[str(list_host_uid)]['follower'][str(list_add_uid)] = timestamp
        # 유저가 추가된 목록의 유저의 팔로잉 수 증가
        increase_follower_num(list_host_uid)
        return True


def delete_user_in_following_list(list_host_uid, list_delete_uid):
    """
    언팔로우 시 host 유저의 팔로워 목록에서 delete 유저를 지우는 함수

    list_host_uid(int) : 목록 소유자의 uid
    list_delete_uid(int) : 목록에서 삭제할 유저의 uid
    """
    if is_following(list_host_uid, list_delete_uid):
        del _follow[str(list_host_uid)]['following'][str(list_delete_uid)]
        decrease_following_num(list_host_uid)
        return True
    else:
        return False

def delete_user_in_follower_list(list_host_uid, list_delete_uid):
    """
    언팔로우 시 host 유저의 팔로워 목록에서 delete 유저를 지우는 함수

    list_host_uid(int) : 목록 소유자의 uid
    list_delete_uid(int) : 목록에서 삭제할 유저의 uid
    """
    if is_follower(list_host_uid, list_delete_uid):
        del _follow[str(list_host_uid)]['follower'][str(list_delete_uid)]
        decrease_follower_num(list_host_uid)
        return True
    else:
        return False

def is_following(from_uid, to_uid):
    """
    from user가 to user를 팔로잉하고 있는지 알려주는 함수

    from_uid(int) : 팔로우 상태를 알고자 하는 유저의 uid
    to_uid(int) : 팔로우하고 있는지 알기 위한 유저의 uid
    """
    if str(from_uid) in _follow and 'following' in _follow[str(from_uid)] and str(to_uid) in _follow[str(from_uid)]['following']:
        return True
    else:
        return False

def is_follower(from_uid, to_uid):
    if str(from_uid) in _follow and 'follower' in _follow[str(from_uid)] and str(to_uid) in _follow[str(from_uid)]['follower']:
        return True
    else:
        return False

# 팔로우
def follow_user(from_uid, to_uid, timestamp):
    """
    from user가 to user를 팔로우할 때의 DB 데이터를 설정하는 함수

    팔로잉 정보를 생성하는 단계는 다음과 같다.
    - from user의 팔로잉 목록에 to user 정보를 넣는다.
    - from user의 팔로잉 수를 1 증가시킨다.
    - to user의 팔로워 목록에 from user 정보를 넣는다.
    - to user의 팔로워 수를 1 증가시킨다.

    from_uid(int) : 팔로우를 하는 유저의 uid
    to_uid(int) : 팔로우를 당하는 유저의 uid
    timestamp(str) : 팔로우 관계 형성 시각
    """
    # 자기 자신을 팔로우하는 경우 False 반환
    if from_uid == to_uid:
        return False

    # 각 유저의 팔로잉, 팔로워 리스트에 상대방을 추가
    following_status = add_user_in_following_list(from_uid, to_uid, timestamp)
    follower_status = add_user_in_follower_list(to_uid, from_uid, timestamp)
    
    # 팔로잉, 팔로워 목록 중 하나라도 갱신에 오류가 생겼다면 취소, False 반환
    if (following_status is False) or (follower_status is False):
        delete_user_in_following_list(from_uid, to_uid)
        delete_user_in_follower_list(to_uid, from_uid)
        print("Follow Error")
        return False

    # 정상적으로 팔로우 과정이 진행됐다면 True 반환
    print("Follow (" + str(from_uid) + " -> " + str(to_uid) + ")")
    return True

# 언팔로우
def unfollow_user(from_uid, to_uid):
    """
    from user가 to user를 언팔로우할 때의 DB 데이터를 설정하는 함수

    팔로잉 정보를 삭제하는 단계는 다음과 같다.
    - from user의 팔로잉 목록에 to user 정보를 지운다.
    - from user의 팔로잉 수를 1 감소시킨다.
    - to user의 팔로워 목록에 from user 정보를 지운다.
    - to user의 팔로워 수를 1 감소시킨다.

    from_uid(int) : 기존에 팔로우를 한 유저의 uid
    to_uid(int) : 기존에 팔로우를 당한 유저의 uid
    timestamp(str) : 팔로우 관계 형성 시각
    """
    # 각 유저의 팔로잉, 팔로워 리스트에 상대방을 삭제
    following_status = delete_user_in_following_list(from_uid, to_uid)
    follower_status = delete_user_in_follower_list(to_uid, from_uid)

    if following_status and follower_status:
        print("Unfollow (" + str(from_uid) + " -> " + str(to_uid) + ")")
        return True
    else:
        print("UnFollow Error")
        return False

# 회원탈퇴 시 유저의 팔로우 정보 삭제
def delete_user_follow_info(uid):
    """
    해당 유저의 FOLLOW DB 내 팔로잉, 팔로워 relation id 리스트를 얻는 함수

    uid(int) : 유저의 uid
    """
    following_list = get_user_following_uid_list(uid)
    follower_list = get_user_follower_uid_list(uid)

    # 팔로잉 리스트의 모든 유저를 언팔로우
    for following_user in following_list:
        unfollow_user(uid, int(following_user))
    
    # 팔로우 리스트의 모든 유저가 해당 유저를 언팔로우
    for follower_user in follower_list:
        unfollow_user(int(follower_user), uid)
    
    # Document 상에 마저 남은 해당 유저의 구조 삭제 
    del _follow[str(uid)]
    print("All follow information of user " + str(uid) + " is deleted.")

def save():
    dir = db.reference('FOLLOW')
    dir.update(_follow)