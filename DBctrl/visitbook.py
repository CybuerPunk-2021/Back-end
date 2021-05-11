import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from .profile import is_profile_exist
from .etc import timestamp

# VISITBOOK 데이터베이스 구조
"""
'VISITBOOK':
{
    'uid':
    {
        'cid':
        {
            'writer_uid': 댓글 작성자 uid,
            'comment': '댓글 내용',
            'timestamp': '댓글 작성 날짜, 시각',
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
    dir = db.reference('VISITBOOK').child(str(uid))
    comment_data = dir.get()

    # 댓글 데이터가 없으면 None 반환
    if comment_data is None:
        print("No comment data in " + str(uid) + " visitbook.")
        return None
    
    # 댓글 데이터 딕셔너리의 value 값을 리스트에 추가
    comment_list = []
    for comment in comment_data:
        data = comment_data.get(comment)
        # 댓글에 답글이 있다면 data에 답글의 갯수 추가
        if 'reply' in data:
            data['reply_num'] = len(data['reply'])
            del data['reply']
        # 댓글에 답글이 없다면 data에 답글의 갯수가 0이라는 정보 추가
        else:
            data['reply_num'] = 0
        # data에 cid 값 추가
        data['cid'] = comment
        comment_list.append(comment_data.get(comment))

    return comment_list

def get_comment(uid, cid):
    """
    방명록의 코멘트 하나의 정보를 받는 함수

    uid(int) : 해당 프로필 유저의 uid 값
    cid(int) : 방명록 댓글 cid 값
    """
    return db.reference('VISITBOOK').child(str(uid)).child(str(cid)).get()

def get_comment_reply(uid, cid):
    """
    방명록 댓글의 답글을 받는 함수

    uid(int) : 해당 프로필 유저의 uid 값
    cid(int) : 방명록 댓글 cid 값
    """
    dir = db.reference('VISITBOOK').child(str(uid)).child(str(cid)).child('reply')

    # 답글 데이터가 없으면 None 반환
    if dir.get() is None:
        print("No reply comment data in " + str(cid) + " comment.")
        return None
    
    return dir.get()

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
    dir = db.reference('VISITBOOK').child(str(uid)).child(str(cid)).child('reply')
    reply_data = dir.get()

    # 답글 데이터가 없으면 None 반환
    if reply_data is None:
        print("No reply comment data in " + str(cid) + " comment.")
        return None
    
    # 답글 데이터 딕셔너리의 value 값을 리스트에 추가
    reply_list = []
    for reply in reply_data:
        data = reply_data.get(reply)
        # data에 reply_cid 값 추가
        data['reply_cid'] = reply
        reply_list.append(reply_data.get(reply))

    return reply_list

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
    # 방명록 주인인 uid 유저가 프로필 데이터가 없으면 False 반환
    if is_profile_exist(str(uid)) is False:
        print("Visitbook is not exist. Wrong uid value.")
        return False
    
    # 댓글을 남기는 유저의 uid 값이 올바른 값이 아니라면 False 반환
    if is_profile_exist(str(writer_uid)) is False:
        print("There's no writer's uid user data in DB.")
        return False
    
    # 댓글 내용이 아무 데이터도 없는 값이면 False 반환
    if comment is None:
        print("Comment value is None.")
        return False

    # 모든 값이 유효하다면 DB에 댓글 등록
    dir = db.reference('VISITBOOK').child(str(uid))
    new_comment = dir.push()
    new_comment.set({
        'writer_uid': writer_uid,
        'comment': comment,
        'timestamp': timestamp,
        'reply': None
    })
    print("Add comment in " + str(uid) + "`s visitbook.")
    return new_comment.child('timestamp').get()

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
    # 방명록 주인인 uid 유저가 프로필 데이터가 없으면 False 반환
    if is_profile_exist(str(uid)) is False:
        print("Visitbook is not exist. Wrong uid value.")
        return False

    # 해당 uid 유저의 방명록 데이터가 없으면 False 반환
    dir = db.reference('VISITBOOK').child(str(uid))
    if dir.get() is None:
        print("User " + str(uid) + "`s visitbook is not exist.")
        return False

    # 해당 방명록 댓글 중 cid와 매칭되는 댓글이 없다면 False 반환
    dir = db.reference('VISITBOOK').child(str(uid)).child(str(cid))
    if dir.get() is None:
        print("Invalid comment ID value.")
        return False
    
    # 모든 값이 유효하다면 답글 DB에 저장
    new_reply = dir.child('reply').push()
    new_reply.set({
        'writer_uid': writer_uid,
        'reply_comment': reply_comment,
        'timestamp': timestamp,
    })
    return new_reply.child('timestamp').get()

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
    # 방명록 주인인 uid 유저가 프로필 데이터가 없으면 False 반환
    if is_profile_exist(str(uid)) is False:
        print("Visitbook is not exist. Wrong uid value.")
        return False

    # 해당 uid 유저의 방명록 데이터가 없으면 False 반환
    dir = db.reference('VISITBOOK').child(str(uid))
    if dir.get() is None:
        print("User " + str(uid) + "`s visitbook is not exist.")
        return False

    # 해당 cid 방명록이 없다면 False 반환
    dir = db.reference('VISITBOOK').child(str(uid)).child(str(cid))
    if dir.get() is None:
        print("Invalid comment ID value.")
        return False
    
    # 기존에 해당 댓글을 작성한 유저의 uid가 수정을 시도하는 유저의 uid와 다를 경우 False 반환
    if dir.child('writer_uid').get() != writer_uid:
        print("Writer uid value is not matched with existing comment writer's uid.")
        return False

    # 수정할 댓글 내용이 아무 데이터도 없는 값이면 False 반환
    if modified_comment is None:
        print("Comment value is None.")
        return False

    # 모든 값이 유효하다면 DB에 댓글 등록
    dir.update({
        'comment': modified_comment,
        'timestamp': timestamp
    })
    print(str(uid) + "`s visitbook comment " + str(cid) + " modified.")
    return dir.child('timestamp').get()

# 방명록 댓글의 답글 수정
def modify_comment_reply(uid, cid, reply_cid, modified_reply_comment, timestamp):
    """
    방명록 댓글의 답글 내용을 수정하는 함수
    성공하면 타임스탬프 값을, 실패하면 False 반환
    
    uid(int) : 해당 프로필 유저의 uid 값
    cid(str) : 답글을 달 댓글의 cid 값
    modified_comment(str) : 수정할 댓글 내용
    timestamp(str) : 서버 시계 기준 방명록 댓글의 답글 수정 시각
    """
    # 방명록 주인인 uid 유저가 프로필 데이터가 없으면 False 반환
    if is_profile_exist(str(uid)) is False:
        print("Visitbook is not exist. Wrong uid value.")
        return False

    # 해당 uid 유저의 방명록 데이터가 없으면 False 반환
    dir = db.reference('VISITBOOK').child(str(uid))
    if dir.get() is None:
        print("User " + str(uid) + "`s visitbook is not exist.")
        return False
    
    # 해당 cid 방명록이 없다면 False 반환
    dir = db.reference('VISITBOOK').child(str(uid)).child(str(cid))
    if dir.get() is None:
        print("Invalid comment ID value.")
        return False

    # 해당 reply_cid와 맞는 답글 데이터가 없는 경우 False 반환 
    dir = db.reference('VISITBOOK').child(str(uid)).child(str(cid)).child('reply').child(str(reply_cid))
    if dir.get() is None:
        print("Invalid reply comment ID value.")
        return False

    # 기존에 해당 답글을 작성한 유저의 uid가 수정을 시도하는 유저의 uid와 다를 경우 False 반환
    if dir.child('writer_uid').get() != writer_uid:
        print("Writer uid value is not matched with existing reply comment writer's uid.")
        return False

    # 수정할 댓글 내용이 아무 데이터도 없는 값이면 False 반환
    if modified_reply_comment is None:
        print("Reply comment value is None.")
        return False

    # 모든 값이 유효하다면 DB에 댓글 등록
    dir.update({
        'reply_comment': modified_reply_comment,
        'timestamp': timestamp
    })
    print(str(uid) + "`s visitbook comment " + str(cid) + " modified.")
    return dir.child('timestamp').get()

def delete_comment(uid, cid):
    """
    방명록 댓글 내용을 삭제하는 함수
    이 때 해당 댓글에 달린 답글도 모두 삭제된다.
    
    uid(int) : 해당 프로필 유저의 uid 값
    cid(str) : 삭제할 댓글의 cid 값
    """
    # 해당 uid 유저의 방명록 데이터가 없으면 False 반환
    dir = db.reference('VISITBOOK').child(str(uid))
    if dir.get() is None:
        print("User " + str(uid) + "`s visitbook is already not exist.")
        return False

    # 해당 댓글이 이미 없다면 False 반환
    dir = db.reference('VISITBOOK').child(str(uid)).child(str(cid))
    if dir.get() is None:
        print("Comment " + str(cid) + " is not exist.")
        return False
    
    # 해당 댓글이 있다면 삭제, True 반환
    dir.delete()
    print("Comment " + str(cid) + "in " + str(uid) + "`s visitbook is deleted.")
    return True

def delete_visitbook(uid):
    """
    한 유저의 방명록 정보를 모두 삭제하는 함수
    
    uid(int) : 해당 프로필 유저의 uid 값
    """
    # 해당 uid 유저의 방명록 데이터가 없으면 False 반환
    dir = db.reference('VISITBOOK').child(str(uid))
    if dir.get() is None:
        print("User " + str(uid) + "`s visitbook is not exist.")
        return False
    
    # 해당 유저의 방명록 데이터를 모두 삭제
    dir.delete()
    print("Delete visitbook.(uid : " + str(uid) + ")")
    return True
