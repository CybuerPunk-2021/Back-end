from datetime import datetime
from DBctrl import *
from random import randint
from sendEmail import send_mail
import json
import os.path

email_auth = {}

def manage(data, sck, addr):
    global socket
    global ipAddr
    socket = sck
    ipAddr = addr
    log.add_log(get_timestamp(), {'type': 'receive', 'content': data}, ipAddr)
    try:
        act = data['action']
        if act not in manage_list:
            send("{'action': 'wrong action format'}")
            return
        manage_list[act](data)
    except Exception as e:
        send("{'action': 'wrong msg format'}")
        print(str(e))
    return

def profile_img_request_size(data):
    global socket
    uid = data['uid']
    path = '../data/img/profile/' + str(data['uid'])

    if not os.path.isfile(path):
        path = '../data/img/profile/default.png'

    f = open(path, 'rb')
    img = f.read()
    f.close()
    ret = {'action': 'profile_img_request_size', 'size': len(img), 'timestamp': get_timestamp()}
    send(ret)
    try:
        data = socket.recv(1024).decode()
        data = data.replace("'", "\"")
        data = json.loads(data)
        if data['action'] == 'profile_img_request' and data['uid'] == uid:
            socket.send(img)
            pass
        else:
            send("{'action': 'wrong uid'}")
    except:
        return

def profile_img_update_size(data):
    global socket
    uid = data['uid']
    size = int(data['size'])
    ret = {'action': 'profile_img_update_size', 'timestamp': get_timestamp()}
    send(ret)
    try:
        path = '../data/img/profile/' + str(data['uid'])
        f = open(path, 'wb')
        
        for _ in range(int(size / 4096) + 1):
            data = socket.recv(4096)
            f.write(data)
        f.close()
        ret = {'action': 'profile_img_update', 'type': 'True'}
    except:
        ret = {'action': 'profile_img_update', 'type': 'False'}
    send(ret)

def signup(data):
    global socket
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
        email_auth[(data['id'], data['nickname'])] = sendEmail(data)
        ret = {'action': 'email send'}
    send(ret)
    try:
        while True:
            auth = socket.recv(1024)
            auth = auth.decode()
            auth = auth.replace("'", "\"")
            auth = json.loads(auth)
            if auth['action'] == 'email auth':
                if email_auth[(data['id'], data['nickname'])] == auth['auth']:
                    uid = userinfo.make_userinfo(data['id'], data['pw'], data['email'], data['nickname'])
                    profile.make_profile(uid, data['id'], data['nickname'], get_timestamp())
                    newsfeed.make_newsfeed(uid, data['nickname'])
                    ret = {'action': 'email auth', 'auth': 'True'}
                    send(ret)
                    del(email_auth[(data['id']), data['nickname']])
                    break
                else:
                    ret = {'action': 'email auth', 'auth': 'False'}
                    send(ret)
            else:
                send('wrong action')
                del(email_auth[(data['id']), data['nickname']])
                break
    except Exception as e:
        send('wrong format')
        print(e)
        del(email_auth[(data['id']), data['nickname']])
        return

def sendEmail(data):
    auth = randint(100000, 999999)
    send_mail(data['email'], str(auth))
    return auth

def login(data):
    id = data['id']
    pw = data['pw']
    res = userinfo.login(id, pw)
    if res == False:
        ret = {'action': 'False'}
    else:
        ret = {'action':'True', 'nickname': res[0], 'uid': int(res[1])}
    send(ret)

def get_home(data):
    res = newsfeed.get_newsfeed_uid(data['uid'])
    if res:
        res = res[data['count'] * 2: (data['count'] + 1) * 2]
        for snap in res:
            snap['snapshot_intro'] = snapshot.get_snapshot_intro(snap['uid'], snap['timestamp'])
            snap['like'] = str(snapshot.is_user_like_snapshot(data['uid'], snap['uid'], snap['timestamp']))
        ret = {'action': 'homeinfo', 'info': res}
    else:
        ret = {'action': 'homeinfo', 'info': []}
    send(ret)
    return

def profile_info(data):
    res = profile.get_profile(data['uid'])
    if res == None:
        send('None')
    else:
        ret = {'action': 'profile_info', 'follower': res['num_follower'], 'self_intro': res['introduction']}
        ret['snapshot_info'] = res['snapshot_info']        
    send(ret)

def get_follower(data):
    res = follow.get_user_follower_uid_list(data['uid'])
    if res:
        ret = {'action': 'follower', 'follower': res}
    else:
        ret = {'action': 'follower err'}
    send(ret)

