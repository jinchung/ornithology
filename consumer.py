import threading
import Queue
import json
import datetime

COL1 = 10;
COL2 = 40;
COL3 = 20;

class Consumer(threading.Thread):

    def __init__(self, tweets_queue, keywords, update_metrics):
        threading.Thread.__init__(self)
        self.tweets_queue = tweets_queue
        self.keywords = keywords
        self.update_metrics_callback = update_metrics
        self.logfile = open('matched_tweets.log', 'w')
        self.date_format = '%a %b %d %H:%M:%S +0000 %Y'

    def run(self):
        while True:
            tweet = self.tweets_queue.get(True)
            text = set(tweet['text'].lower().split())
            matches = self.keywords.intersection(text)
            for match in matches:
                self.logfile.write(match.rjust(COL1) + tweet['created_at'].rjust(COL2) + str(tweet["coordinates"]).rjust(COL3) + '\n')
                self.logfile.flush()
            self.update_metrics_callback(self.calculate_latency(tweet['created_at']))

    def calculate_latency(self, tweet_timestamp):
        now = datetime.datetime.utcnow()
        delta = now - datetime.datetime.strptime(tweet_timestamp, self.date_format)
        return delta.total_seconds()
        
