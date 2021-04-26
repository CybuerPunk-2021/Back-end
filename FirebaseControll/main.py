from os.path import isfile
import sys

from pprint import pprint

# 암호키가 있을 때 DB 제어 패키지 import
# 없다면 main 강제종료
key_path = "./key/key.json"

if isfile(key_path) is True:
    print("Importing DB controll package")
    from DBctrl import *
    print("Import DB controll package success.")
else:
    print("There's no key to access Firebase DB. Please insert Key json file into ./key directory.")
    print("SYSTEM OUT")
    sys.exit()

# 실행 부분

def using_USERINFO():
    while True:
        print("1 : show all user info")
        print("2 : show user info")
        print("3 : make user info")
        print("")
        print("6 : delete user info")
        print("0 : MENU")
        num = input("USERINFO : ")

        if num == 1:
            pprint(userinfo.get_all_userinfo())
        elif num == 2:
            user_id = input("user login ID : ")
            pprint(userinfo.get_userinfo(str(user_id)))
        elif num == 6:
            user_id = input("user login ID : ")
            pprint(userinfo.delete_userinfo(str(user_id)))
        elif num == 0:
            break
        else
            break

def using_FOLLOW_RELATION():
    while True:
        print("1 : show all follow situations")
        print("2 : show user follow")
        print("3 : follow user")
        print("4 : unfollow user")
        print("0 : MENU")
        num = input("FOLLOW : ")

        if num == 1:
            print("Follow situation : ")
            pprint(follow.get_all_follow())
            print("Relation situation : ")
            pprint(follow.get_all_relation())
        elif num == 2:
            user_id = input("UID : ")
            pprint(follow.get_follow(str(user_id)))
        elif num == 0:
            break
        else
            break


while True:
    print("1 : userinfo")
    print("2 : profile")
    print("3 : visitbook")
    print("4 : follow")
    print("0 : EXIT")
    num = input("Select number of  what you want. : ")

    if num == 1:
        using_USERINFO()
    elif num == 2:
        #using_PROFILE()
    elif num == 3:
        #using_VISITBOOK()
    elif num == 4:
        using_FOLLOW_RELATION()
    elif num == 0:
        print("End program.")
        break