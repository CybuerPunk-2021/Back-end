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

