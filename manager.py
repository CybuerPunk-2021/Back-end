from datetime import datetime
from DBctrl import *
from sendEmail import signup_send_mail, modify_pw_send_mail
import json
import os.path
from os import getcwd
import traceback

email_auth = {} # dict to save signup data

def manage(data, sck, addr): # manage function
    socket = (sck, addr) # make tuple to save socket data
    try:
        act = data['action'] # 
        if act not in manage_list:
            send({'action': 'wrong action format'}, socket)
            return
        start = datetime.now()
        manage_list[act](data, socket)
        end = datetime.now()
        print('TIME: ' + str(end - start))
        log.add_log(get_timestamp(), {'type': 'receive', 'content': data}, addr) # write log
    except ConnectionResetError:
        raise ConnectionResetError()
    except Exception as e:
        send({'action': 'wrong msg format'}, socket)
        traceback.print_exc()
        log.add_error_log(get_timestamp(), {'content': data, 'error_type': str(type(e)) + " : " + str(e)}, addr)
    return
'''
def profile_img_request_size(data, socket):
    uid = data['uid']
    path = '../data/img/profile/' + str(data['uid'])

    if not os.path.isfile(path):
        path = '../data/img/profile/default.png'

    f = open(path, 'rb')
    img = f.read()
    f.close()
    ret = {'action': 'profile_img_request_size', 'size': len(img), 'timestamp': profile.get_profile_image_time(data['uid'])}
    send(ret, socket)
    try:
        data = socket[0].recv(1024).decode()
        data = data.replace("'", "\"")
        data = json.loads(data)
        if data['action'] == 'profile_img_request' and data['uid'] == uid:
            socket[0].sendall(img)
        else:
            send({'action': 'wrong uid'}, socket)
    except Exception as e:
        send({'action': 'wrong msg format'}, socket)
        traceback.print_exc()
        return

def profile_img_update_size(data, socket):
    uid = data['uid']
    size = int(data['size'])
    t = get_timestamp()
    ret = {'action': 'profile_img_update_size', 'timestamp': t}
    send(ret, socket)
    try:
        path = '../data/img/profile/' + str(data['uid'])
        f = open(path, 'wb')
        
        d = socket[0].recv(size)
        f.write(d)
        f.close()
        ret = {'action': 'profile_img_update', 'type': 'True'}
        profile.modify_profile_image_time(data['uid'], t)
    except Exception as e:
        traceback.print_exc()
        ret = {'action': 'profile_img_update', 'type': 'False'}
    send(ret, socket)
'''
def signup(data, socket):
    res = userinfo.check_id_nickname_dup(data['id'], data['nickname'])

    for ea in email_auth.keys():
        if data['id'] == ea[0] or data['nickname'] == ea[1]:
            res = -1

    if res == -1:
        ret = {'action':'dup id'}
        send(ret, socket)
        return
    elif res == -2:
        ret = {'action': 'dup nick'}
        send(ret, socket)
        return
    elif res == True:
        email_auth[(data['id'], data['nickname'])] = signup_sendEmail(data['email'])
        ret = {'action': 'email send'}
    send(ret, socket)
    try:
        while True:
            auth = socket[0].recv(1024)
            auth = auth.decode()
            auth = auth.replace("'", "\"")
            auth = json.loads(auth)
            print(str(auth)) # log
            if auth['action'] == 'email auth':
                if email_auth[(data['id'], data['nickname'])] == auth['auth']:
                    uid = userinfo.make_userinfo(data['id'], data['pw'], data['email'], data['nickname'])
                    profile.make_profile(uid, data['id'], data['nickname'], get_timestamp())
                    newsfeed.make_newsfeed(uid, data['nickname'])
                    ret = {'action': 'email auth', 'auth': 'True'}
                    send(ret, socket)
                    del(email_auth[(data['id']), data['nickname']])
                    
                    userinfo.save()
                    profile.save()
                    newsfeed.save()

                    break
                else:
                    ret = {'action': 'email auth', 'auth': 'False'}
                    send(ret, socket)
            else:
                send({'action': 'wrong action'}, socket)
                del(email_auth[(data['id']), data['nickname']])
                break
    except ConnectionResetError:
        del(email_auth[(data['id']), data['nickname']])
        raise ConnectionResetError()
    except Exception as e:
        del(email_auth[(data['id']), data['nickname']])
        raise e

def login(data, socket):
    id = data['id']
    pw = data['pw']
    res = userinfo.login(id, pw)
    if not res:
        ret = {'action': 'False'}
    else:
        snap = snapshot.get_user_latest_snapshot(res[1])
        ret = {'action':'True', 'nickname': res[0], 'uid': int(res[1]), 'email': res[2]}
        if snap:
            ret['timestamp'] = snap['timestamp']
        else:
            ret['timestamp'] = ""
    send(ret, socket)

