
import pycurl
import pickle
import datetime
import json

import processor

class TwitterProcessor(processor.Processor):

    def __init__(self, username, password, msg_queue, dev_mode):
        super(TwitterProcessor, self).__init__(msg_queue, dev_mode)

        self.date_format = '%a %b %d %H:%M:%S +0000 %Y'
        self.attributes = ['text', 'coordinates', 'created_at']

        if not self.dev_mode:
            self.stream_url = 'https://stream.twitter.com/1.1/statuses/sample.json'
            self.username = username
            self.password = password
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
                self.msg_queue.put(self.map(tweet))

    def on_receive(self, data):
        self.buffer += data
        content = json.loads(self.buffer)
        self.buffer = ""

        if 'text' in content.keys():
            self.msg_queue.put(self.map(content))

    def map(self, tweet):
        tweet = {key:value for (key,value) in tweet.items() if key in self.attributes}
        result = {'source': 'twitter', 'content':tweet['text'], 'location':tweet['coordinates']}
        result['timestamp'] = datetime.datetime.strptime(tweet['created_at'], self.date_format)
        return result

