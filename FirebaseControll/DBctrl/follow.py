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
        'timestamp': '타임스탬프',
        'to_uid': 팔로우를 당한 사람의 uid
    },
    ...
}
"""

def get_all_relation():
    """
    모든 팔로우 관계 정보를 받는 함수
    """
    return db.reference('RELATION').get()

def get_relation(relation_id):
    """
    한 팔로우 관계 정보를 받는 함수

    relation_id(str) : 팔로우 관계의 id
    """
    return db.reference('RELATION').child(str(relation_id)).get()

def get_following_user_in_relation(relation_id):
    """
    관계 id가 주어졌을 때 해당 관계에서 팔로우를 하고 있는 유저의 uid를 얻는 함수

    relation_id(str) : 팔로잉 유저를 얻고자 하는 관계 id
    """
    return db.reference('RELATION').child(str(relation_id)).child('from_uid').get()

def get_follower_user_in_relation(relation_id):
    """
    관계 id가 주어졌을 때 해당 관계에서 팔로우를 당하고 있는 유저의 uid를 얻는 함수

    relation_id(str) : 팔로워 유저를 얻고자 하는 관계 id
    """
    return db.reference('RELATION').child(str(relation_id)).child('to_uid').get()

def make_relation(from_uid, to_uid):
    """
    한 유저가 다른 유저를 팔로잉한다는 관계 정보를 만드는 함수

    from_uid(int) : 팔로우를 하는 유저의 uid
    to_uid(int) : 팔로우를 당하는 유저의 uid
    """
    dir = db.reference('RELATION')
    new_data = dir.push()
    new_data.set({
        'from_uid': from_uid,
        'timestamp': timestamp(),
        'to_uid': to_uid
    })
    print("Relation " + str(new_data.key) + " created.")
    add_follow_info(from_uid, to_uid, new_data.key)

def delete_relation(relation_id):
    """
    한 유저가 다른 유저를 팔로잉한다는 관계 정보를 삭제하는 함수

    relation_id(str) : 삭제하고자 하는 관계의 relation id
    """
    dir = db.reference('RELATION').child(str(relation_id))
    relation_info = dir.get()
    
    if relation_info is not None:
        from_uid = relation_info['from_uid']
        to_uid = relation_info['to_uid']

        dir.delete()
        print("Relation " + str(relation_id) + " deleted.")
    else:
        print("There's no relation " + str(relation_id) + "in DB.")

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

def get_user_following_info(uid):
    """
    해당 유저의 FOLLOW DB 내 팔로잉 relation id 리스트를 얻는 함수

    uid(int) : 유저의 uid
    """
    return db.reference('FOLLOW').child(str(uid)).child('following').get()

def get_user_follower_info(uid):
    """
    해당 유저의 FOLLOW DB 내 팔로워 relation id 리스트를 얻는 함수

    uid(int) : 유저의 uid
    """
    return db.reference('FOLLOW').child(str(uid)).child('follower').get()

def get_user_following_uid_list(uid):
    """
    유저가 팔로우하는 유저들의 uid 목록 리스트를 받는 함수

    uid(int) : 팔로잉 목록을 찾고자 하는 유저의 uid
    """
    # 해당 uid 유저의 팔로잉 관계 목록 리스트를 받아온다.
    relation_list = db.reference('FOLLOW').child(str(uid)).child('following').get()
    
    # 만약 해당 유저가 팔로잉이 없다면 중지
    if relation_list is None:
        print(str(uid) + " doesn't follow anybody.")
        return None
    # 리스트의 관계를 선형탐색하며 해당 유저"가" 팔로우하는 유저의 uid를 받아온다.
    following_list = []
    for relation in relation_list:
        following_user_uid = db.reference('RELATION').child(str(relation)).child('to_uid').get()
        following_list.append(int(following_user_uid))
    return following_list

def get_user_follower_uid_list(uid):
    """
    유저를 팔로우하는 유저들의 uid 목록 리스트를 받는 함수

    uid(int) : 팔로워 목록을 찾고자 하는 유저의 uid
    """
    # 해당 uid 유저의 팔로워 관계 목록 리스트를 받아온다.
    relation_list = db.reference('FOLLOW').child(str(uid)).child('follower').get()
    
    # 만약 해당 유저가 팔로워가 없다면 중지
    if relation_list is None:
        print(str(uid) + " doesn't have follower.")
        return None
    # 리스트의 관계를 선형탐색하며 해당 유저"를" 팔로우하는 유저의 uid를 받아온다.
    else:
        follower_list = []
        for relation in relation_list:
            follower_user_uid = db.reference('RELATION').child(str(relation)).child('from_uid').get()
            follower_list.append(int(follower_user_uid))
        return follower_list

def get_user_following_num(uid):
    """
    유저의 팔로잉 수를 받는 함수

    uid(str) : 유저의 uid
    """
    relation_list = db.reference('FOLLOW').child(str(uid)).child('following').get()
    
    if relation_list is None:
        return 0
    else:
        return len(relation_list)

def get_user_follower_num(uid):
    """
    유저의 팔로워 수를 받는 함수

    uid(str) : 유저의 uid
    """
    relation_list = db.reference('FOLLOW').child(str(uid)).child('follower').get()
    
    if relation_list is None:
        return 0
    else:
        return len(relation_list)

def is_following(compare_user_uid, target_user_uid):
    """
    한 유저가 다른 유저를 팔로잉하고 있는지 확인하는 함수
    팔로잉하고 있다면 해당 관계의 relation_id 반환
    팔로잉하고 있지 않다면 None 반환

    compare_user_uid(int) : 찾고자 하는 팔로우 관계에서 from에 해당하는 유저 uid
    target_user_uid(int) : 찾고자 하는 팔로우 관계에서 to에 해당하는 유저 uid
    """
    # compare_user의 팔로잉 관계 목록 탐색
    relation_list = db.reference('FOLLOW').child(str(compare_user_uid)).child('following').get()
    
    # compare 유저가 한 명도 팔로우하고 있지 않다면 None 반환
    if relation_list is None:
        print("User " + str(compare_user_uid) + " doesn't follow anybody now.")
        return None
    # compare 유저가 한 명 이상 팔로우하고 있다면 진행
    else:
        # 리스트의 관계를 순차탐색
        for relation_id in relation_list:
            relation_info = get_relation(relation_id)
            if relation_info is None:
                print("Relation " + str(relation_id) + " is not exist.")
                return None
            elif relation_info['to_uid'] == target_user_uid:
                return relation_id

def add_follow_info(from_uid, to_uid, relation_id):
    """
    FOLLOW DB 내 from의 팔로잉 목록과 to의 팔로워 목록 내에서
    서로의 팔로우 정보를 추가하는 함수

    from_uid(int) : 팔로우를 끊는 유저의 uid
    to_uid(int) : 팔로우를 끊을 유저의 uid
    relation_id(str) : from이 to를 팔로우한다는 relation의 id
    """
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
    """
    FOLLOW DB 내 from의 팔로잉 목록과 to의 팔로워 목록 내에서
    서로의 팔로우 정보를 삭제하는 함수

    from_uid(int) : 팔로우를 끊는 유저의 uid
    to_uid(int) : 팔로우를 끊을 유저의 uid
    relation_id(str) : from이 to를 팔로우한다는 relation의 id
    """
    # from의 팔로잉 목록에서 to의 정보를 삭제
    dir = db.reference('FOLLOW').child(str(from_uid))
    following_list = dir.child('following').get()
    if following_list is not None:
        if relation_id in following_list:
            following_list.remove(str(relation_id))
            dir.update({'following':following_list})

    # to의 팔로워 목록에서 from의 정보가 삭제
    dir = db.reference('FOLLOW').child(str(to_uid))
    follower_list = dir.child('follower').get()
    if follower_list is not None:
        if relation_id in follower_list:
            follower_list.remove(str(relation_id))
            dir.update({'follower':follower_list})

    print("Follow list delete complete.(" + str(from_uid) + " -> " + str(to_uid) + ")")
    delete_relation(str(relation_id))

def delete_user_all_follow_info(uid):
    """
    한 유저의 모든 팔로우, 관계 정보를 삭제하는 함수
    유저의 팔로잉, 팔로워 리스트를 받은 후
    리스트를 순차탐색하며 하나씩 지운다.

    uid(int) : 정보를 삭제하고자 하는 유저의 uid
    """
    # 유저의 팔로잉, 팔로워 리스트를 받아온다.
    following_list = get_user_following_info(uid)
    follower_list = get_user_follower_info(uid)

    # 한 명 이상의 팔로잉이 있다면 진행
    if following_list is not None:
        for relation in following_list:
            delete_follow_info(uid, get_follower_user_in_relation(relation), relation)
    # 한 명 이상 팔로워가 있다면 진행
    if follower_list is not None:
        for relation in follower_list:
            delete_follow_info(get_following_user_in_relation(relation), uid, relation)

    print("All follow information of user " + str(uid) + " is deleted.")

def follow_user(from_uid, to_uid):
    """
    from user가 to user를 팔로우할 때의 DB 데이터를 설정하는 함수

    팔로잉 정보가 생성되는 단계는 다음과 같다.
    - from -> to 관계 생성
    - from의 following 목록에 관계 데이터 추가
    - to의 follower 목록에 관계 데이터 추가

    from_uid(int) : 팔로우를 하는 유저의 uid
    to_uid(int) : 팔로우를 당하는 유저의 uid
    """
    # 만약 from이 to를 팔로우하지 않은 상태라면 관계 생성
    if is_following(from_uid, to_uid) is None:
        make_relation(from_uid, to_uid)
    # 만약 이미 from에서 to를 팔로우하고 있다면 중지
    else:
        print(str(from_uid) + " already following " + str(to_uid) + ".")

def unfollow_user(from_uid, to_uid):
    """
    from user가 to user를 팔로우할 때의 DB 데이터를 설정하는 함수

    팔로잉 정보가 삭제되는 단계는 다음과 같다.
    - from의 following 목록에 관계 데이터 삭제
    - to의 follower 목록에 관계 데이터 삭제
    - from -> to 관계 삭제

    from_uid(int) : 팔로우를 끊는 유저의 uid
    to_uid(int) : 팔로우를 끊을 유저의 uid
    """
    # from이 to를 기존에 팔로우하고 있었는지 확인
    relation_info = is_following(from_uid, to_uid)

    # 만약 from이 to를 팔로우하고 있다면 삭제 진행
    if relation_info is not None:
        delete_follow_info(from_uid, to_uid, relation_info)
    # 만약 이미 from이 to를 팔로우하고 있지 않다면 중지
    else:
        print(str(from_uid) + " isn't following " + str(to_uid) + ".")
