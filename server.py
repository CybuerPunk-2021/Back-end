from socket import socket
from socket import AF_INET
from socket import SOCK_STREAM
from threading import Thread
from manager import manage
import json
import firebase_admin
from firebase_admin import credentials

from flask import Flask

buf_size = 1024 # read buffer size

if not firebase_admin._apps:
    cred = credentials.Certificate("../key/key.json")
    firebase_admin.initialize_app(cred,{'databaseURL' : 'https://decisive-sylph-308301-default-rtdb.firebaseio.com/'})

class c_sck(Thread): # client socket thread object
    def __init__(self, socket, lst): # init method
        super().__init__() # Thread.__init__()
        self.s_sck = socket # server socket
        self.lst = lst # client socket list

    def run(self): # when thread is started
        self.c_socket, self.addr = self.s_sck.accept() # accept
        print('aceepted')
        create_thread(self.s_sck) # create new thread to accept client
        tmp_thread = Thread(target = self.c_recv) # thread for receive msg
        tmp_thread.daemon = True # set damon
        tmp_thread.start() # start

    def c_recv(self): # receive msg from client
        while True: # repeat
            print('receiving...')
            try: # while connection is alive
                get_data = self.c_socket.recv(buf_size) # receive data
                data = get_data.decode() # decode data
                data = data.replace("'", "\"")
                print(str(data)) # log
                data = json.loads(data) # convert data to json(dict)
                manage(data, self.c_socket, self.addr[0])
            except ConnectionResetError: # when connection is die
                self.c_socket.close() # close socket
                self.lst.remove(self) # remove self from client list
                break # break loop

    def c_send(self, data): # send data to client
        self.c_socket.send(data.encode()) # send data to client

def create_thread(s_sck): # create new c_sck thread
    c_sck_lst.append(c_sck(s_sck, c_sck_lst)) # make c_sck object and append it to client socket list
    c_sck_lst[-1].daemon = True # set daemon
    c_sck_lst[-1].start() # start

c_sck_lst = [] # initialize client socket list
s_sck = socket(AF_INET, SOCK_STREAM) # initialize server socket
host = '0.0.0.0' # set host
port = 5500 # set port
max_listen = 100 # set maximum listen size
s_sck.bind((host, port)) # bind
s_sck.listen(max_listen) # listen
create_thread(s_sck) # create new c_sck thread

while True: # repeat
    inp = input() # input data
    if inp == 'q': # if input is 'q' then
        break # break server
    else: # else
        try: 
            for i in c_sck_lst: # to all clients
                i.c_send(inp.encode()) # send input msg
        except Exception as e: # when exception occurs
            # make log
            continue # repeat loop

for j in c_sck_lst: # when break server, to all clients
    try:
        j.c_socket.close() # close all clients
    except Exception as e:
        pass

s_sck.close() # close server socket