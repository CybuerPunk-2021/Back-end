import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from pprint import pprint

if not firebase_admin._apps:
    cred = credentials.Certificate("./key/key.json")
    firebase_admin.initialize_app(cred,{'databaseURL' : 'https://decisive-sylph-308301-default-rtdb.firebaseio.com/'})

# 프로필

def get_profile(uid):
    """
    유저의 프로필 내용을 불러오는 함수

    uid(str) : 해당 프로필 유저의 uid
    """
    return db.reference('PROFILE/' + uid).get()

def delete_profile(uid):
    dir = db.reference('PROFILE/' + uid)
    dir.delete
    dir = db.reference('PROFILE')

"""
def get_visitbook_comment():
"""

"""
def get_visitbook_comment_reply(uid, cid):
    dir = db.reference('VISITBOOK/' + uid + '/cid/')
"""

def test():
    print("a")