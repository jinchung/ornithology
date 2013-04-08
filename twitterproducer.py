"""
Twitter subclass for pulling content from Twitter API
"""

import pycurl
import json

import producer

class TwitterProducer(producer.Producer):
    """
    Twitter subclass for pulling content from Twitter API
    """

    def __init__(self, username, password, msg_queue):
        super(TwitterProducer, self).__init__(msg_queue)

        self.date_format = '%a %b %d %H:%M:%S %Y'
        self.attributes = ['text', 'coordinates', 'created_at']

        self.stream_url = 'https://stream.twitter.com/1.1/statuses/sample.json'
        self.username = username
        self.password = password
        self.buffer = ""
        self.conn = pycurl.Curl()
        self.conn.setopt(pycurl.USERPWD,
                         "%s:%s" % (self.username, self.password))
        self.conn.setopt(pycurl.URL, self.stream_url)
        self.conn.setopt(pycurl.WRITEFUNCTION, self.on_receive)

    def run(self):
        self.conn.perform()

    def on_receive(self, data):
        """
        Behavior on the receival of content from Twitter
        """

        self.buffer += data
        content = json.loads(self.buffer)
        self.buffer = ""

        if 'text' in content.keys():
            self.msg_queue.put(self.map(content))

    def map(self, tweet):
        tweet = {
                    key:value
                    for
                    (key,value)
                    in
                    tweet.items()
                    if
                    key
                    in
                    self.attributes
                }

        result = {
                    'source': 'twitter',
                    'color':self.colors['green'],
                    'content':tweet['text'],
                    'location':tweet['coordinates']
                 }

        result['timestamp'] = self.parse_time(tweet['created_at'],
                                              self.date_format)
        return result

