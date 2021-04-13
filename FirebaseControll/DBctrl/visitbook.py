import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from pprint import pprint

if not firebase_admin._apps:
    cred = credentials.Certificate("./key/key.json")
    firebase_admin.initialize_app(cred,{'databaseURL' : 'https://decisive-sylph-308301-default-rtdb.firebaseio.com/'})

# 방명록

def get_visitbook(uid):
    """
    유저 프로필에 보여줄 방명록 댓글을 받는 함수
    
    uid(str) : 해당 프로필 유저의 uid 값
    """
    return db.reference('VISITBOOK/' + uid).get()

def get_visitbook_last_cid(uid):
    """
    유저 프로필 내 방명록 댓글 중 마지막 댓글의 cid 값을 받는 함수
    
    uid(str) : 해당 프로필 유저의 uid 값
    """
    dir = db.reference('VISITBOOK/' + uid)

def get_visitbook_comment(uid, cid):
    """
    방명록의 코멘트 하나의 내용을 받는 함수

    uid(str) : 해당 프로필 유저의 uid 값
    cid(int) : 방명록 댓글 cid 값
    """
    return db.reference('VISITBOOK/' + uid + '/' + str(cid)).get()

"""
def set_visitboook_comment(uid):
    dir = db.reference('VISITBOOK/' + uid)
    dir.set(
        {
            
        }
    )
"""

def update_visitbook_comment(uid, cid, modified_comment):
    """
    방명록의 코멘트를 수정하는 함수

    uid(str) : 해당 프로필 유저의 uid 값
    cid(int) : 방명록 댓글 cid 값
    modified_comment(str) : 수정할 코멘트 내용
    """
    dir = db.reference('VISITBOOK/' + uid + '/' + str(cid))
    dir.update({'comment' : modified_comment})

"""
def get_visitbook_comment_reply(uid, cid):
    dir = db.reference('VISITBOOK/' + uid + '/cid/')
"""
