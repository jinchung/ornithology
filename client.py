import socket
import json

class Client(object):

    def __init__(self, host, port, keywords):
        self.keywords = keywords
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.sock.sendall(self.keywords)
        self.template = u'{0:^80}{1:^30}{2:^30}'
        print self.template.format('Content', 'Source', 'Timestamp')
        self.template = u'{0:<80}{1:^30}{2:^30}'
        self.colors = {
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m', 
            'purple': '\033[35m',
            'cyan': '\033[36m',
            'white': '\033[37m',
            'end': '\033[0m'
        }

    def start(self):
        while True:
            payload = self.sock.recv(20000)
            if payload:
                msgs = '[' + payload + ']'
                msgs = msgs.replace('}{', '},{')  
                msgs = json.loads(msgs)
                for msg in msgs:
                    self.pretty_print(msg)

    def pretty_print(self, msg):
        """
        Format each match and pretty print them
        """
        content = msg['content'][:75] + '...'
        content_length = len(content)
        source = (self.colors[msg['color']] + 
                  msg['source'] + self.colors['end'])

        aux = ''
        for word in content.split():
            if word.lower() in msg['keywords']:
                #aux += self.colors['green'] + word + self.colors['end'] + ' '
                aux += self.colors['red'] + word + self.colors['end'] + ' '
            else:
                aux += word + ' '

        print aux + self.template.format(content, source, msg['timestamp'])[content_length:]

if __name__ == "__main__":
    host = 'localhost'
    #host = 'alexandre-1225B.local'
    port = 1234
    keywords = 'death oil party boy girl tonight fun cool interest rate climbing people' 
    client = Client(host, port, keywords)
    client.start()
