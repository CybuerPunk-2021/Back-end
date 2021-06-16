from firebase_admin import db

from .etc import increase_num
from .etc import decrease_num

from pprint import pprint

# VISITBOOK 데이터베이스 구조
"""
'VISITBOOK':
{
    'uid':
    {
        'comment_num': 방명록 댓글 갯수,
        'cid':
        {
            'writer_uid': 댓글 작성자 uid,
            'comment': '댓글 내용',
            'timestamp': '댓글 작성 날짜, 시각',
            'reply_num': 답글 갯수,
            'reply': 
            {
                'reply_cid': 
                {
                    'writer_uid': 댓글 작성자 uid,
                    'reply_comment': '댓글 내용',
                    'timestamp': '댓글 작성 날짜, 시각'
                },
                ...
            }
        },
        ...
    },
    ...
}
"""

_visitbook = db.reference('VISITBOOK').get()
if not _visitbook:
    _visitbook = {}


def increase_comment_num(uid):
    """
    방명록에 댓글 추가 후 답글 갯수를 1 증가시키는 함수

    uid(int) : 해당 프로필 유저의 uid 값
    """
    print(_visitbook[str(uid)])
    if str(uid) in _visitbook:
        _visitbook[str(uid)]['comment_num'] = _visitbook[str(uid)]['comment_num'] + 1
        return True
    else:
        return False

def increase_comment_reply_num(uid, cid):
    """
    방명록 내 댓글에 답글 추가 후 답글 갯수를 1 증가시키는 함수

    uid(int) : 해당 프로필 유저의 uid 값
    cid(int) : 답글이 달린 댓글의 cid 값
    """
    if str(uid) in _visitbook and str(cid) in _visitbook[str(uid)]:
        _visitbook[str(uid)][str(cid)]['reply_num'] = _visitbook[str(uid)][str(cid)]['reply_num'] + 1
        return True
    else:
        return False
        
def decrease_comment_num(uid):
    """
    방명록에 댓글 삭제 후 답글 갯수를 1 감소시키는 함수

    uid(int) : 해당 프로필 유저의 uid 값
    """
    if str(uid) in _visitbook:
        _visitbook[str(uid)]['comment_num'] = _visitbook[str(uid)]['comment_num'] - 1
        return True
    else:
        return False

def decrease_comment_reply_num(uid, cid):
    """
    방명록 내 댓글에 답글 삭제 후 답글 갯수를 1 감소시키는 함수

    uid(int) : 해당 프로필 유저의 uid 값
    cid(int) : 답글이 달린 댓글의 cid 값
    """
    if str(uid) in _visitbook and str(cid) in _visitbook[str(uid)]:
        _visitbook[str(uid)][str(cid)]['reply_num'] = _visitbook[str(uid)][str(cid)]['reply_num'] - 1
        return True
    else:
        return False

def is_visitbook_exist(uid):
    """
    해당 uid 값을 가진 유저의 방명록 정보가 존재하는지 알려주는 함수
    결과가 있다면 True, 없다면 False 반환

    uid(int) : 찾고자 하는 유저의 uid
    """
    return str(uid) in _visitbook

def is_comment_exist(uid, cid):
    """
    해당 cid 값을 가진 방명록 댓글이 있는지 알려주는 함수
    결과가 있다면 True, 없다면 False 반환

    uid(int) : 찾고자 하는 유저의 uid
    cid(str) : 탐색할 댓글의 cid 값
    """
    return str(uid) in _visitbook and str(cid) in _visitbook[str(uid)]


def is_comment_reply_exist(uid, cid, reply_cid):
    """
    해당 reply_cid 값을 가진 방명록 댓글의 답글이 있는지 알려주는 함수
    결과가 있다면 True, 없다면 False 반환

    uid(int) : 찾고자 하는 유저의 uid
    cid(str) : 답글이 있는 댓글의 cid 값
    reply_cid(str) : 답글의 cid 값
    """
    return str(uid) in _visitbook and str(cid) in _visitbook[str(uid)] and 'reply' in _visitbook[str(uid)][str(cid)] and str(reply_cid) in _visitbook[str(uid)][str(cid)]['reply']

def get_all_visitbook():
    """
    모든 방명록 정보를 받는 함수
    """
    return _visitbook

# 방명록 요청
def get_visitbook(uid):
    """
    한 유저의 방명록 정보를 받는 함수
    
    uid(int) : 해당 프로필 유저의 uid 값
    """
    if str(uid) in _visitbook:
        return _visitbook[str(uid)]
    else:
        return None

    
