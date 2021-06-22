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
        act = data['action'] # get action
        if act not in manage_list: # chk action
            send({'action': 'wrong action format'}, socket) # return wrong action
            return # return
        manage_list[act](data, socket) # do action
        log.add_log(get_timestamp(), {'type': 'receive', 'content': data}, addr) # write log
    except ConnectionResetError: # connection error
        raise ConnectionResetError() # raise
    except Exception as e: # other exceptions
        send({'action': 'wrong msg format'}, socket) # return wrong msg
        traceback.print_exc() # stack trace
        log.add_error_log(get_timestamp(), {'content': data, 'error_type': str(type(e)) + " : " + str(e)}, addr) # write err log
    return
    
def signup(data, socket): # signup
    res = userinfo.check_id_nickname_dup(data['id'], data['nickname']) # chk dup

    for ea in email_auth.keys(): # chk signup list
        if data['id'] == ea[0] or data['nickname'] == ea[1]: # ing
            res = -1 # -1

    if res == -1: # dup id
        ret = {'action':'dup id'} # dup id
        send(ret, socket) # send
        return
    elif res == -2: # dup nick
        ret = {'action': 'dup nick'} # dup nick
        send(ret, socket) # send
        return
    elif res: # ok
        email_auth[(data['id'], data['nickname'])] = signup_sendEmail(data['email']) # add signup list and send mail
        ret = {'action': 'email send'} # request auth
    send(ret, socket) # send
    try: 
        while True: # untile get true auth
            auth = socket[0].recv(1024) # recv data
            auth = auth.decode() # decode data 
            auth = auth.replace("'", "\"") # replace single quote to double
            auth = json.loads(auth) # convert data to json(dict)
            print(str(auth)) # log
            if auth['action'] == 'email auth': # chk action
                if email_auth[(data['id'], data['nickname'])] == auth['auth']: # true auth
                    uid = userinfo.make_userinfo(data['id'], data['pw'], data['email'], data['nickname']) # make_userinfo
                    profile.make_profile(uid, data['id'], data['nickname'], get_timestamp()) # make_profile
                    newsfeed.make_newsfeed(uid, data['nickname']) # make newsfeed
                    ret = {'action': 'email auth', 'auth': 'True'} # email auth true
                    send(ret, socket) # send
                    del(email_auth[(data['id']), data['nickname']]) # delete manage list
                    userinfo.save() # save userinfo
                    profile.save() # save profile
                    newsfeed.save() # save newsfeed
                    break # break loop
                else: # false auth
                    ret = {'action': 'email auth', 'auth': 'False'} # email auth false
                    send(ret, socket) # send
            else:
                send({'action': 'wrong action'}, socket) # return wrong action
                del(email_auth[(data['id']), data['nickname']]) # delete manage list
                break # break loop
    except ConnectionResetError: # if connection error
        del(email_auth[(data['id']), data['nickname']]) # delete manage list
        raise ConnectionResetError() # raise
    except Exception as e: # other exceptions
        del(email_auth[(data['id']), data['nickname']]) # delete manage list
        raise e # raise

def login(data, socket): #login
    res = userinfo.login(data['id'], data['pw']) # login
    if not res: # if fail
        ret = {'action': 'False'} # send false
    else: # if success
        snap = snapshot.get_user_latest_snapshot(res[1]) # get latest snapshot
        ret = {'action':'True', 'nickname': res[0], 'uid': int(res[1]), 'email': res[2]} # make return
        if snap: # if latest snapshot exist
            ret['timestamp'] = snap['timestamp'] # get timestamp
        else: # if latest snapshot not exist
            ret['timestamp'] = "" # empty timestamp
    send(ret, socket) # send

def get_home(data, socket):
    refresh_num = 4 # refresh_num
    res = newsfeed.get_newsfeed_uid(data['uid']) # get newsfeed
    if res: # if newsfeed exist
        res = res[data['count'] * refresh_num: (data['count'] + 1) * refresh_num] # get
        for snap in res: # get timestamp of snapshot
            _snap = snapshot.get_snapshot(snap['uid'], snap['timestamp']) # get snapshot
            snap['snapshot_intro'] = _snap['snapshot_intro'] # snapshot intro
            snap['size'] = snapshot.get_snapshot_size(snap['uid'], snap['timestamp']) # snapshot size
            if 'like_user' in _snap: # like user exist
                snap['like'] = str(data['uid'] in _snap['like_user']) # get like boolean
                snap['like_num'] = len(_snap['like_user']) # get like_num
            else: # like user non exist
                snap['like'] = "False" 
                snap['like_num'] = 0
        ret = {'action': 'homeinfo', 'info': res} # make return
    else:
        ret = {'action': 'homeinfo', 'info': []} # make return
    send(ret, socket) # send
    return

