import socket
import json

COL1 = 10
COL2 = 15
COL3 = 30
COL4 = 15

class Client(object):

    def __init__(self, host, port, keywords):
        self.keywords = keywords
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.pretty_file = open('logs/pretty_log.txt', 'w')
        self.sock.sendall(self.keywords)

    def start(self):
        while True:
            msg = self.sock.recv(20000)
            if msg:
                print msg

    def pretty_print(self, matches, msg):
        """
        Format each match and print them to pretty file
        """
        for match in matches:
            row = match.rjust(COL1)
            row += (self.colors[msg.color] +
                        msg.source.rjust(COL2) + self.colors['end'])
            row += str(msg.timestamp).rjust(COL3)
            row += str(msg.location).rjust(COL4)
            row += '\n'
            self.pretty_file.write(row)
            self.pretty_file.flush()

if __name__ == "__main__":
    host = 'localhost'
    #host = 'alexandre-1225B.local'
    port = 1234
    keywords = 'death oil party boy girl tonight fun cool interest rate climbing people' 
    client = Client(host, port, keywords)
    client.start()