# 방명록 댓글 요청
def get_comment(uid, cid):
    """
    해당 유저의 방명록 댓글과 그 댓글의 답글 정보를 받는 함수

    uid(int) : 해당 프로필 유저의 uid 값
    cid(int) : 방명록 댓글 cid 값
    """
    if str(uid) in _visitbook and str(cid) in _visitbook[str(uid)]:
        return _visitbook[str(uid)][str(cid)]
    else:
        return None


# 방명록 댓글의 답글 요청
def get_comment_reply(uid, cid, reply_cid):
    """
    해당 유저의 방명록 댓글에 달린 답글의 정보를 받는 함수

    uid(int) : 해당 프로필 유저의 uid 값
    cid(int) : 방명록 댓글 cid 값
    reply_cid(str) : 답글의 cid 값
    """
    if str(uid) in _visitbook and str(cid) in _visitbook[str(uid)] and 'reply' in _visitbook[str(uid)][str(cid)] and str(reply_cid) in _visitbook[str(uid)][str(cid)]['reply']:
        return _visitbook[str(uid)][str(cid)]['reply'][str(reply_cid)]
    else:
        return None

# 댓글 리스트 요청
def get_comment_list(uid):
    """
    한 유저의 방명록 댓글의 리스트를 받는 함수

    return 형식 : 
    [
        {
            'cid': '댓글 cid',
            'comment': '댓글 내용',
            'reply_num': 답글 갯수,
            'timestamp': '타임스탬프',
            'writer_uid': '댓글 작성자 uid'
        },
        ...
    ]

    uid(int) : 해당 프로필 유저의 uid 값
    """
    comment_data = get_visitbook(str(uid)) 

    # 댓글 데이터가 없다면 None 반환
    if comment_data is None:
        print("There's no comment data in " + str(uid) + "'s visitbook.")
        return None

    # 댓글 정보 리스트 반환
    return_list = []
    for cid in comment_data:
        _cid = comment_data[str(cid)]
        return_list.append({
            'writer_uid': _cid['writer_uid'],
            'comment': _cid['comment'],
            'timestamp': _cid['timestamp'],
            'reply_num': _cid['reply_num']
        })
    return_list.reverse()
    return return_list

# 답글 리스트 요청
def get_comment_reply_list(uid, cid):
    """
    방명록 댓글의 답글을 배열로 받는 함수

    return 형식 : 
    [
        {
            'reply_cid': '답글 cid',
            'reply_comment': '답글 내용',
            'timestamp': '타임스탬프',
            'writer_uid': '답글 작성자 uid'
        },
        ...
    ]

    uid(int) : 해당 프로필 유저의 uid 값
    cid(int) : 방명록 댓글 cid 값
    """

    reply_data = None
    if str(uid) in _visitbook and str(cid) in _visitbook[str(uid)] and 'reply' in _visitbook[str(uid)][str(cid)]:
        reply_data = _visitbook[str(uid)][str(cid)]['reply']

    # 답글 데이터가 없으면 None 반환
    if reply_data is None:
        print("No reply comment data in " + str(cid) + " comment.")
        return None
    
    # 답글 데이터가 있다면 리스트로 변환
    for comment_id, data in reply_data.items():
        # 데이터의 value에 cid 정보 삽입
        data['reply_cid'] = comment_id

    # 댓글 정보 리스트 반환
    return_list = list(reply_data.values())
    return_list.reverse()
    return return_list


# 방명록 댓글 갯수 요청
def get_comment_num(uid):
    """
    해당 유저의 방명록에 있는 댓글의 갯수를 받는 함수

    uid(int) : 해당 프로필 유저의 uid 값
    """

    if str(uid) in _visitbook and 'comment_num' in _visitbook[str(uid)]:
        return _visitbook[str(uid)]['comment_num']
    else:
        return 0


# 방명록 답글 갯수 요청
def get_comment_reply_num(uid, cid):
    """
    해당 유저의 방명록 내 댓글에 달린 답글의 갯수를 받는 함수

    uid(int) : 해당 프로필 유저의 uid 값
    cid(int) : 방명록 댓글 cid 값
    """
    if str(uid) in _visitbook and str(cid) in _visitbook[str(uid)] and 'reply_num' in _visitbook[str(uid)][str(cid)]:
        return _visitbook[str(uid)][str(cid)]['reply_num']
    else:
        return 0

