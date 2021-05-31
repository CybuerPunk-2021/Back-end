from datetime import datetime
from DBctrl import *
from sendEmail import signup_send_mail, modify_pw_send_mail
import json
import os.path
import traceback

email_auth = {}

def manage(data, sck, addr):
    socket = (sck, addr)
    log.add_log(get_timestamp(), {'type': 'receive', 'content': data}, addr)
    try:
        act = data['action']
        if act not in manage_list:
            send({'action': 'wrong action format'}, socket)
            return
        manage_list[act](data, socket)
    except ConnectionResetError:
        raise ConnectionResetError()
    except Exception as e:
        send({'action': 'wrong msg format'}, socket)
        traceback.print_exc()
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
            break

    if res == -1:
        ret = {'action':'dup id'}
    elif res == -2:
        ret = {'action': 'dup nick'}
    elif res == True:
        email_auth[(data['id'], data['nickname'])] = signup_sendEmail(data)
        ret = {'action': 'email send'}
    send(ret, socket)
    try:
        while True:
            auth = socket[0].recv(1024)
            auth = auth.decode()
            auth = auth.replace("'", "\"")
            auth = json.loads(auth)
            if auth['action'] == 'email auth':
                if email_auth[(data['id'], data['nickname'])] == auth['auth']:
                    uid = userinfo.make_userinfo(data['id'], data['pw'], data['email'], data['nickname'])
                    profile.make_profile(uid, data['id'], data['nickname'], get_timestamp())
                    newsfeed.make_newsfeed(uid, data['nickname'])
                    ret = {'action': 'email auth', 'auth': 'True'}
                    send(ret, socket)
                    del(email_auth[(data['id']), data['nickname']])
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
    except:
        send({'action': 'wrong format'}, socket)
        traceback.print_exc()
        del(email_auth[(data['id']), data['nickname']])
        return

def login(data, socket):
    id = data['id']
    pw = data['pw']
    res = userinfo.login(id, pw)
    if res == False:
        ret = {'action': 'False'}
    else:
        ret = {'action':'True', 'nickname': res[0], 'uid': int(res[1])}
    send(ret, socket)

def get_home(data, socket):
    refresh_num = 4
    res = newsfeed.get_newsfeed_uid(data['uid'])
    if res:
        res = res[data['count'] * refresh_num: (data['count'] + 1) * refresh_num]
        for snap in res:
            snap['snapshot_intro'] = snapshot.get_snapshot_intro(snap['uid'], snap['timestamp'])
            snap['like'] = str(snapshot.is_user_like_snapshot(data['uid'], snap['uid'], snap['timestamp']))
        ret = {'action': 'homeinfo', 'info': res}
    else:
        ret = {'action': 'homeinfo', 'info': []}
    send(ret, socket)
    return

def profile_info(data, socket):
    res = profile.get_profile(data['uid'])
    if res == None:
        send({'action': 'None'}, socket)
    else:
        ret = {'action': 'profile_info', 'follower': res['num_follower'], 'self_intro': res['introduction']}
        if 'snapshot_info' in res:
            ret['snapshot_info'] = res['snapshot_info']        
        else:
            ret['snapshot_info'] = {}
    send(ret, socket)

def get_follower(data, socket):
    res = follow.get_user_follower_uid_list(data['uid'])
    result = []
    for r in res:
        tmp = {'uid': r}
        tmp['nickname'] = profile.get_profile_nickname(r)
        result.append(tmp)

    if res:
        ret = {'action': 'follower', 'follower': result}
    else:
        ret = {'action': 'follower err'}
    send(ret, socket)

def get_following(data, socket):
    res = follow.get_user_following_uid_list(data['uid'])
    result = []
    for r in res:
        tmp = {'uid': r}
        tmp['nickname'] = profile.get_profile_nickname(r)
        result.append(tmp)

    if res:
        ret = {'action': 'following', 'following': result}
    else:
        ret = {'action': 'following err'}
    send(ret, socket)

def add_follow(data, socket):
    if follow.follow_user(data['from_uid'], data['to_uid'], get_timestamp()):
        ret = {'action': 'OK'}
    else:
        ret = {'action': 'ALREADY'}
    send(ret, socket)
    
def del_follow(data, socket):
    if follow.unfollow_user(data['from_uid'], data['to_uid']):
        ret = {'action': 'OK'}
    else:
        ret = {'action': 'ALREADY'}
    send(ret, socket)

