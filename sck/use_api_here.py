import os
from os.path import isfile
import sys

from pprint import pprint

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

# 암호키가 있을 때 DB 제어 패키지 import
# 없다면 main 강제종료
key_path = "../FirebaseControll/key/key.json"

if isfile(key_path) is True:
    print("Importing DB controll package")
    from FirebaseControll.DBctrl import *
    print("Import DB controll package success.")
else:
    print("There's no key to access Firebase DB. Please insert Key json file into ../FirebaseControll/key directory.")
    print("SYSTEM OUT")
    sys.exit()

"""

uid 값이 544996263인 유저의 방명록 댓글 목록을 얻고 싶다.
-> 
ex1)
datalist = visitbook.get_comment_list(544996263)

OR

user_uid = 544996263
datalist = visitbook.get_comment_list(user_uid)

ex2)
pprint(visitbook.get_comment_list(544996263))
를 통해 cid가 '-MZgqNb2OlTJ2zbMfE19'란 것을 알게 됐으니, 이 값으로 답글 리스트를 받고 싶다면
pprint(visitbook.get_comment_reply_list(544996263, '-MZgqNb2OlTJ2zbMfE19'))

다른 함수들이나 자세한 DB 구조는 description.txt나 모듈 소스코드 보시면 됩니다.
"""