# 방명록 댓글 추가
def add_comment(uid, writer_uid, comment, timestamp):
    """
    유저 프로필 내 방명록에 댓글을 남기는 함수
    성공하면 타임스탬프 값을, 실패하면 False 반환
    
    uid(int) : 해당 프로필 유저의 uid 값
    writer_uid(int) : 댓글 작성 유저의 uid 값
    comment(str) : 댓글 내용
    timestamp(str) : 서버 시계 기준 방명록 댓글 추가 시각
    """
    # 댓글 내용이 아무 데이터도 없는 값이면 False 반환
    if comment is None:
        print("Comment value is None.")
        return False

    # DB에 댓글 등록 후 timestamp 반환
    if str(uid) not in _visitbook:
        _visitbook[str(uid)] = {'comment_num': 0}

    _visitbook[str(uid)][str(writer_uid) + timestamp] = {
        'writer_uid': writer_uid,
        'comment': comment,
        'timestamp': timestamp,
        'reply_num': 0
    }

    # 댓글 갯수 1 증가
    increase_comment_num(uid)

    # 추가 완료 후 timestamp 반환
    return timestamp

# 방명록 댓글의 답글 추가
def add_comment_reply(uid, cid, writer_uid, reply_comment, timestamp):
    """
    방명록 댓글에 답글을 남기는 함수
    성공하면 타임스탬프 값을, 실패하면 False 반환
    
    uid(int) : 해당 프로필 유저의 uid 값
    cid(str) : 답글을 달 댓글의 cid 값
    writer_uid(int) : 답글 작성 유저의 uid 값
    reply_comment(str) : 답글 내용 문자열
    timestamp(str) : 서버 시계 기준 방명록 댓글의 답글 추가 시각
    """
    # 답글 내용이 아무 데이터도 없는 값이면 False 반환
    if reply_comment is None:
        print("Comment value is None.")
        return False

    # 해당 방명록 댓글 중 cid와 매칭되는 댓글이 없다면 False 반환
    if is_comment_exist(uid, cid) is False:
        print("Invalid comment ID value.")
        return False
    
    if 'reply' not in _visitbook[str(uid)][str(cid)]:
        _visitbook[str(uid)][str(cid)] = {'reply_num': 0}

    # 모든 값이 유효하다면 답글 DB에 저장
    _visitbook[str(uid)][str(cid)]['reply'][str(writer_uid) + timestamp] = {
        'writer_uid': writer_uid,
        'reply_comment': reply_comment,
        'timestamp': timestamp,
    }

    # 답글 갯수 1 증가
    increase_comment_reply_num(uid, cid)

    # 추가 완료 후 timestamp 반환
    return timestamp

# 방명록 댓글 수정
def modify_comment(uid, cid, writer_uid, modified_comment, timestamp):
    """
    방명록 댓글 내용을 수정하는 함수
    성공하면 타임스탬프 값을, 실패하면 False 반환
    
    uid(int) : 해당 프로필 유저의 uid 값
    cid(str) : 답글을 달 댓글의 cid 값
    writer_uid(int) : 댓글 작성 유저의 uid 값
    modified_comment(str) : 수정할 댓글 내용
    timestamp(str) : 서버 시계 기준 방명록 댓글 수정 시각
    """
    # 수정할 댓글 내용이 아무 데이터도 없는 값이면 False 반환
    if modified_comment is None:
        print("Comment value is None.")
        return False

    # 수정할 방명록 부분 정보를 불러옴
    visitbook_data = get_comment(uid, cid)

    # 해당 방명록 정보가 없다면 False 반환
    if visitbook_data is None:
        print("Invalid comment ID value.")
        return False
    
    # 기존에 해당 댓글을 작성한 유저의 uid가 수정을 시도하는 유저의 uid와 다를 경우 False 반환
    if visitbook_data['writer_uid'] != writer_uid:
        print("Writer uid value is not matched with existing comment writer's uid.")
        return False

    # 모든 값이 유효하다면 DB에 댓글 등록
    _visitbook[str(uid)][str(cid)]['comment'] = modified_comment
    _visitbook[str(uid)][str(cid)]['timestamp'] = timestamp

    # 수정 완료 후 timestamp 반환
    print(str(uid) + "'s visitbook comment " + str(cid) + " modified.")
    return timestamp

