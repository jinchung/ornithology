"""
NYT User: Jin's email
NYT Pwd: ornithology
Application Registration Name: Ornithology
Times Newswire API Key: 7831b763eca627bc9b2967a43cb8a5e6:3:67531365
"""

import json
import pycurl
import time

import producer

class NYTProducer(producer.Producer):
    """
    Base producer class for NYT API
    """

    def __init__(self, msg_queue):
        super(NYTProducer, self).__init__(msg_queue)

        self.attributes = ['title', 'abstract', 'updated_date', 'geo_facet']
        self.date_format = '%Y-%m-%dT%H:%M:%S'

        self.apikey = '7831b763eca627bc9b2967a43cb8a5e6:3:67531365'

        self.buffer = ""
        self.stream_url = ("http://api.nytimes.com/svc/news/v3/content/all"
                          "/all.json?api-key=" + self.apikey)
        self.conn = pycurl.Curl()
        self.conn.setopt(pycurl.URL, self.stream_url)
        self.conn.setopt(pycurl.WRITEFUNCTION, self.write_function)

    def run(self):
        while True:
            self.conn.perform()
            if self.buffer:
                content = json.loads(self.buffer)
                for msg in content["results"]:
                    self.msg_queue.put(self.map(msg))
            self.buffer = ""
            time.sleep(20) # max allowed requests for NYT Newswire API
                           # is 5000 requests per day

    def write_function(self, data):
        """
        Callback for pycurl to write to buffer
        """
        self.buffer += data

    def map(self, msg):
        msg = {key:value for (key,value) in msg.items()
                if key in self.attributes}

        geo_facet = msg['geo_facet'][0] if msg['geo_facet'] else None
        
        source = 'NYT'
        #authorID
        #author
        #msgID
        color = self.colors['white']
        content = msg['title'] + ' - ' + msg['abstract']
        location = geo_facet
        timestamp = self.parse_time(msg['updated_date'], self.date_format)

        return self.map_to_std_msg(source, authorID, author, msgID, color,
                                   content, location, timestamp)

