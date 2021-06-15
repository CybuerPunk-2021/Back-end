from firebase_admin import db
from datetime import date, timedelta

from .follow import get_user_following_uid_list

_newsfeed = db.reference('NEWSFEED').get()

# NEWSFEED 데이터베이스 구조
"""
'NEWSFEED':
{
    'uid':
    {
        'nickname': '닉네임',
        'snapshot': [timestamp1, timestamp2, ...]
    },
    ...
}
"""

# follow 목록을 가져와서
# 내가 follow하는 사람만 다 가져와서
# timestamp로 정렬해서 앞에서부터 짤라서 주기

def make_newsfeed(uid, nickname):
    _newsfeed[str(uid)] = {'nickname': nickname}

def get_all_newsfeed():
    return _newsfeed

def get_newsfeed_one_uid(uid):
    if str(uid) in _newsfeed:
        return _newsfeed[str(uid)]
    else:
        return None

def get_newsfeed_uid(uid):
    lst = get_user_following_uid_list(uid)
    ret = []
    if lst:
        for _follow in lst:
            if str(_follow) in _newsfeed and 'snapshot' in _newsfeed[str(_follow)]:
                for _newstime in _newsfeed[str(_follow)]['snapshot']:
                    _ret = {}
                    _ret['timestamp'] = _newstime
                    _ret['uid'] = _follow
                    _ret['nickname'] = _newsfeed[str(_follow)]['nickname']
                    ret.append(_ret)

        ret = sorted(ret, key = (lambda x:x['timestamp']), reverse=True)
        return ret
    else:
        return None

def add_snap(uid, timestamp):
    if str(uid) in _newsfeed and 'snapshot' in _newsfeed[str(uid)]:
        _newsfeed[str(uid)]['snapshot'].append(timestamp)
    else:
        _newsfeed[str(uid)]['snapshot'] = [timestamp]

def del_snap(uid, timestamp):
    if str(uid) in _newsfeed and 'snapshot' in _newsfeed[str(uid)] and timestamp in _newsfeed[str(uid)]['snapshot']:
        _newsfeed[str(uid)]['snapshot'].remove(timestamp)
        return True
    else:
        return False

def mod_nick(uid, nickname):
    if str(uid) in _newsfeed:
        _newsfeed[str(uid)]['nickname'] = nickname
        return True
    else:
        return False

def delete_user(uid):
    if str(uid) in _newsfeed:
        del _newsfeed[str(uid)]
        return True
    else:
        return False

def remove_old_newsfeed():
    last_day = (date.today() - timedelta(6)).strftime('%Y%m%d')
    for uid in _newsfeed:
        if not 'snapshot' in _newsfeed[uid]:
            continue
        cnt = 0
        for i in range(len(_newsfeed[uid]['snapshot'])):
            if _newsfeed[uid]['snapshot'][i][:8] < last_day:
                cnt = cnt + 1
        _newsfeed[uid]['snapshot'] = _newsfeed[uid]['snapshot'][cnt:]
    save()

def save():
    dir = db.reference('NEWSFEED')
    dir.update(_newsfeed)