# 방명록 댓글의 답글 수정
def modify_comment_reply(uid, cid, reply_cid, writer_uid, modified_reply_comment, timestamp):
    """
    방명록 댓글의 답글 내용을 수정하는 함수
    성공하면 타임스탬프 값을, 실패하면 False 반환
    
    uid(int) : 해당 프로필 유저의 uid 값
    cid(str) : 답글이 존재하는 댓글의 cid 값
    reply_cid(str) : 답글의 cid 값
    modified_comment(str) : 수정할 댓글 내용
    timestamp(str) : 서버 시계 기준 방명록 댓글의 답글 수정 시각
    """
    # 수정할 댓글 내용이 아무 데이터도 없는 값이면 False 반환
    if modified_reply_comment is None:
        print("Reply comment value is None.")
        return False

    # 수정할 방명록 부분 정보를 불러옴
    visitbook_data = get_comment_reply(uid, cid, reply_cid)

    # 해당 방명록 정보가 없다면 False 반환
    if visitbook_data is None:
        print("Invalid reply comment ID value.")
        return False

    # 기존에 해당 답글을 작성한 유저의 uid가 수정을 시도하는 유저의 uid와 다를 경우 False 반환
    if visitbook_data['writer_uid'] != writer_uid:
        print("Writer uid value is not matched with existing reply comment writer's uid.")
        return False

    # 모든 값이 유효하다면 DB에 댓글 등록
    _visitbook[str(uid)][str(cid)]['reply'][reply_cid]['reply_comment'] = modified_reply_comment
    _visitbook[str(uid)][str(cid)]['reply'][reply_cid]['timestamp'] = timestamp

    # 수정 완료 후 timestamp 반환
    print(str(uid) + "'s visitbook comment " + str(cid) + " modified.")
    return timestamp

# 방명록 삭제
def delete_visitbook(uid):
    """
    한 유저의 방명록 정보를 모두 삭제하는 함수
    
    uid(int) : 해당 프로필 유저의 uid 값
    """
    # 해당 uid 유저의 방명록 데이터가 없으면 False 반환
    
    if is_visitbook_exist(uid) is False:
        print("User " + str(uid) + "'s visitbook is not exist.")
        return False
    
    # 해당 유저의 방명록 데이터를 모두 삭제
    del _visitbook[str(uid)]

    # 삭제 완료 후 True 반환
    print("Delete visitbook.(uid : " + str(uid) + ")")
    return True
# 방명록 댓글 삭제
def delete_comment(uid, cid):
    """
    방명록 댓글 내용을 삭제하는 함수
    이 때 해당 댓글에 달린 답글도 모두 삭제된다.
    
    uid(int) : 해당 프로필 유저의 uid 값
    cid(str) : 삭제할 댓글의 cid 값
    """
    # 해당 댓글이 이미 없다면 False 반환

    if is_comment_exist(uid, cid) is False:
        print("Comment " + str(cid) + " is not exist.")
        return False
    
    # 해당 댓글이 있다면 삭제, True 반환
    del _visitbook[str(uid)][str(cid)]

    # 댓글 갯수 1 감소
    decrease_comment_num(uid)

    # 삭제 완료 후 True 반환
    print("Comment " + str(cid) + "in " + str(uid) + "'s visitbook is deleted.")
    return True

# 방명록 댓글의 답글 삭제
def delete_comment_reply(uid, cid, reply_cid):
    """
    방명록 댓글 내용을 삭제하는 함수
    이 때 해당 댓글에 달린 답글도 모두 삭제된다.
    
    uid(int) : 해당 프로필 유저의 uid 값
    cid(str) : 삭제할 답글의 댓글 cid 값
    reply_cid(str) : 삭제할 답글의 cid 값
    """
    # 해당 댓글이 이미 없다면 False 반환

    if is_comment_reply_exist(uid, cid, reply_cid) is False:
        print("Comment reply " + str(reply_cid) + " is not exist.")
        return False
    
    # 해당 댓글이 있다면 삭제, True 반환
    del _visitbook[str(uid)][str(cid)]['reply'][str(reply_cid)]

    # 답글 갯수 1 감소
    decrease_comment_reply_num(uid, cid)

    # 삭제 완료 후 True 반환
    print("Reply comment " + str(reply_cid) + " of comment " + str(cid) + "in " + str(uid) + "'s visitbook is deleted.")
    return True

def save():
    dir = db.reference('VISITBOOK')
    dir.update(_visitbook)