def profile_info(data, socket):
    res = profile.get_profile(data['uid']) # get profile
    if not res: # if no profile
        send({'action': 'profile_info', 'follower': 0, 'self_intro': "", 'snapshot_info': {}}, socket) # send none
    else: #profile exist
        ret = {'action': 'profile_info', 'follower': res['num_follower'], 'self_intro': res['introduction']}
        snap = snapshot.get_user_latest_snapshot(data['uid']) # get latest snapshot
        if snap: # if snapshot exist
            snap['size'] = snapshot.get_snapshot_size(data['uid'], snap['timestamp']) # get size
            if 'like_user' in snap: # get like user
                snap['like_num'] = len(snap['like_user']) # get like num
                del snap['like_user']
            else:
                snap['like_num'] = 0
        else: # if snapshot not exist
            snap = {'timestamp': "", 'like_num': 0, 'snapshot_intro': "", 'size': 0}
        ret['snapshot_info'] = snap

        send(ret, socket) # send

def get_follower(data, socket):
    res = follow.get_user_follower_uid_list(data['uid']) # get follower
    result = [] # result array

    if res: # follower exist
        for r in res: # iterate, r = uid
            tmp = {'uid': r}
            tmp['nickname'] = profile.get_profile_nickname(r) # get nickname
            tmp['isfollow'] = str(follow.is_following(data['uid'], r)) # get following
            result.append(tmp) # append to result array
        ret = {'action': 'follower', 'follower': result}
    else: # if follower not exist
        ret = {'action': 'follower', 'follower': []}
    send(ret, socket) # send

def get_following(data, socket):
    res = follow.get_user_following_uid_list(data['uid']) # get following
    result = [] # result array

    if res: # following exist
        for r in res: # iterate, r = uid
            tmp = {'uid': r}
            tmp['nickname'] = profile.get_profile_nickname(r) # get nickname
            result.append(tmp) # append to result array
        ret = {'action': 'following', 'following': result}
    else: # if following not exist
        ret = {'action': 'following', 'following': []}
    send(ret, socket) # send

def add_follow(data, socket):
    if follow.follow_user(data['from_uid'], data['to_uid'], get_timestamp()): # add follow
        ret = {'action': 'OK'}
    else:
        ret = {'action': 'ALREADY'}
    send(ret, socket) # send
    follow.save() # save follow
    profile.save() # save profile
    
def del_follow(data, socket):
    if follow.unfollow_user(data['from_uid'], data['to_uid']): # delete follow
        ret = {'action': 'OK'}
    else:
        ret = {'action': 'ALREADY'}
    send(ret, socket) # send
    follow.save() # save follow
    profile.save() # save profile

def mod_nick(data, socket):
    if profile.modify_nickname(data['uid'], data['nickname']): # modify nickname
        newsfeed.mod_nick(data['uid'], data['nickname']) # modify nickname
        ret = {'action': 'nickname_ok'}
    else:
        ret = {'action': 'dup nick'}
    send(ret, socket) # send
    profile.save() # save profile
    newsfeed.save() # save newsfeed

def mod_email(data, socket):
    try:
        email_auth[data['uid']] = signup_sendEmail(data['email']) # add signup list and send email
        ret = {'action': 'email_send'}
    except:
        ret = {'action': 'err'}
    send(ret, socket) # send

    try:
        while True: # untile true auth
            auth = socket[0].recv(1024) # recv data
            auth = auth.decode() # decode date
            auth = auth.replace("'", "\"") # replace single quote to double
            auth = json.loads(auth) # convert data to json(dict)
            if auth['action'] == 'email auth': # chk action
                if email_auth[data['uid']] == auth['auth']: # chk auth
                    userinfo.modify_email(userinfo.get_login_id_using_uid(data['uid']), data['email']) # modify email
                    ret = {'action': 'email auth', 'auth': 'True'}
                    send(ret, socket) # send
                    del(email_auth[data['uid']]) # delete signup list
                    userinfo.save() # save userinfo
                    break
                else: # false auth
                    ret = {'action': 'email auth', 'auth': 'False'}
                    send(ret, socket) # send
            else: # wrong action
                send({'action': 'wrong action'}, socket) # send
                del(email_auth[data['uid']]) # delete signup list
                break # break loop
    except ConnectionResetError: # connection error
        del(email_auth[data['uid']]) # delete signup list
        raise ConnectionResetError() # raise
    except Exception as e: # other exceptions
        del(email_auth[data['uid']]) # delete signup list
        raise e # raise
    


