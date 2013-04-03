import pycurl
import json
import threading
import Queue
import pickle

class Processor(threading.Thread):

    def __init__(self, username, password, tweets_queue, dev_mode):
        threading.Thread.__init__(self)
        self.tweets_queue = tweets_queue
        self.dev_mode = dev_mode
        if not self.dev_mode:
            self.stream_url = 'https://stream.twitter.com/1.1/statuses/sample.json'
            self.username = username
            self.password = password
            self.attributes = ['text', 'id', 'coordinates', 'created_at']
            self.buffer = ""
            self.conn = pycurl.Curl()
            self.conn.setopt(pycurl.USERPWD, "%s:%s" % (self.username, self.password))
            self.conn.setopt(pycurl.URL, self.stream_url)
            self.conn.setopt(pycurl.WRITEFUNCTION, self.on_receive)

    def run(self):
        if not self.dev_mode:
            self.conn.perform()
        else:
            print("\n%%%%% Executing in DEV mode %%%%%\n")
            tweets = pickle.load(open("tweets.p","rb"))
            for tweet in tweets:
                self.tweets_queue.put(tweet)
                print(json.dumps(tweet, indent=4, separators=(',', ': ')))

    def on_receive(self, data):
        self.buffer += data
        #if data.endswith("rn") and self.buffer.strip():
        content = json.loads(self.buffer)
        self.buffer = ""

        if 'text' in content.keys():
            res = {key:value for (key,value) in content.items() if key in self.attributes}
            self.tweets_queue.put(res)
            print(json.dumps(res, indent=4, separators=(',', ': ')))