def get_following(data):
    res = follow.get_user_following_uid_list(data['uid'])
    if res:
        ret = {'action': 'following', 'following': res}
    else:
        ret = {'action': 'following err'}
    send(ret)

def add_follow(data):
    if follow.follow_user(data['from_uid'], data['to_uid'], get_timestamp()):
        ret = {'action': 'OK'}
    else:
        ret = {'action': 'ALREADY'}
    send(ret)
    
def del_follow(data):
    if follow.unfollow_user(data['from_uid'], data['to_uid']):
        ret = {'action': 'OK'}
    else:
        ret = {'action': 'ALREADY'}
    send(ret)

def mod_nick(data):
    if profile.modify_nickname(data['uid'], data['nickname']):
        newsfeed.mod_nick(data['uid'], data['nickname'])
        ret = {'action': 'nickname_ok'}
    else:
        ret = {'action': 'dup nick'}
    send(ret)

def mod_email(data):
    global socket
    try:
        email_auth[data['uid']] = sendEmail(data)
        ret = {'action': 'email_send'}
    except:
        ret = {'action': 'err'}
    send(ret)

    try:
        while True:
            auth = socket.recv(1024)
            auth = auth.decode()
            auth = auth.replace("'", "\"")
            auth = json.loads(auth)
            if auth['action'] == 'email auth':
                if email_auth[data['uid']] == auth['auth']:
                    userinfo.modify_email(userinfo.get_userinfo_using_uid(data['uid']), data['email'])
                    ret = {'action': 'email auth', 'auth': 'True'}
                    send(ret)
                    del(email_auth[data['uid']])
                    break
                else:
                    ret = {'action': 'email auth', 'auth': 'False'}
                    send(ret)
            else:
                send('wrong action')
                del(email_auth[data['uid']])
                break
    except:
        send('wrong format')
        del(email_auth[data['uid']])
    


def mod_pw(data):
    if userinfo.modify_password_using_uid(data['uid'], data['pw'], data['new_pw']):
        ret = {'action': 'pw_ok'}
    else:
        ret = {'action': 'err'}
    send(ret)

def mod_intro(data):
    if profile.modify_introduction(data['uid'], data['introduce']):
        ret = {'action': 'introduce_ok'}
    else:
        ret = {'action': 'err'}
    send(ret)

def mod_snapdesc(data):
    if snapshot.modify_snapshot_intro(data['uid'], data['timestamp'], data['introduce']):
        ret = {'action': 'description_ok'}
    else:
        ret = {'action': 'err'}
    send(ret)

def del_snapshot(data):
    if snapshot.delete_snapshot(data['uid'], datap['timestamp']):
        ret = {'action': 'ok'}
    else:
        ret = {'action': 'err'}
    send(ret)

def like_snapshot(data):
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
    send(ret)

def get_snapshot_item_list(data):
    res = snapshot.get_snapshot_item(data['uid'], data['timestamp'])
    if res:
        ret = {'action': 'snapshot_roominfo', 'item_list': res}
    else:
        ret = {'action': 'err'}
    send(ret)

def save_snapshot(data):
    snap = snapshot.SnapshotObj(data['snapshot_intro'], None, [])
    for item in data['item_list']:
        _item = snapshot.ItemObj('desk', item['iid'], item['position'], item['scale'], item['rotation'])
        snap.put_item(_item)
    res = snapshot.save_snapshot(data['uid'], get_timestamp(), snap)
    print(res)

    if not res:
        ret = {'action': 'err'}
    else:
        newsfeed.add_snap(data['uid'], res)
        ret = {'action': 'ok', 'timestamp': res}
    send(ret)

def visit_book_request(data):
    if data['type'] == 'comment':
        res = visitbook.get_comment_list(data['uid'])
    elif data['type'] == 'reply':
        res = visitbook.get_comment_reply_list(data['uid'], data['cid'])
    res = res[int(data['count']) * 5:(int(data['count']) + 1) * 5 ]
    ret = {'action': 'visit_book_request'}
    ret['visit_book'] = res
    send(ret)

def visit_book_write(data):
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
    send(ret)
    

def send(msg):
    global socket
    global ipAddr
    log.add_log(get_timestamp(), {'type': 'send', 'content': msg}, ipAddr)
    msg = str(msg)
    msg = msg.replace("\'", "\"")
    print(msg)
    socket.send(msg.encode())

def get_timestamp():
    t = str(datetime.now())
    t = t.replace('-', '')
    t = t.replace(':', '')
    t = t.replace(' ', '')
    t = t.replace('.', '')
    return t


manage_list = {
    'profile_img_request_size': profile_img_request_size,
    'profile_img_update_size': profile_img_update_size,
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
    'visit_book_write': visit_book_write
}