def mod_pw(data, socket):
    if userinfo.modify_password_using_uid(data['uid'], data['pw'], data['new_pw']): # modify password
        ret = {'action': 'pw_ok'}
    else:
        ret = {'action': 'err'}
    send(ret, socket) # send
    userinfo.save() # save userinfo

def mod_intro(data, socket):
    if profile.modify_introduction(data['uid'], data['introduce']): # modify introduction
        ret = {'action': 'introduce_ok'}
    else:
        ret = {'action': 'err'}
    send(ret, socket) # send
    profile.save() # save profile

def mod_snapdesc(data, socket):
    if snapshot.modify_snapshot_intro(data['uid'], data['timestamp'], data['introduce']): # modify snapshot intro
        ret = {'action': 'description_ok'}
    else:
        ret = {'action': 'err'}
    send(ret, socket) # send
    snapshot.save() # save snapshot

def del_snapshot(data, socket):
    if snapshot.delete_snapshot(data['uid'], data['timestamp']): # delete snapshot
        newsfeed.del_snap(data['uid'], data['timestamp']) # delete snapshot
        ret = {'action': 'ok'}
    else:
        ret = {'action': 'err'}
    send(ret, socket) # send
    snapshot.save() # save snapshot
    newsfeed.save() # save newsfeed

def like_snapshot(data, socket):
    if data['type'] == 'add': # if type add
        if snapshot.like_snapshot(data['to_uid'], data['from_uid'], data['timestamp']): # add like to snapshot
            ret = {'action': 'ok'}
        else:
            ret = {'action': 'err'}
    elif data['type'] == 'delete': # if type deelte
        if snapshot.unlike_snapshot(data['to_uid'], data['from_uid'], data['timestamp']): # delete like to snapshot
            ret = {'action': 'ok'}
        else:
            ret = {'action': 'err'}
    else:
        ret = {'action': 'like snapshot err'}
    send(ret, socket) # send
    snapshot.save() # save snapshot

def get_snapshot_item_list(data, socket):
    res = snapshot.get_snapshot_item(data['uid'], data['timestamp'])
    if res:
        ret = {'action': 'snapshot_roominfo', 'item_list': res}
    else:
        ret = {'action': 'snapshot_roominfo', 'item_list': []}
    send(ret, socket)

def save_snapshot(data, socket):
    snap = snapshot.SnapshotObj(data['snapshot_intro'], None, []) # make snapshot obj
    for item in data['item_list']: # iterate
        _item = snapshot.ItemObj('desk', item['iid'], item['position'], item['scale'], item['rotation']) # make item obj
        snap.put_item(_item) # add item to snap
    res = snapshot.save_snapshot(data['uid'], get_timestamp(), snap) # save snapshot
    
    if not res:
        ret = {'action': 'err'}
    else: # if success
        newsfeed.add_snap(data['uid'], res) # add snapshot to newsfeed
        ret = {'action': 'ok', 'timestamp': res}
    send(ret, socket) # send
    snapshot.save() #save snapshot
    newsfeed.save() # save newsfeed

def visit_book_request(data, socket):
    res = visitbook.get_comment_list(data['uid']) # get comment list
    if not res: # if no comment
        send({'action': 'visit_book_request', 'visit_book': []}, socket)
        return

    refresh_num = 5 # refresh num
    res = res[int(data['count']) * refresh_num:(int(data['count']) + 1) * refresh_num]
    for r in res: # iterate
        r['nickname'] = profile.get_profile_nickname(r['writer_uid']) # get nickname
    ret = {'action': 'visit_book_request'}
    ret['visit_book'] = res
    send(ret, socket) # send

def visit_book_write(data, socket):
    if data['type'] == 'comment': # if type is comment
        res = visitbook.add_comment(data['uid'], data['writer_uid'], data['comment'], get_timestamp()) # add comment
        if res:
            ret = {'action': 'visitbook_write', 'timestamp': res}
        else:
            ret = {'action': 'err'}
    elif data['type'] == 'reply': # if type is reply
        res = visitbook.add_comment_reply(data['uid'], data['cid'], data['writer_uid'], data['comment'], get_timestamp()) # add reply
        if res:
            ret = {'action': 'visitbook_write', 'timestamp': res}
        else:
            ret = {'action': 'err'}
    else:
        ret = {'action': 'err'}
    send(ret, socket) # send
    visitbook.save() # save visitbook

