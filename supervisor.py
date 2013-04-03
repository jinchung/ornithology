import sys
import processor
import Queue

"""
Spawn the twitter stream producer thread
Set up queue
Spawn consumer thread

Development Twitter account is:
Username: ornitweet
Password: ornithology
"""

class Supervisor(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.tweets = Queue.Queue()

    def launch(self):  
        p = processor.Processor(self.username, self.password, self.tweets)
        p.start()

if __name__=="__main__":
    _, username, password = sys.argv
    Supervisor(username, password).launch()

