from firebase_admin import db

from .etc import increase_num
from .etc import decrease_num

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

def increase_following_num(uid):
    """
    팔로잉 리스트에 유저를 추가한 후
    PROFILE document의 팔로잉 숫자를 1 증가시키는 함수

    uid(int) : 팔로잉 수를 증가시킬 유저의 uid
    """
    try:
        dir = db.reference('PROFILE').child(str(uid)).child('num_following')
        return dir.transaction(increase_num)
    except db.TransactionAbortedError:
        print("Transaction failed. -> increase following num")
        return False
def increase_follower_num(uid):
    """
    팔로잉 리스트에 유저를 추가한 후
    PROFILE document의 팔로잉 숫자를 1 증가시키는 함수

    uid(int) : 팔로잉 수를 증가시킬 유저의 uid
    """
    try:
        dir = db.reference('PROFILE').child(str(uid)).child('num_follower')
        return dir.transaction(increase_num)
    except db.TransactionAbortedError:
        print("Transaction failed. -> increase follower num")
        return False
def decrease_following_num(uid):
    """
    팔로잉 리스트에 유저를 삭제한 후
    PROFILE document의 팔로잉 숫자를 1 감소시키는 함수

    uid(int) : 팔로잉 수를 감소시킬 유저의 uid
    """
    try:
        dir = db.reference('PROFILE').child(str(uid)).child('num_following')
        return dir.transaction(decrease_num)
    except db.TransactionAbortedError:
        print("Transaction failed. -> decrease following num")
        return False
def decrease_follower_num(uid):
    """
    팔로잉 리스트에 유저를 삭제한 후
    PROFILE document의 팔로잉 숫자를 1 감소시키는 함수

    uid(int) : 팔로잉 수를 감소시킬 유저의 uid
    """
    try:
        dir = db.reference('PROFILE').child(str(uid)).child('num_follower')
        return dir.transaction(decrease_num)
    except db.TransactionAbortedError:
        print("Transaction failed. -> decrease follower num")
        return False

def get_all_follow_info():
    """
    모든 유저의 FOLLOW DB 내 팔로잉, 팔로워 리스트의 relation id를 얻는 함수
    """
    return db.reference('FOLLOW').get()
def get_user_follow_info(uid):
    """
    해당 유저의 FOLLOW DB 내 팔로잉, 팔로워 relation id 리스트를 얻는 함수

    uid(int) : 유저의 uid
    """
    return db.reference('FOLLOW').child(str(uid)).get()

# 팔로잉 목록
def get_user_following_uid_list(uid):
    """
    해당 유저가 팔로우하는 유저들의 uid 목록 리스트를 받는 함수

    uid(int) : 팔로잉 목록을 찾고자 하는 유저의 uid
    """
    following_dict = db.reference('FOLLOW').child(str(uid)).child('following').get() or {}
    return list(following_dict.keys())
# 팔로워 목록
def get_user_follower_uid_list(uid):
    """
    해당 유저를 팔로우하는 유저들의 uid 목록 리스트를 받는 함수

    uid(int) : 팔로워 목록을 찾고자 하는 유저의 uid
    """
    follower_dict =  db.reference('FOLLOW').child(str(uid)).child('follower').get() or {}
    return list(follower_dict.keys())

def add_user_in_following_list(list_host_uid, list_add_uid, timestamp):
    """
    팔로잉 관계 형성 시 host 유저의 팔로잉 목록에 add 유저를 넣는 함수

    list_host_uid(int) : 목록 소유자의 uid
    list_add_uid(int) : 목록에 추가할 유저의 uid
    timestamp(str) : 팔로우 관계 형성 시각
    """
    dir = db.reference('FOLLOW').child(str(list_host_uid)).child('following')

    # 이미 from이 to를 팔로잉하고 있다면 False 출력
    if dir.child(str(list_add_uid)).get() is not None:
        print(str(list_host_uid) + " user already following " + str(list_add_uid) + " user.")
        return False
    else:
        # from이 to를 팔로우하고 있지 않다면 데이터 입력
        dir.update({str(list_add_uid): timestamp})
        
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
    dir = db.reference('FOLLOW').child(str(list_host_uid)).child('follower')

    # 이미 from이 to의 팔로워라면 False 출력
    if dir.child(str(list_add_uid)).get() is not None:
        print(str(list_host_uid) + " user already has follower " + str(list_add_uid) + " user.")
        return False
    else:
        # from이 to를 팔로우하고 있지 않다면 데이터 입력
        dir.update({str(list_add_uid): timestamp})

        # 유저가 추가된 목록의 유저의 팔로워 수 증가
        increase_follower_num(list_host_uid)
        return True
def delete_user_in_following_list(list_host_uid, list_delete_uid):
    """
    언팔로우 시 host 유저의 팔로워 목록에서 delete 유저를 지우는 함수

    list_host_uid(int) : 목록 소유자의 uid
    list_delete_uid(int) : 목록에서 삭제할 유저의 uid
    """
    dir = db.reference('FOLLOW').child(str(list_host_uid)).child('following').child(str(list_delete_uid))
    dir.delete()

    # 유저가 삭제된 목록의 유저의 팔로워 수 감소
    decrease_following_num(list_host_uid)
    return True
def delete_user_in_follower_list(list_host_uid, list_delete_uid):
    """
    언팔로우 시 host 유저의 팔로워 목록에서 delete 유저를 지우는 함수

    list_host_uid(int) : 목록 소유자의 uid
    list_delete_uid(int) : 목록에서 삭제할 유저의 uid
    """
    dir = db.reference('FOLLOW').child(str(list_host_uid)).child('follower').child(str(list_delete_uid))
    dir.delete()

    # 유저가 삭제된 목록의 유저의 팔로워 수 감소
    decrease_follower_num(list_host_uid)
    return True

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
    # 각 유저의 팔로잉, 팔로워 리스트에 상대방을 추가
    add_user_in_following_list(from_uid, to_uid, timestamp)
    add_user_in_follower_list(to_uid, from_uid, timestamp)

    print("Follow (" + str(from_uid) + " -> " + str(to_uid) + ")")
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
    # 각 유저의 팔로잉, 팔로워 리스트에 상대방을 추가
    delete_user_in_following_list(from_uid, to_uid)
    delete_user_in_follower_list(to_uid, from_uid)

    print("Unfollow (" + str(from_uid) + " -> " + str(to_uid) + ")")

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
    db.reference('FOLLOW').child(str(uid)).delete()
    print("All follow information of user " + str(uid) + " is deleted.")
