from firebase_admin import db

import asyncio
import time

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
        'follower_num': '팔로워 수',
        'following_num': '팔로잉 수'
    },
    ...
}
"""

def increase_num(follow_num):
    return follow_num + 1 if follow_num else 1

def decrease_num(follow_num):
    return follow_num - 1 if follow_num > 0 else 0

def get_all_follow_info():
    """
    모든 유저의 FOLLOW DB 내 팔로잉, 팔로워 리스트의 relation id를 얻는 함수
    """
    return db.reference('N_FOLLOW').get()

def get_follow_info(uid):
    return db.reference('N_FOLLOW').child(str(uid)).get()
# 
def get_user_following_list(uid):
    return db.reference('N_FOLLOW').child(str(uid)).child('following').get()
# 
def get_user_follower_list(uid):
    return db.reference('N_FOLLOW').child(str(uid)).child('follower').get()

def get_user_following_num(uid):
    return db.reference('N_FOLLOW').child(str(uid)).child('following_num').get() or 0

def get_user_follower_num(uid):
    return db.reference('N_FOLLOW').child(str(uid)).child('follower_num').get() or 0

async def add_user_in_following_list(list_host_uid, list_add_uid, timestamp):
    data_dir = db.reference('N_FOLLOW').child(str(list_host_uid)).child('following')
    num_dir = db.reference('N_FOLLOW').child(str(list_host_uid)).child('following_num')

    # 이미 from이 to를 팔로잉하고 있다면 False 출력
    if data_dir.child(str(list_add_uid)).get() is not None:
        print(str(list_host_uid) + " user already following " + str(list_add_uid) + " user.")
        return False

    # from이 to를 팔로우하고 있지 않다면 데이터 입력
    begin = time.time()
    data_dir.update({str(list_add_uid): timestamp})
    end = time.time()
    print("update")
    print(round(end - begin, 3))
    begin = time.time()
    num_dir.transaction(increase_num)
    end = time.time()
    print("transaction")
    print(round(end - begin, 3))
    
    return True

async def add_user_in_follower_list(list_host_uid, list_add_uid, timestamp):
    data_dir = db.reference('N_FOLLOW').child(str(list_host_uid)).child('follower')
    num_dir = db.reference('N_FOLLOW').child(str(list_host_uid)).child('follower_num')

    # 이미 from이 to의 팔로워라면 False 출력
    if data_dir.child(str(list_add_uid)).get() is not None:
        print(str(list_host_uid) + " user already has follower " + str(list_add_uid) + " user.")
        return False

    # from이 to를 팔로우하고 있지 않다면 데이터 입력
    data_dir.update({str(list_add_uid): timestamp})
    num_dir.transaction(increase_num)
    return True

def delete_user_in_following_list(list_host_uid, list_delete_uid):
    data_dir = db.reference('N_FOLLOW').child(str(list_host_uid)).child('following').child(str(list_delete_uid))
    num_dir = db.reference('N_FOLLOW').child(str(list_host_uid)).child('following_num')
    
    data_dir.delete()
    num_dir.transaction(decrease_num)
    return True

def delete_user_in_follower_list(list_host_uid, list_delete_uid):
    data_dir = db.reference('N_FOLLOW').child(str(list_host_uid)).child('follower').child(str(list_delete_uid))
    num_dir = db.reference('N_FOLLOW').child(str(list_host_uid)).child('follower_num')

    data_dir.delete()
    num_dir.transaction(decrease_num)
    return True

def follow_user(from_uid, to_uid, timestamp):
    # 각 유저의 팔로잉, 팔로워 리스트에 상대방을 추가
    loop = asyncio.get_event_loop()
    loop.run_until_complete(add_user_in_following_list(from_uid, to_uid, timestamp))
    loop.run_until_complete(add_user_in_follower_list(to_uid, from_uid, timestamp))
    loop.close()

def unfollow_user(from_uid, to_uid):
    # 각 유저의 팔로잉, 팔로워 리스트에 상대방을 추가
    delete_user_in_following_list(from_uid, to_uid)
    delete_user_in_follower_list(to_uid, from_uid)