def search(data, socket):
    query = profile.search_profile(data['query'], data['uid']) # search query
    for q in query: # iterate
        q['isfollow'] = str(follow.is_following(data['uid'], q['uid'])) # chk is follow
    res = {'action': 'search', 'result': query}
    send(res, socket) # send

def snapshot_album(data, socket):
    album = snapshot.get_user_snapshot(data['uid']) # get user snapshot list
    res = []
    if not album: # if no snapshot
        send({'action': 'snapshot_album', 'snapshot': []}, socket)
        return

    refresh_num = 4 # refresh num
    _album = list(album.keys()) # get timestamp
    _album.reverse() # reverse
    _album = _album[int(data['count']) * refresh_num:(int(data['count']) + 1) * refresh_num]
    for _snap in _album: # iterate
        snap = {'timestamp': _snap}
        snap['snapshot_intro'] = album[_snap]['snapshot_intro'] # get intro
        snap['size'] = snapshot.get_snapshot_size(data['uid'], _snap) # get size
        if 'like_user' in album[_snap]: # if like user exist
            snap['like_num'] = len(album[_snap]['like_user'])
        else: # if like user not exist
            snap['like_num'] = 0
        res.append(snap) # append to res

    ret = {'action': 'snapshot_album', 'snapshot': res}
    send(ret, socket) # send

def find_id(data, socket):
    res = userinfo.get_login_id_using_email(data['email']) # find id
    ret = {'action': 'find_id', 'result': res}
    send(ret, socket) # send

def find_pw(data, socket):
    res = userinfo.get_login_id_using_email(data['email']) # get id from email
    ret = {'action': 'find_pw'}
    if data['id'] in res: # id chk
        pw = find_pw_sendEmail(data['email']) # send email
        if userinfo.modify_unknown_password_using_login_id(data['id'], pw): # modify pw
            ret['result'] = 'ok'
        else:
            ret['result'] = 'err'
    else:
        ret['result'] = 'err'
    send(ret, socket) # send

def chg_profile_img(data, socket):
    ts = get_timestamp() # get timestamp
    profile.modify_profile_image_time(data['uid'], ts) # modify profile image time
    profile.modify_profile_image_size(data['uid'], data['size']) # modify profile image size
    ret = {'action': 'chg_profile_img', 'timestamp': ts}
    send(ret, socket) # send
    profile.save() # save profile

def chk_profile_img(data, socket):
    ts = profile.get_profile_image_time_list(data['uid']) # get profile image time
    sz = profile.get_profile_image_size_list(data['uid']) # get profile image size
    ret = {'action': 'chk_profile_img', 'timestamp': ts, 'size': sz}
    send(ret, socket) # send

def chg_bg_img(data, socket):
    ts = get_timestamp() # get timestamp
    profile.modify_profile_background_image_time(data['uid'], ts) # modify bg image time
    profile.modify_profile_background_image_size(data['uid'], data['size']) # modify bg image size
    ret = {'action': 'chg_bg_img', 'timestamp': ts}
    send(ret, socket) # send
    profile.save() # save profile

def chk_bg_img(data, socket):
    ts = profile.get_profile_background_image_time(data['uid']) # get bg image time
    sz = profile.get_profile_background_image_size(data['uid']) # get bg image size
    ret = {'action': 'chk_bg_img', 'timestamp': ts, 'size': sz}
    send(ret, socket) # send

def snapshot_size(data, socket):
    if snapshot.modify_snapshot_size(data['uid'], data['timestamp'], data['size']): # modify snapshot thumbnail size
        ret = {'action': 'OK'}
    else:
        ret = {'action': 'err'}
    send(ret, socket) # send
    snapshot.save() # save snapshot

def backup_log(data, socket):
    log_path = getcwd() + "/../data/log/" + get_timestamp() # make path
    log.save_log(log_path) # save log
    log.delete_all_log() # delte all log
    send("OK", socket) # send




def send(msg, socket):
    msg = str(msg) # convert msg to string
    msg = msg.replace("\'", "\"") # replace single quote to double
    print(msg) # print
    socket[0].send(msg.encode()) # send encoded msg
    log.add_log(get_timestamp(), {'type': 'send', 'content': msg}, socket[1]) # wirte log

def get_timestamp(): # make timestamp
    t = str(datetime.now())
    t = t.replace('-', '')
    t = t.replace(':', '')
    t = t.replace(' ', '')
    t = t.replace('.', '')
    return t

def signup_sendEmail(email): # signup send email
    return signup_send_mail(email)

def find_pw_sendEmail(email): # find pw send email
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