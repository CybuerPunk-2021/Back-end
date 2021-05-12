import smtplib
from email.mime.text import MIMEText

_from, _pw = input('email id와 비밀번호를 입력해주세요.').split()

s = smtplib.SMTP('smtp.gmail.com', 587)
s.starttls()


def send_mail(_to, _msg):
    s.login(_from, _pw)
    msg = MIMEText(_msg)
    msg['Subject'] = 'dARak 회원가입 인증 메일입니다.'

    s.sendmail(_from, _to, msg.as_string())
    s.close()