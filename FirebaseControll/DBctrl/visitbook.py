import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from .etc import timestamp
from pprint import pprint

if not firebase_admin._apps:
    cred = credentials.Certificate("./key/key.json")
    firebase_admin.initialize_app(cred,{'databaseURL' : 'https://decisive-sylph-308301-default-rtdb.firebaseio.com/'})

# 방명록

def get_all_visitbook():
    """
    모든 방명록 정보를 받는 함수
    """
    return db.reference('VISITBOOK').get()

def get_visitbook(uid):
    """
    한 유저의 방명록 정보를 받는 함수
    
    uid(int) : 해당 프로필 유저의 uid 값
    """
    return db.reference('VISITBOOK').child(str(uid)).get()

def get_comment(uid, cid):
    """
    방명록의 코멘트 하나의 정보를 받는 함수

    uid(int) : 해당 프로필 유저의 uid 값
    cid(int) : 방명록 댓글 cid 값
    """
    return db.reference('VISITBOOK').child(str(uid)).child(str(cid)).get()

def get_comment_reply_cid(uid, cid):
    """
    방명록 댓글의 답글 cid를 받는 함수

    uid(int) : 해당 프로필 유저의 uid 값
    cid(int) : 방명록 댓글 cid 값
    """
    return db.reference('VISITBOOK').child(str(uid)).child(str(cid)).child('reply_cid').get()

def get_comment_reply(uid, cid):
    """
    방명록 댓글의 답글을 받는 함수

    uid(int) : 해당 프로필 유저의 uid 값
    cid(int) : 방명록 댓글 cid 값
    """
    reply_list = []
    reply_idx = get_comment_reply_cid(uid, cid)

    for idx in reply_idx:
        reply = get_comment(uid, idx)
        reply_list.append(reply)

    return reply_list

def make_visitbook(uid):
    dir = db.reference('VISITBOOK')
    dir.update({str(uid):None})

def add_comment(uid, writer_uid, comment):
    """
    유저 프로필 내 방명록에 댓글을 남기는 함수
    
    uid(int) : 해당 프로필 유저의 uid 값
    writer_uid(int) : 댓글 작성 유저의 uid 값
    comment(str) : 댓글 내용 문자열
    """
    dir = db.reference('VISITBOOK').child(str(uid))
    new_comment = dir.push()
    new_comment.set({
        'writer_uid':writer_uid,
        'comment':comment,
        'timestamp':timestamp(),
        'reply_cid':[]
    })

    return new_comment.key

def add_comment_reply(uid, cid, writer_uid, reply):
    """
    방명록 댓글에 답글을 남기는 함수
    
    uid(int) : 해당 프로필 유저의 uid 값
    cid(str) : 답글을 달 댓글의 cid 값
    writer_uid(int) : 답글 작성 유저의 uid 값
    reply(str) : 답글 내용 문자열
    """
    key = add_comment(uid, writer_uid, reply)
    dir = db.reference('VISITBOOK').child(str(uid)).child(str(cid))

    if dir.child('reply_cid').get() is None:
        dir.update({'reply_cid':[key]})
    else:
        reply_list = dir.child('reply_cid').get()
        reply_list.append(str(key))
        dir.update({'reply_cid':reply_list})

def modify_comment(uid, cid, modified_comment):
    """
    방명록 댓글 내용을 수정하는 함수
    
    uid(int) : 해당 프로필 유저의 uid 값
    cid(str) : 답글을 달 댓글의 cid 값
    modified_comment(str) : 수정할 댓글 내용
    """
    dir = db.reference('VISITBOOK').child(str(uid)).child(str(cid))
    dir.update({
        'comment':modified_comment,
        'timestamp':timestamp()
    })

def delete_comment(uid, cid):
    """
    방명록 댓글 내용을 삭제하는 함수
    이 때 해당 댓글에 달린 답글도 모두 삭제된다.
    
    uid(int) : 해당 프로필 유저의 uid 값
    cid(str) : 삭제할 댓글의 cid 값
    """
    # 해당 댓글로 위치 이동
    dir = db.reference('VISITBOOK').child(str(uid)).child(str(cid))

    # 답글이 있다면 해당 답글로 이동 후 답글을 탐색
    if dir.child('reply_cid').get() is not None:
        # 해당 댓글의 답글 cid를 받음
        reply_list = get_comment_reply_cid(str(uid), str(cid))
        # 답글 cid를 보고 삭제, 재귀함수
        for idx in reply_list:
            delete_comment(uid, idx)

    # 답글 삭제 후 마지막으로 댓글 삭제
    dir.delete()

def delete_visitbook(uid):
    """
    한 유저의 방명록 정보를 모두 삭제하는 함수
    
    uid(int) : 해당 프로필 유저의 uid 값
    """
    # 현재 DB상에 해당 uid의 데이터가 있으면 진행
    if get_visitbook(uid) is not None:
        # DB에서 삭제
        dir = db.reference('VISITBOOK').child(str(uid))
        dir.delete()

        print("Delete visitbook.(uid : " + str(uid) + ")")
        return True
    # 현재 DB상에 해당 uid의 데이터가 없으면 중단  
    else:
        print("There's no UID value in VISITBOOK DB.")
        return False