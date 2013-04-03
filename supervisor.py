import sys
import processor
import Queue

"""
Spawn the twitter stream producer thread
Set up queue
Spawn consumer thread

Usage:
    $ python supervisor.py uSErName pa$$w0rd

    or

    $ python supervisor.py -D uSErName pa$$w0rd # for turning dev mode on


Development Twitter account is:
Username: ornitweet
Password: ornithology
"""

class Supervisor(object):
    def __init__(self, username, password, dev_mode):
        self.username = username
        self.password = password
        self.tweets_queue = Queue.Queue()
        self.dev_mode = dev_mode

    def launch(self):  
        p = processor.Processor(self.username, self.password, self.tweets_queue, self.dev_mode)
        p.start()

if __name__=="__main__":
    if len(sys.argv) == 3:
        _, username, password = sys.argv
        dev_mode = False
    elif len(sys.argv) == 4 and sys.argv[1] in ["-d","-D"]:
        _, dev_mode, username, password = sys.argv
        dev_mode = True
    else:
        print(supervisor.__doc__)

    Supervisor(username, password, dev_mode).launch()

