from firebase_admin import db

from .snapshot import update_profile_snapshot_preview


# PROFILE 데이터베이스 구조
"""
'PROFILE':
{
    'uid':
    {
        'introduction': '간단 소개글',
        'login_id': 'USERINFO의 로그인 아이디',
        'login_id_upper': 'USERINFO의 로그인 아이디 색인용 대문자 버전',
        'nickname': '닉네임',
        'nickname_upper': '닉네임 색인용 대문자 버전',
        'num_follower': 팔로워 수,
        'num_following': 팔로잉 수,
        'profile_image_time': '가장 최근에 프로필 이미지를 변경한 시각',
        'bg_image_time': '가장 최근에 배경 이미지를 변경한 시각',
        'snapshot_info':
        {
            'snapshot_intro': '스냅샷 코멘트',
            'like_num': 스냅샷 좋아요 수,
            'timestamp': '스냅샷 생성 시기',
        }
    }
}
"""

def is_profile_exist(uid):
    """
    해당 uid 값을 가진 유저가 존재하는지 알려주는 함수
    해당 uid의 유저가 있다면 True, 없다면 False 반환

    uid(int) : 찾고자 하는 유저의 uid
    """
    dir = db.reference('PROFILE').child(str(uid))
    return dir.get() is not None

def is_profile_nickname_exist(nickname):
    """
    DB 상에 현재 입력한 닉네임을 가진 유저가 있는지 확인하는 함수
    DB에 해당 닉네임의 유저가 있으면 True, 없으면 False 반환

    nickname(str) : 찾고자 하는 닉네임 값
    """
    dir = db.reference('PROFILE')
    founded_info = dir.order_by_child('nickname').equal_to(nickname).get()

    return len(founded_info) > 0

def get_all_profile():
    """
    DB에 있는 모든 유저의 프로필 내용을 불러오는 함수
    """
    return db.reference('PROFILE').get()

# 유저 프로필 요청
def get_profile(uid):
    """
    유저의 프로필 내용을 불러오는 함수
    유저 데이터가 존재하면 해당 프로필 정보를 반환, 없으면 None 반환

    uid(int) : 해당 프로필 유저의 uid
    """
    if is_profile_exist(str(uid)) is False:
        return None
    
    dir = db.reference('PROFILE').child(str(uid))
    
    # 유저의 프로필 내 최신 스냅샷 정보 동기화
    update_profile_snapshot_preview(uid)

    return dir.get()

# 프로필 닉네임 요청
def get_profile_nickname(uid):
    """
    해당 유저의 닉네임을 받는 함수

    uid(int) : 해당 프로필 유저의 uid
    """
    return db.reference('PROFILE').child(str(uid)).child('nickname').get()
# 프로필 이미지 최근 수정 시각 요청
def get_profile_image_time(uid):
    """
    제일 최근 유저의 프로필 이미지를 변경한 시각을 얻는 함수
    uid(int) : 해당 프로필 유저의 uid
    """
    return db.reference('PROFILE').child(str(uid)).child('profile_image_time').get()
# 프로필 배경 이미지 최근 수정 시각 요청
def get_profile_background_image_time(uid):
    """
    제일 최근 유저의 프로필 배경 이미지를 변경한 시각을 얻는 함수
    uid(int) : 해당 프로필 유저의 uid
    """
    return db.reference('PROFILE').child(str(uid)).child('bg_image_time').get()
# 팔로잉 수 요청
def get_following_num(uid):
    """
    유저의 팔로잉 수를 받는 함수

    uid(str) : 유저의 uid
    """
    return db.reference('PROFILE').child(str(uid)).child('num_following').get() or 0
# 팔로워 수 요청
def get_follower_num(uid):
    """
    유저의 팔로워 수를 받는 함수

    uid(str) : 유저의 uid
    """
    return db.reference('PROFILE').child(str(uid)).child('num_follower').get() or 0

def search_profile_using_nickname(nickname):
    """
    해당 문자열을 포함하는 닉네임을 가진 유저를 검색하는 함수

    nickname(str) : 닉네임 검색 키워드
    """
    data = db.reference('PROFILE').order_by_child('nickname_upper').start_at(str(nickname.upper())).end_at(str(nickname.upper()) + '\uf8ff').get() or []
    return list(data)
def search_profile_using_login_id(login_id):
    """
    해당 문자열을 포함하는 로그인 아이디를 가진 유저를 검색하는 함수

    login_id(str) : 로그인 아이디 검색 키워드
    """
    data = db.reference('PROFILE').order_by_child('login_id_upper').start_at(str(login_id.upper())).end_at(str(login_id.upper()) + '\uf8ff').get() or []
    return list(data)
