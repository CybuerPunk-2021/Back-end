import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from pprint import pprint

if not firebase_admin._apps:
    cred = credentials.Certificate("./key/key.json")
    firebase_admin.initialize_app(cred,{'databaseURL' : 'https://decisive-sylph-308301-default-rtdb.firebaseio.com/'})

# ITEM 데이터베이스 구조
"""
'ITEM':
{
    
}
"""

# 아이템 목록

def get_all_item():
    """
    DB에 있는 모든 유저의 프로필 내용을 불러오는 함수
    """
    return db.reference('ITEM').get()

def add_category(category):
    dir = db.reference('ITEM')
    dir.push(str(category))

def add_item(category, item_name, iid, data_path, size):
    dir = db.reference('ITEM').child(str(category)).child(str(item_name))
    dir.update({
        'iid': iid,
        'data': data_path,
        'size': size
    })



# def add_item(category, )