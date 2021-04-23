import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from .etc import timestamp

from pprint import pprint

if not firebase_admin._apps:
    cred = credentials.Certificate("./key/key.json")
    firebase_admin.initialize_app(cred,{'databaseURL' : 'https://decisive-sylph-308301-default-rtdb.firebaseio.com/'})

# RELATION 데이터베이스 구조
"""
'RELATION':
{
    'relation_id':
    {
        'from_uid': 팔로우를 건 사람의 uid,
        'timestamp': '2021-04-07 17:57:02',
        'to_uid': 팔로우를 당한 사람의 uid
    },
    ...
}
"""

def get_all_relation():
    return db.reference('RELATION').get()

def get_relation(relation_id):
    return db.reference('RELATION').child(str(relation_id)).get()

def make_relation(from_uid, to_uid):
    dir = db.reference('RELATION')
    new_data = dir.push()
    new_data.set({
        'from_uid': from_uid,
        'to_uid': to_uid,
        'timestamp': timestamp(),
    })
    print("Relation " + str(new_data.key) + " created.")
    add_follow_info(from_uid, to_uid, new_data.key)

def delete_relation(relation_id):
    dir = db.reference('RELATION').child(str(relation_id))
    relation_info = dir.get()

    from_uid = relation_info['from_uid']
    to_uid = relation_info['to_uid']

    dir.delete()
    print("Relation " + str(relation_id) + " deleted.")

# FOLLOW 데이터베이스 구조
"""
'FOLLOW':
{
    'uid':
    {
        'follower': [relation_id1, relation_id2, ...],
        'following': [relation_id2, relation_id3, ...]
    },
    ...
}
"""
def get_all_follow():
    return db.reference('FOLLOW').get()

def get_follow(uid):
    return db.reference('FOLLOW').child(str(uid)).get()

def is_following(compare_user_uid, target_user_uid):
    # compare_user의 팔로잉 목록 탐색
    dir = db.reference('FOLLOW').child(str(compare_user_uid)).child('following')
    following_list = dir.get()
    if following_list is not None:
        for idx in following_list:
            relation_info = get_relation(idx)
            if relation_info['to_uid'] == target_user_uid:
                return idx
    else:
        return None

def add_follow_info(from_uid, to_uid, relation_id):
    # from이 to를 팔로잉, 정보 저장
    dir = db.reference('FOLLOW').child(str(from_uid))
    following_list = dir.child('following').get()
    if following_list is None:
        dir.update({'following':[str(relation_id)]})
    else:
        following_list.append(str(relation_id))
        dir.update({'following':following_list})

    # from은 to의 팔로워, 정보 저장
    dir = db.reference('FOLLOW').child(str(to_uid))
    follower_list = dir.child('follower').get()
    if follower_list is None:
        dir.update({'follower':[str(relation_id)]})
    else:
        follower_list.append(str(relation_id))
        dir.update({'follower':follower_list})

    print("Follow list update complete.(" + str(from_uid) + " -> " + str(to_uid) + ")")

def delete_follow_info(from_uid, to_uid, relation_id):
    # from의 팔로잉 목록에서 to의 정보를 삭제
    dir = db.reference('FOLLOW').child(str(from_uid))
    following_list = dir.child('following').get()
    following_list.remove(str(relation_id))
    dir.update({'following':following_list})

    # to의 팔로워 목록에서 from의 정보가 삭제
    dir = db.reference('FOLLOW').child(str(to_uid))
    follower_list = dir.child('follower').get()
    follower_list.remove(str(relation_id))
    dir.update({'follower':follower_list})

    print("Follow list delete complete.(" + str(from_uid) + " -> " + str(to_uid) + ")")
    delete_relation(str(relation_id))

def follow_user(from_uid, to_uid):
    # 만약 from이 to를 팔로우하지 않은 상태라면 관계 생성
    if is_following(from_uid, to_uid) is None:
        make_relation(from_uid, to_uid)
    # 만약 이미 from에서 to를 팔로우하고 있다면 중지
    else:
        print(str(from_uid) + " already following " + str(to_uid) + ".")

def unfollow_user(from_uid, to_uid):
    relation_info = is_following(from_uid, to_uid)
    # 만약 from이 to를 팔로우하고 있다면 삭제 진행
    if relation_info is not None:
        delete_follow_info(from_uid, to_uid, relation_info)
    # 만약 이미 from이 to를 팔로우하고 있지 않다면 중지
    else:
        print(str(from_uid) + " isn't following " + str(to_uid) + ".")

# 수정 필요
"""
def delete_all_follow_user(uid):
    # from이 to를 팔로잉, 정보 저장
    dir = db.reference('FOLLOW').child(str(uid))
    following_list = dir.child('following').get()
    follower_list = dir.child('follower').get()

    if following_list is not None:
        for relation in following_list:
            get_relation(relation)['to_uid']
            dir.update({'following':[str(relation_id)]})
    else:
        following_list.append(str(relation_id))
        dir.update({'following':following_list})

    # from은 to의 팔로워, 정보 저장
    dir = db.reference('FOLLOW').child(str(to_uid))
    follower_list = dir.child('follower').get()
    if follower_list is None:
        dir.update({'follower':[str(relation_id)]})
    else:
        follower_list.append(str(relation_id))
        dir.update({'follower':follower_list})
"""