# 프로필 검색
def search_profile(input_string):
    """
    해당 문자열을 포함하는 닉네임, 로그인 아이디를 가진 유저를 검색하는 함수
    닉네임 검색 결과, 로그인 아이디 검색 결과를 통해 uid 리스트를 반환한다.

    input_string(str) : 검색 키워드 문자열
    """
    return list(set(search_profile_using_nickname(input_string) + search_profile_using_login_id(input_string)))

def make_profile(uid, login_id, nickname, timestamp):
    """
    해당 uid 값으로 초기 프로필 데이터를 세팅하는 함수
    생성에 성공하면 True, 실패하면 False 반환

    uid(str) : 해당 프로필 유저의 uid
    login_id(str) : 해당 프로필 유저의 로그인 아이디
    """
    # 현재 DB상에 같은 uid 값이 있으면 중단
    if get_profile(str(uid)) is not None:
        print("Already exist same UID.")
        return False
    
    # 현재 DB상에 같은 uid 값이 없으면 진행
    dir = db.reference('PROFILE').child(str(uid))
    dir.set({
        'login_id': str(login_id),
        'login_id_upper': str(login_id).upper(),
        'nickname': str(nickname),
        'nickname_upper': str(nickname).upper(),
        'introduction': 'Hello',
        'num_follower': 0,
        'num_following': 0,
        'profile_image_time': timestamp,
        'bg_image_time': timestamp,
    })
    print("Setting " + login_id + " account's profile success.")
    return True

# 닉네임 변경
def modify_nickname(uid, new_name):
    """
    프로필 닉네임을 수정하는 함수
    수정을 성공하면 True, 실패하면 False 반환

    uid(str) : 해당 프로필 유저의 uid
    new_name(str) : 변경할 닉네임 정보
    """
    dir = db.reference('PROFILE').child(str(uid))
    # 유효한 유저의 uid 값이 아니면 False 반환
    if dir.get() is None:
        print("Invalid UID value.")
        return False

    # 이미 다른 유저가 사용 중인 닉네임이라면 False 반환
    if is_profile_nickname_exist(new_name) is True:
        print("Already used nickname value.")
        return False

    # PROFILE document에 nickname 값 변경
    dir.update({
        'nickname': new_name,
        'nickname_upper': new_name.upper()
        })
    
    # NEWSFEED document에 nickname 값 변경
    dir = db.reference('NEWSFEED').child(str(uid))
    dir.update({'nickname': new_name})

    return True

# 간단 소개글 변경
def modify_introduction(uid, new_intro):
    """
    프로필 간단 소개글을 수정하는 함수
    수정을 성공하면 True, 실패하면 False 반환

    uid(str) : 해당 프로필 유저의 uid
    new_intro(str) : 변경할 간단 소개글 정보
    """
    dir = db.reference('PROFILE').child(str(uid))
    # 유효한 유저의 uid 값이 아니면 False 반환
    if dir.get() is None:
        print("Invalid UID value.")
        return False

    dir.update({'introduction':new_intro})
    return True

# 프로필 이미지 최근 수정 시각 변경
def modify_profile_image_time(uid, timestamp):
    """
    제일 최근 프로필 이미지를 수정한 시각을 변경하는 함수
    
    uid(int) : 해당 프로필 유저의 uid
    timestamp(str) : 프로필 이미지를 변경한 시각
    """
    dir = db.reference('PROFILE').child(str(uid))
    dir.update({'profile_image_time': timestamp})

# 프로필 배경 이미지 최근 수정 시각 변경
def modify_profile_background_image_time(uid, timestamp):
    """
    서버에 유저의 변경된 프로필 배경 이미지 저장 후 이미지 파일 경로를 수정하는 함수

    uid(int) : 해당 프로필 유저의 uid
    timestamp(str) : 프로필 배경 이미지를 변경한 시각
    """
    dir = db.reference('PROFILE').child(str(uid))
    dir.update({'bg_image_time': timestamp})

def delete_profile(uid):
    """
    유저의 프로필 정보를 삭제
    삭제를 성공하면 True, 실패하면 False를 반환

    login_id(str) : 유저의 로그인 아이디
    """
    # 현재 DB상에 해당 uid의 데이터가 없으면 중단
    if get_profile(uid) is None:
        print("There's no UID in PROFILE DB.")
        return False

    # DB에서 삭제
    dir = db.reference('PROFILE').child(str(uid))
    loginID = dir.child('login_id').get()
    dir.delete()

    print("Delete profile.(uid : " + str(uid) + ", login ID : " + str(loginID) + ")")
    return True
