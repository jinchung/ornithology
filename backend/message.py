"""
Message class to represent standard message format
"""
import json
import datetime

class Message(object):
    """
    Generic message format with type attribute
    """
    def __init__(self, msg_id, msg_type):
        self.msg_id = msg_id
        self.type = msg_type

class MediaMessage(Message):
    """
    Standard media message format
    """
    def __init__(self, msg_id, source, content, timestamp, 
                 msg_type='media', author_id=None, author=None, 
                 color='white', location=None):
        """
        Create a dictionary of msg format from its inputs
        """
        super(MediaMessage, self).__init__(msg_id, msg_type)
        self.source = source 
        self.content = content 
        self.timestamp = timestamp
        self.author_id = author_id
        self.author = author
        self.color = color
        self.location = location
    
    def to_dict(self):
        """
        Transforms standard message into dict
        """
        tmp = dict(self.__dict__)
        tmp['timestamp'] = str(tmp['timestamp'])
        return tmp

    def to_json(self):
        """
        Transforms standard message into json string format
        """
        tmp = dict(self.__dict__)
        tmp['timestamp'] = str(tmp['timestamp'])
        return json.dumps(tmp)

class ConnectionMessage(Message):
    """
    Standard incoming connection request message
    """
    def __init__(self, client, keywords):
        msg_id = ('connection_' + client.peerstr + '_' + 
                  str(datetime.datetime.utcnow()))
        super(ConnectionMessage, self).__init__(msg_id, 'connection')
        self.client = client
        self.keywords = keywords

class DisconnectionMessage(Message):
    """
    Standard incoming connection request message
    """
    def __init__(self, client):
        msg_id = ('disconnection_' + client.peerstr + '_' +
                 str(datetime.datetime.utcnow())) 
        super(DisconnectionMessage, self).__init__(msg_id, 'disconnection')
        self.client = client

class ShutdownSignal(Message):
    """
    Shutdown message type to notify consumer threads to exit
    """
    def __init__(self):
        msg_id = 'shutdown_' + str(datetime.datetime.utcnow())
        super(ShutdownSignal, self).__init__(msg_id, 'shutdown')

