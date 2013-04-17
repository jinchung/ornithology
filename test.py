import socket
import json

host = 'alexandre-1225B.local'
port = 1234

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))

default_keywords = 'death oil party boy girl tonight fun cool interest rate climbing people' 

sock.sendall(default_keywords)
while True:
    msg = sock.recv(20000)
    if msg:
        print msg
        #print json.loads(msg)
