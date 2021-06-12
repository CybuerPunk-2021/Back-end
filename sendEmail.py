import smtplib
from email.mime.text import MIMEText
from random import randint, choice

_from, _pw = input('email id와 비밀번호를 입력해주세요.').split()

global s

def login_out(func):
    def _login_out(_to):
        global s
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(_from, _pw)
        ret = func(_to)
        s.quit()
        s.close()
        return ret
    return _login_out
        
@login_out
def signup_send_mail(_to):
    global s
    auth = randint(100000, 999999)
    msg = MIMEText(str(auth))
    msg['Subject'] = 'dARak 회원가입 인증 메일입니다.'

    s.sendmail(_from, _to, msg.as_string())
    return auth

@login_out
def modify_pw_send_mail(_to):
    global s
    lst = "123456789abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ"
    res = ""
    for _ in range(8):
        res += choice(lst)
    
    msg = MIMEText("변경된 비밀번호는: " + res + "입니다.")
    msg['Subject'] = 'dARak 비밀번호 변경 알림입니다.'

    s.sendmail(_from, _to, msg.as_string())
    return res