def get_home(data, socket):
    refresh_num = 4
    res = newsfeed.get_newsfeed_uid(data['uid'])
    if res:
        res = res[data['count'] * refresh_num: (data['count'] + 1) * refresh_num]
        for snap in res:
            _snap = snapshot.get_snapshot(snap['uid'], snap['timestamp'])
            snap['snapshot_intro'] = _snap['snapshot_intro']
            snap['size'] = snapshot.get_snapshot_size(snap['uid'], snap['timestamp'])
            if 'like_user' in _snap:
                snap['like'] = str(data['uid'] in _snap['like_user'])
                snap['like_num'] = len(_snap['like_user'])
            else:
                snap['like'] = "False"
                snap['like_num'] = 0
        ret = {'action': 'homeinfo', 'info': res}
    else:
        ret = {'action': 'homeinfo', 'info': []}
    send(ret, socket)
    return

def profile_info(data, socket):
    res = profile.get_profile(data['uid'])
    if not res:
        send({'action': 'profile_info', 'follower': 0, 'self_intro': "", 'snapshot_info': {}}, socket)
    else:
        ret = {'action': 'profile_info', 'follower': res['num_follower'], 'self_intro': res['introduction']}
        snap = snapshot.get_user_latest_snapshot(data['uid'])
        if snap:
            snap['size'] = snapshot.get_snapshot_size(data['uid'], snap['timestamp'])
            if 'like_user' in snap:
                snap['like_num'] = len(snap['like_user'])
                del snap['like_user']
            else:
                snap['like_num'] = 0
        else:
            snap = {'timestamp': "", 'like_num': 0, 'snapshot_intro': "", 'size': 0}
        ret['snapshot_info'] = snap

        send(ret, socket)

def get_follower(data, socket):
    res = follow.get_user_follower_uid_list(data['uid'])
    result = []

    if res:
        for r in res:
            tmp = {'uid': r}
            tmp['nickname'] = profile.get_profile_nickname(r)
            result.append(tmp)
        ret = {'action': 'follower', 'follower': result}
    else:
        ret = {'action': 'follower', 'follower': []}
    send(ret, socket)

def get_following(data, socket):
    res = follow.get_user_following_uid_list(data['uid'])
    result = []

    if res:
        for r in res:
            tmp = {'uid': r}
            tmp['nickname'] = profile.get_profile_nickname(r)
            result.append(tmp)
        ret = {'action': 'following', 'following': result}
    else:
        ret = {'action': 'following', 'following': []}
    send(ret, socket)

def add_follow(data, socket):
    if follow.follow_user(data['from_uid'], data['to_uid'], get_timestamp()):
        ret = {'action': 'OK'}
    else:
        ret = {'action': 'ALREADY'}
    send(ret, socket)
    follow.save()
    profile.save()
    
def del_follow(data, socket):
    if follow.unfollow_user(data['from_uid'], data['to_uid']):
        ret = {'action': 'OK'}
    else:
        ret = {'action': 'ALREADY'}
    send(ret, socket)
    follow.save()
    profile.save()

def mod_nick(data, socket):
    if profile.modify_nickname(data['uid'], data['nickname']):
        newsfeed.mod_nick(data['uid'], data['nickname'])
        ret = {'action': 'nickname_ok'}
    else:
        ret = {'action': 'dup nick'}
    send(ret, socket)
    profile.save()
    newsfeed.save()

def mod_email(data, socket):
    try:
        email_auth[data['uid']] = signup_sendEmail(data['email'])
        ret = {'action': 'email_send'}
    except:
        ret = {'action': 'err'}
    send(ret, socket)

    try:
        while True:
            auth = socket[0].recv(1024)
            auth = auth.decode()
            auth = auth.replace("'", "\"")
            auth = json.loads(auth)
            if auth['action'] == 'email auth':
                if email_auth[data['uid']] == auth['auth']:
                    userinfo.modify_email(userinfo.get_login_id_using_uid(data['uid']), data['email'])
                    ret = {'action': 'email auth', 'auth': 'True'}
                    send(ret, socket)
                    del(email_auth[data['uid']])
                    userinfo.save()
                    break
                else:
                    ret = {'action': 'email auth', 'auth': 'False'}
                    send(ret, socket)
            else:
                send({'action': 'wrong action'}, socket)
                del(email_auth[data['uid']])
                break
    except ConnectionResetError:
        del(email_auth[data['uid']])
        raise ConnectionResetError()
    except Exception as e:
        del(email_auth[data['uid']])
        raise e
    


