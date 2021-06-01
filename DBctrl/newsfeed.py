from firebase_admin import db
from datetime import date, timedelta

from .follow import get_user_following_uid_list

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
    dir = db.reference('NEWSFEED')
    dir.update({uid: {'nickname': nickname}})

def get_all_newsfeed():
    return db.reference('NEWSFEED').get()

def get_newsfeed_one_uid(uid):
    dir = db.reference('NEWSFEED').child(str(uid))

    return dir.get()

def get_newsfeed_uid(uid):
    lst = get_user_following_uid_list(uid)
    print(lst)
    ret = []
    if lst:
        for follow in lst:
            _newsfeed = get_newsfeed_one_uid(follow)
            if _newsfeed and 'snapshot' in _newsfeed:
                for _newstime in _newsfeed['snapshot']:
                    _ret = {}
                    _ret['timestamp'] = _newstime
                    _ret['uid'] = follow
                    _ret['nickname'] = _newsfeed['nickname']
                    ret.append(_ret)

        ret = sorted(ret, key = (lambda x:x['timestamp']), reverse=True)
        return ret
    else:
        return None

def add_snap(uid, timestamp):
    dir = db.reference('NEWSFEED').child(str(uid)).child('snapshot')
    t = dir.get()
    if t is None:
        t = [timestamp]
    else:
        t.append(timestamp)
    dir = db.reference('NEWSFEED').child(str(uid))
    dir.update({'snapshot': t})

def mod_nick(uid, nickname):
    dir = db.reference('NEWSFEED').child(str(uid))
    if dir.get() is not None:
        dir.update({'nickname': nickname})
        return True
    else:
        return False

def remove_old_newsfeed():
    dir = db.reference('NEWSFEED')
    all_news = dir.get()
    last_day = (date.today() - timedelta(6)).strftime('%Y%m%d')
    for uid in all_news:
        if not 'snapshot' in all_news[uid]:
            continue
        cnt = 0
        for i in range(len(all_news[uid]['snapshot'])):
            if all_news[uid]['snapshot'][i][:8] < last_day:
                cnt = cnt + 1
        all_news[uid]['snapshot'] = all_news[uid]['snapshot'][cnt:]
        _dir = dir.child(uid)
        _dir.update({'snapshot': all_news[uid]['snapshot']})