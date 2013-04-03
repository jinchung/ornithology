
import threading
import Queue
import json

COL1 = 10;
COL2 = 40;
COL3 = 20;

class Consumer(threading.Thread):

    def __init__(self, tweets_queue, keywords):
        threading.Thread.__init__(self)
        self.tweets_queue = tweets_queue
        self.keywords = keywords

    def run(self):

        print "Keyword".rjust(COL1), "Time".rjust(COL2), "Place".rjust(COL3)              
        print "===========================================================================" 
        while True:
            tweet = self.tweets_queue.get(True)
            text = set(tweet['text'].lower().split())
            matches = self.keywords.intersection(text)
            for match in matches:
                print match.rjust(COL1), tweet['created_at'].rjust(COL2), str(tweet["coordinates"]).rjust(COL3)

