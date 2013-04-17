"""
Message class to represent standard message format
"""
import json

class Message(object):
    """
    Generic message format with type attribute
    """
    def __init__(self, type):
        self.type = type

class MediaMessage(Message):
    """
    Standard media message format
    """
    def __init__(self, source, content, timestamp, msg_id=None,
                author_id=None, author=None, color='white', location=None):
        """
        Create a dictionary of msg format from its inputs
        """
        super(MediaMessage, self).__init__('media')
        self.source = source 
        self.content = content 
        self.timestamp = timestamp
        self.msg_id = msg_id
        self.author_id = author_id
        self.author = author
        self.color = color
        self.location = location

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
    def __init__(self, socket, keywords):
        super(ConnectionMessage, self).__init__('connection')
        self.socket = socket
        self.keywords = keywords

class DisconnectionMessage(Message):
    """
    Standard incoming connection request message
    """
    def __init__(self, socket):
        super(DisconnectionMessage, self).__init__('disconnection')
        self.socket = socket

class ShutdownSignal(Message):
    """
    Shutdown message type to notify consumer threads to exit
    """
    def __init__(self):
        super(ShutdownSignal, self).__init__('shutdown')