def mod_pw(data, socket):
    if userinfo.modify_password_using_uid(data['uid'], data['pw'], data['new_pw']):
        ret = {'action': 'pw_ok'}
    else:
        ret = {'action': 'err'}
    send(ret, socket)
    userinfo.save()

def mod_intro(data, socket):
    if profile.modify_introduction(data['uid'], data['introduce']):
        ret = {'action': 'introduce_ok'}
    else:
        ret = {'action': 'err'}
    send(ret, socket)
    profile.save()

def mod_snapdesc(data, socket):
    if snapshot.modify_snapshot_intro(data['uid'], data['timestamp'], data['introduce']):
        ret = {'action': 'description_ok'}
    else:
        ret = {'action': 'err'}
    send(ret, socket)
    snapshot.save()

def del_snapshot(data, socket):
    if snapshot.delete_snapshot(data['uid'], data['timestamp']):
        newsfeed.del_snap(data['uid'], data['timestamp'])
        ret = {'action': 'ok'}
    else:
        ret = {'action': 'err'}
    send(ret, socket)
    snapshot.save()
    newsfeed.save()

def like_snapshot(data, socket):
    if data['type'] == 'add':
        if snapshot.like_snapshot(data['to_uid'], data['from_uid'], data['timestamp']):
            ret = {'action': 'ok'}
        else:
            ret = {'action': 'err'}
    elif data['type'] == 'delete':
        if snapshot.unlike_snapshot(data['to_uid'], data['from_uid'], data['timestamp']):
            ret = {'action': 'ok'}
        else:
            ret = {'action': 'err'}
    else:
        ret = {'action': 'like snapshot err'}
    send(ret, socket)
    snapshot.save()

def get_snapshot_item_list(data, socket):
    res = snapshot.get_snapshot_item(data['uid'], data['timestamp'])
    if res:
        ret = {'action': 'snapshot_roominfo', 'item_list': res}
    else:
        ret = {'action': 'snapshot_roominfo', 'item_list': []}
    send(ret, socket)

def save_snapshot(data, socket):
    snap = snapshot.SnapshotObj(data['snapshot_intro'], None, [])
    for item in data['item_list']:
        _item = snapshot.ItemObj('desk', item['iid'], item['position'], item['scale'], item['rotation'])
        snap.put_item(_item)
    res = snapshot.save_snapshot(data['uid'], get_timestamp(), snap)
    
    if not res:
        ret = {'action': 'err'}
    else:
        newsfeed.add_snap(data['uid'], res)
        ret = {'action': 'ok', 'timestamp': res}
    send(ret, socket)
    snapshot.save()
    newsfeed.save()

def visit_book_request(data, socket):
    #if data['type'] == 'comment':
    res = visitbook.get_comment_list(data['uid'])
    #elif data['type'] == 'reply':
        #res = visitbook.get_comment_reply_list(data['uid'], data['cid'])
    if not res:
        send({'action': 'visit_book_request', 'visit_book': []}, socket)
        return

    refresh_num = 5
    res = res[int(data['count']) * refresh_num:(int(data['count']) + 1) * refresh_num]
    for r in res:
        r['nickname'] = profile.get_profile_nickname(r['writer_uid'])
    ret = {'action': 'visit_book_request'}
    ret['visit_book'] = res
    send(ret, socket)

def visit_book_write(data, socket):
    if data['type'] == 'comment':
        res = visitbook.add_comment(data['uid'], data['writer_uid'], data['comment'], get_timestamp())
        if res:
            ret = {'action': 'visitbook_write', 'timestamp': res}
        else:
            ret = {'action': 'err'}
    elif data['type'] == 'reply':
        res = visitbook.add_comment_reply(data['uid'], data['cid'], data['writer_uid'], data['comment'], get_timestamp())
        if res:
            ret = {'action': 'visitbook_write', 'timestamp': res}
        else:
            ret = {'action': 'err'}
    else:
        ret = {'action': 'err'}
    send(ret, socket)
    visitbook.save()

def search(data, socket):
    query = profile.search_profile(data['query'], data['uid'])
    for q in query:
        q['isfollow'] = follow.is_following(data['uid'], q['uid'])
    res = {'action': 'search', 'result': query}
    send(res, socket)

