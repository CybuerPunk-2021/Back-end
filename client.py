from socket import *

clientSock = socket(AF_INET, SOCK_STREAM)
clientSock.connect(('godzero.iptime.org', 5500))

print('연결 성공')

while True:
    inp = input()
    if inp == 'q':
        break

    clientSock.send(inp.encode())
    res = clientSock.recv(1024).decode()
    print(res)