import smtplib
from email.mime.text import MIMEText
from random import randint, choice

_from, _pw = input('email id와 비밀번호를 입력해주세요.').split()

global s

def login_out(func):
    def _login_out():
        global s
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(_from, _pw)
        func()
        s.quit()
        s.close()
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
    lst = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    res = ""
    for _ in range(15):
        res += choice(lst)
    
    msg = MIMEText("변경된 비밀번호는: " + res + "입니다.")
    msg['Subject'] = 'dARak 비밀번호 변경 알림입니다.'

    s.sendmail(_from, _to, msg.as_string())
    return res