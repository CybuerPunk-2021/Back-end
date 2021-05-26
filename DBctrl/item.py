from firebase_admin import db

from .etc import check_list_3dim
from .etc import increase_num

# ITEM 데이터베이스 구조
"""
'ITEM':
{
    'category':
    {
        'latest_id_num': '카테고리 내 아이템 중 id 값이 가장 큰 아이템의 id값',
        'item_list':
        [
            {
                'iid': '아이템 ID',
                'item_name': '아이템 이름',
                'scale': [x, y, z],
            },
            ...
        ]
    },
    ...
}
"""

def increase_iid_num(category):
    """
    카테고리에 아이템을 추가할 때 item id 값을 정하기 위한 트랜잭션 함수

    category(str) : 아이템을 추가할 카테고리 이름
    """
    try:
        dir = db.reference('ITEM').child(str(category)).child('latest_id_num')
        return dir.transaction(increase_num)
    except db.TransactionAbortedError:
        print("Transaction failed. -> increase following num")
        return False

def get_all_item():
    """
    DB에 있는 모든 유저의 프로필 내용을 불러오는 함수
    """
    return db.reference('ITEM').get()

def get_item(category, iid):
    """
    카테고리 내 아이템 정보를 얻는 함수

    category(str) : 아이템의 카테고리 이름
    iid(int) : 아이템의 카테고리 내 id
    """
    dir = db.reference('ITEM').child(str(category)).child('item_list')
    # 해당 카테고리에 아이템이 없다면 False 반환
    if dir.get() is None:
        print("There's no item in " + str(category) + " category.")
        return False
    
    # 카테고리의 아이템 리스트를 탐색
    item_list = dir.get()
    for item in item_list:
        # 해당 아이템의 id가 iid와 같다면 데이터 반환
        if int(item['iid']) == int(iid):
            return item
    
    # 리스트에 찾는 아이템이 없으면 False 반환
    print("There's not exist item " + str(iid) + " in " + str(category) + "category.")
    return False

# 아이템 추가
def add_item(category, item_name, scale):
    """
    ITEM DB 내 아이템을 추가하는 함수

    category(str) : 아이템의 카테고리 이름
    item_name(str) : 아이템 이름
    scale([int, int, int]) : 아이템 사이즈 3차원 배열
    """
    dir = db.reference('ITEM').child(str(category))

    # 아이템의 id 값을 결정하기 위한 번호 트랜잭션 작업
    while True:
        new_item_num = increase_iid_num(category)
        print(new_item_num)
        if new_item_num is not False:
            break
    
    # scale parameter는 3차원 리스트 타입이어야 함
    if check_list_3dim(scale) is False:
        return False

    # 추가할 아이템 data 선언
    data = {
        'iid': new_item_num,
        'item_name': item_name,
        'scale': scale,
    }

    # 해당 카테고리를 신설하는 경우
    if dir.child('item_list').get() is None:
        dir.update({'item_list': [data]})
    # 해당 카테고리가 이미 존재하는 경우
    else:
        item_list = dir.child('item_list').get()
        item_list.append(data)
        dir.update({'item_list': item_list})
    return True

# 아이템 삭제
def delete_item(category, iid):
    """
    카테고리 내 아이템 정보를 삭제하는 함수

    category(str) : 아이템의 카테고리 이름
    iid(int) : 아이템의 카테고리 내 id
    """
    dir = db.reference('ITEM').child(str(category))
    # 해당 카테고리에 아이템이 없다면 False 반환
    if dir.child('item_list').get() is None:
        print("There's no item in " + str(category) + " category.")
        return False
    
    item_list = dir.child('item_list').get()
    for item in item_list:
        if int(item['iid']) == int(iid):
            item_list.remove(item)
            dir.update({'item_list': item_list})
            return True
    
    # 리스트에 삭제하고자 하는 아이템이 없으면 False 반환
    print("There's not exist item " + str(iid) + " in " + str(category) + "category.")
    return False

def delete_category(category):
    """
    카테고리 내 모든 아이템 정보를 삭제하는 함수

    category(str) : 아이템의 카테고리 이름
    """
    dir = db.reference('ITEM').child(str(category))
    dir.delete()