def snapshot_album(data, socket):
    album = snapshot.get_user_snapshot(data['uid'])
    res = []
    if not album:
        send({'action': 'snapshot_album', 'snapshot': []}, socket)
        return

    refresh_num = 4
    _album = list(album.keys())
    _album.reverse()
    _album = _album[int(data['count']) * refresh_num:(int(data['count']) + 1) * refresh_num]
    for _snap in _album:
        snap = {'timestamp': _snap}
        snap['snapshot_intro'] = album[_snap]['snapshot_intro']
        snap['size'] = snapshot.get_snapshot_size(data['uid'], _snap)
        if 'like_user' in album[_snap]:
            snap['like_num'] = len(album[_snap]['like_user'])
        else:
            snap['like_num'] = 0
        res.append(snap)

    ret = {'action': 'snapshot_album', 'snapshot': res}
    send(ret, socket)

def find_id(data, socket):
    res = userinfo.get_login_id_using_email(data['email'])
    ret = {'action': 'find_id', 'result': res}
    send(ret, socket)

def find_pw(data, socket):
    res = userinfo.get_login_id_using_email(data['email'])
    ret = {'action': 'find_pw'}
    if data['id'] in res:
        pw = find_pw_sendEmail(data['email'])
        if userinfo.modify_unknown_password_using_login_id(data['id'], pw):
            ret['result'] = 'ok'
        else:
            ret['result'] = 'err'
    else:
        ret['result'] = 'err'
    send(ret, socket)

def chg_profile_img(data, socket):
    ts = get_timestamp()
    profile.modify_profile_image_time(data['uid'], ts)
    profile.modify_profile_image_size(data['uid'], data['size'])
    ret = {'action': 'chg_profile_img', 'timestamp': ts}
    send(ret, socket)
    profile.save()

def chk_profile_img(data, socket):
    ts = profile.get_profile_image_time_list(data['uid'])
    sz = profile.get_profile_image_size_list(data['uid'])
    ret = {'action': 'chk_profile_img', 'timestamp': ts, 'size': sz}
    send(ret, socket)

def chg_bg_img(data, socket):
    ts = get_timestamp()
    profile.modify_profile_background_image_time(data['uid'], ts)
    profile.modify_profile_background_image_size(data['uid'], data['size'])
    ret = {'action': 'chg_bg_img', 'timestamp': ts}
    send(ret, socket)
    profile.save()

def chk_bg_img(data, socket):
    ts = profile.get_profile_background_image_time(data['uid'])
    sz = profile.get_profile_background_image_size(data['uid'])
    ret = {'action': 'chk_bg_img', 'timestamp': ts, 'size': sz}
    send(ret, socket)

def snapshot_size(data, socket):
    if snapshot.modify_snapshot_size(data['uid'], data['timestamp'], data['size']):
        ret = {'action': 'OK'}
    else:
        ret = {'action': 'err'}

def backup_log(data, socket):
    log_path = getcwd() + "/../data/log/" + get_timestamp()
    log.save_log(log_path)
    log.delete_all_log()
    send("OK", socket)




def send(msg, socket):
    msg = str(msg)
    msg = msg.replace("\'", "\"")
    print(msg)
    socket[0].send(msg.encode())
    log.add_log(get_timestamp(), {'type': 'send', 'content': msg}, socket[1])

def get_timestamp():
    t = str(datetime.now())
    t = t.replace('-', '')
    t = t.replace(':', '')
    t = t.replace(' ', '')
    t = t.replace('.', '')
    return t

def signup_sendEmail(email):
    return signup_send_mail(email)

def find_pw_sendEmail(email):
    return modify_pw_send_mail(email)


    """'profile_img_request_size': profile_img_request_size,
    'profile_img_update_size': profile_img_update_size,"""
    
manage_list = {
    'signup': signup,
    'login': login,
    'home': get_home,
    'profile_info': profile_info,
    'follower': get_follower,
    'following': get_following,
    'follow': add_follow,
    'follow_del': del_follow,
    'modify_nickname': mod_nick,
    'modify_email': mod_email,
    'modify_pw': mod_pw,
    'modify_introduce': mod_intro,
    'modify_snapshotdescription': mod_snapdesc,
    'snapshot_del': del_snapshot,
    'snapshot_like': like_snapshot,
    'snapshot_roominfo': get_snapshot_item_list,
    'snapshot_save': save_snapshot,
    'visit_book_request': visit_book_request,
    'visit_book_write': visit_book_write,
    'search': search,
    'snapshot_album': snapshot_album,
    'find_id': find_id,
    'find_pw': find_pw,
    'chg_profile_img': chg_profile_img,
    'chk_profile_img': chk_profile_img,
    'chg_bg_img': chg_bg_img,
    'chk_bg_img': chk_bg_img,
    'snapshot_size': snapshot_size,
    'backup_log': backup_log
}