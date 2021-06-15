from firebase_admin import db

import time

_profile = db.reference('PROFILE').get()
if not _profile:
    _profile = {}

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
        'profile_image_size': 프로필 이미지 사이즈,
        'bg_image_time': '가장 최근에 배경 이미지를 변경한 시각',
        'bg_image_size': 배경 이미지 사이즈
    }
}
"""

def increase_following_num(uid):
    if str(uid) in _profile:
        _profile[str(uid)]['num_following'] = _profile[str(uid)]['num_following'] + 1
        return True
    else:
        return False

def increase_follower_num(uid):
    if str(uid) in _profile:
        _profile[str(uid)]['num_follower'] = _profile[str(uid)]['num_follower'] + 1
        return True
    else:
        return False

def decrease_following_num(uid):
    if str(uid) in _profile:
        _profile[str(uid)]['num_following'] = _profile[str(uid)]['num_following'] - 1
        return True
    else:
        return False

def decrease_follower_num(uid):
    if str(uid) in _profile:
        _profile[str(uid)]['num_follower'] = _profile[str(uid)]['num_follower'] - 1
        return True
    else:
        return False

def is_profile_exist(uid):
    """
    해당 uid 값을 가진 유저가 존재하는지 알려주는 함수
    해당 uid의 유저가 있다면 True, 없다면 False 반환

    uid(int) : 찾고자 하는 유저의 uid
    """
    if str(uid) in _profile:
        return True
    else:
        return False

def is_profile_nickname_exist(nickname):
    """
    DB 상에 현재 입력한 닉네임을 가진 유저가 있는지 확인하는 함수
    DB에 해당 닉네임의 유저가 있으면 True, 없으면 False 반환

    nickname(str) : 찾고자 하는 닉네임 값
    """
    for uid in _profile:
        if _profile[uid]['nickname'] == nickname:
            return True
    return False

def get_all_profile():
    """
    DB에 있는 모든 유저의 프로필 내용을 불러오는 함수
    """
    return _profile

# 유저 프로필 요청
def get_profile(uid):
    """
    유저의 프로필 내용을 불러오는 함수
    유저 데이터가 존재하면 해당 프로필 정보를 반환, 없으면 None 반환

    uid(int) : 해당 프로필 유저의 uid
    """
    if str(uid) in _profile:
        return _profile[str(uid)]
    else:
        return None

# 프로필 닉네임 요청
def get_profile_nickname(uid):
    """
    해당 유저의 닉네임을 받는 함수

    uid(int) : 해당 프로필 유저의 uid
    """
    if str(uid) in _profile and 'nickname' in _profile[str(uid)]:
        return _profile[str(uid)]['nickname']
    else:
        return None

# 프로필 이미지 최근 수정 시각 요청
def get_profile_image_time(uid):
    """
    제일 최근 유저의 프로필 이미지를 변경한 시각을 얻는 함수
    uid(int) : 해당 프로필 유저의 uid
    """
    if str(uid) in _profile and 'profile_image_time' in _profile[str(uid)]:
        return _profile[str(uid)]['profile_image_time']
    else:
        return ""

def get_profile_image_size(uid):
    """
    제일 최근 유저의 프로필 이미지 사이즈를 얻는 함수
    uid(int) : 해당 프로필 유저의 uid
    """
    if str(uid) in _profile and 'profile_image_size' in _profile[str(uid)]:
        return _profile[str(uid)]['profile_image_size']
    else:
        return 52854

def get_profile_image_time_list(uid):
    timestamp_list = []

    for _uid in uid:
        if str(_uid) in _profile and 'profile_image_time' in _profile[str(_uid)]:
            timestamp_list.append(_profile[str(_uid)]['profile_image_time'])
        else:
            timestamp_list.append("")
    return timestamp_list

def get_profile_image_size_list(uid):
    size_list = []

    for _uid in uid:
        if str(_uid) in _profile and 'profile_image_size' in _profile[str(_uid)]:
            size_list.append(_profile[str(_uid)]['profile_image_size'])
        else:
            size_list.append(52854)
    return size_list

# 프로필 배경 이미지 최근 수정 시각 요청
def get_profile_background_image_time(uid):
    """
    제일 최근 유저의 프로필 배경 이미지를 변경한 시각을 얻는 함수
    uid(int) : 해당 프로필 유저의 uid
    """
    if str(uid) in _profile and 'bg_image_time' in _profile[str(uid)]:
        return _profile[str(uid)]['bg_image_time']
    else:
        return ""

def get_profile_background_image_size(uid):
    """
    제일 최근 유저의 배경 이미지 사이즈를 얻는 함수
    uid(int) : 해당 배경 유저의 uid
    """
    if str(uid) in _profile and 'bg_image_size' in _profile[str(uid)]:
        return _profile[str(uid)]['bg_image_size']
    else:
        return 462393

# 팔로잉 수 요청
def get_following_num(uid):
    """
    유저의 팔로잉 수를 받는 함수

    uid(str) : 유저의 uid
    """
    if str(uid) in _profile:
        return _profile[str(uid)]['num_following']
    else:
        return 0

# 팔로워 수 요청
def get_follower_num(uid):
    """
    유저의 팔로워 수를 받는 함수

    uid(str) : 유저의 uid
    """
    if str(uid) in _profile:
        return _profile[str(uid)]['num_follower']
    else:
        return 0

# 프로필 검색
def search_profile(nickname, from_uid):
    """
    해당 문자열을 포함하는 닉네임을 가진 유저를 검색하는 함수
    검색한 유저의 uid, 닉네임 정보 리스트를 반환한다.

    nickname(str) : 닉네임 검색 키워드
    """
    # 검색 키워드가 아무 값도 없는 경우라면 그대로 넘어감
    if nickname == "":
        return []
    
    return_list = []
    for uid in _profile:
        if nickname.upper() in _profile[uid]['nickname_upper']:
            return_list.append({'uid': int(uid), 'nickname': _profile[uid]['nickname']})

    return return_list

# 프로필 생성
def make_profile(uid, login_id, nickname, timestamp):
    """
    해당 uid 값으로 초기 프로필 데이터를 세팅하는 함수
    생성에 성공하면 True, 실패하면 False 반환

    uid(str) : 해당 프로필 유저의 uid
    login_id(str) : 해당 프로필 유저의 로그인 아이디
    """
    if str(uid) in _profile:
        return False
    
    # 현재 DB상에 같은 uid 값이 없으면 진행
    _profile[str(uid)] = {
        'login_id': str(login_id),
        'login_id_upper': str(login_id).upper(),
        'nickname': str(nickname),
        'nickname_upper': str(nickname).upper(),
        'introduction': 'Hello',
        'num_follower': 0,
        'num_following': 0
    }
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
    # 이미 다른 유저가 사용 중인 닉네임이라면 False 반환
    if is_profile_nickname_exist(new_name) is True:
        print("Already used nickname value.")
        return False

    # PROFILE document에 nickname 값 변경
    if str(uid) in _profile:
        _profile[str(uid)]['nickname'] = new_name
        _profile[str(uid)]['nickname_upper'] = new_name.upper()
        return True
    return False

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
    if str(uid) not in _profile:
        print("Invalid UID value.")
        return False

    # 소개글 수정 후 True 반환\
    _profile[str(uid)]['introduction'] = new_intro
    return True

# 프로필 이미지 최근 수정 시각 변경
def modify_profile_image_time(uid, timestamp):
    """
    제일 최근 프로필 이미지를 수정한 시각을 변경하는 함수
    
    uid(int) : 해당 프로필 유저의 uid
    timestamp(str) : 프로필 이미지를 변경한 시각
    """
    if str(uid) in _profile:
        _profile[str(uid)]['profile_image_time'] = timestamp

def modify_profile_image_size(uid, size):
    """
    제일 최근 프로필 이미지의 사이즈를 변경하는 함수

    uid(int) : 해당 프로필 유저의 uid
    size(int) : 프로필 이미지의 사이즈
    """
    if str(uid) in _profile:
        _profile[str(uid)]['profile_image_size'] = size
    
# 프로필 배경 이미지 최근 수정 시각 변경
def modify_profile_background_image_time(uid, timestamp):
    """
    서버에 유저의 변경된 프로필 배경 이미지 저장 후 이미지 파일 경로를 수정하는 함수

    uid(int) : 해당 프로필 유저의 uid
    timestamp(str) : 프로필 배경 이미지를 변경한 시각
    """
    if str(uid) in _profile:
        _profile[str(uid)]['bg_image_time'] = timestamp

def modify_profile_background_image_size(uid, size):
    """
    제일 최근 배경 이미지의 사이즈를 변경하는 함수

    uid(int) : 해당 프로필 유저의 uid
    size(int) : 배경 이미지의 사이즈
    """
    if str(uid) in _profile:
        _profile[str(uid)]['profile_bg_size'] = size

# 회원탈퇴 시 프로필 데이터 삭제
def delete_profile(uid):
    """
    유저의 프로필 정보를 삭제
    삭제를 성공하면 True, 실패하면 False를 반환

    login_id(str) : 유저의 로그인 아이디
    """
    # 현재 DB상에 해당 uid의 데이터가 없으면 중단
    if is_profile_exist(uid) is False:
        print("There's no UID in PROFILE DB.")
        return False

    # DB에서 삭제
    login_id = _profile[str(uid)]['login_id']
    del _profile[str(uid)]

    print("Delete profile.(uid : " + str(uid) + ", login ID : " + str(login_id) + ")")
    return True

def save():
    dir = db.reference('PROFILE')
    dir.update(_profile)