def mod_nick(data, socket):
    if profile.modify_nickname(data['uid'], data['nickname']):
        newsfeed.mod_nick(data['uid'], data['nickname'])
        ret = {'action': 'nickname_ok'}
    else:
        ret = {'action': 'dup nick'}
    send(ret, socket)

def mod_email(data, socket):
    try:
        email_auth[data['uid']] = signup_sendEmail(data)
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
    except:
        send({'action': 'wrong format'}, socket)
        del(email_auth[data['uid']])
    


def mod_pw(data, socket):
    if userinfo.modify_password_using_uid(data['uid'], data['pw'], data['new_pw']):
        ret = {'action': 'pw_ok'}
    else:
        ret = {'action': 'err'}
    send(ret, socket)

def mod_intro(data, socket):
    if profile.modify_introduction(data['uid'], data['introduce']):
        ret = {'action': 'introduce_ok'}
    else:
        ret = {'action': 'err'}
    send(ret, socket)

def mod_snapdesc(data, socket):
    if snapshot.modify_snapshot_intro(data['uid'], data['timestamp'], data['introduce']):
        ret = {'action': 'description_ok'}
    else:
        ret = {'action': 'err'}
    send(ret, socket)

def del_snapshot(data, socket):
    if snapshot.delete_snapshot(data['uid'], data['timestamp']):
        ret = {'action': 'ok'}
    else:
        ret = {'action': 'err'}
    send(ret, socket)

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

def get_snapshot_item_list(data, socket):
    res = snapshot.get_snapshot_item(data['uid'], data['timestamp'])
    if res:
        ret = {'action': 'snapshot_roominfo', 'item_list': res}
    else:
        ret = {'action': 'err'}
    send(ret, socket)

def save_snapshot(data, socket):
    snap = snapshot.SnapshotObj(data['snapshot_intro'], None, [])
    for item in data['item_list']:
        _item = snapshot.ItemObj('desk', item['iid'], item['position'], item['scale'], item['rotation'])
        snap.put_item(_item)
    res = snapshot.save_snapshot(data['uid'], get_timestamp(), snap)
    #print(res)

    if not res:
        ret = {'action': 'err'}
    else:
        newsfeed.add_snap(data['uid'], res)
        ret = {'action': 'ok', 'timestamp': res}
    send(ret, socket)

def visit_book_request(data, socket):
    refresh_num = 5
    if data['type'] == 'comment':
        res = visitbook.get_comment_list(data['uid'])
    elif data['type'] == 'reply':
        res = visitbook.get_comment_reply_list(data['uid'], data['cid'])
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

def search(data, socket):
    query = profile.search_profile(data['query'])
    res = {'action': 'search', 'result': query}
    send(res, socket)

def snapshot_album(data, socket):
    album = snapshot.get_user_snapshot(data['uid'])
    res = []
    for _snap in album:
        snap = {'timestamp': _snap}
        snap['snapshot_intro'] = album[_snap]['snapshot_intro']
        if 'like_user' in album[_snap]:
            snap['like_num'] = len(album[_snap]['like_user'])
        else:
            snap['like_num'] = 0
        res.insert(0, snap)

    ret = {'action': 'snapshot_album', 'snapshot': res}
    send(ret, socket)

def find_id(data, socket):
    res = userinfo.get_login_id_using_email(data['email'])
    ret = {'action': 'find_id', 'result': res}
    send(ret, socket)

def modify_pw(data, socket):
    res = userinfo.get_login_id_using_email(data['email'])
    ret = {'action': 'moodify_pw'}
    if data['id'] in res:
        pw = modify_pw_sendEmail(data['email'])
        if userinfo.modify_unknown_password_using_login_id(data['id'], pw):
            ret['result'] = 'ok'
        else:
            ret['result'] = 'err'
    else:
        ret['result'] = 'err'
    send(ret, socket)
    

def send(msg, socket):
    log.add_log(get_timestamp(), {'type': 'send', 'content': msg}, socket[1])
    msg = str(msg)
    msg = msg.replace("\'", "\"")
    print(msg)
    socket[0].send(msg.encode())

def get_timestamp():
    t = str(datetime.now())
    t = t.replace('-', '')
    t = t.replace(':', '')
    t = t.replace(' ', '')
    t = t.replace('.', '')
    return t

def signup_sendEmail(data):
    return signup_send_mail(data['email'])

def modify_pw_sendEmail(data):
    return modify_pw_send_mail(data['email'])


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
    'modify_pw': modify_pw
}