"""
Message class to represent standard message format
"""
import json
import socket
import datetime

class Message(object):
    """
    Generic message format with type attribute
    """
    def __init__(self, msg_id, type):
        self.msg_id = type
        self.type = type

class MediaMessage(Message):
    """
    Standard media message format
    """
    def __init__(self, msg_id, source, content, timestamp, 
                 type='media', author_id=None, author=None, 
                 color='white', location=None):
        """
        Create a dictionary of msg format from its inputs
        """
        super(MediaMessage, self).__init__(msg_id, type)
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
    def __init__(self, socket_, keywords):
        msg_id = ('connection_' + socket_.getsockname()[0] + '_' + 
                  str(datetime.datetime.utcnow()))
        super(ConnectionMessage, self).__init__(msg_id, 'connection')
        self.sock = socket_
        self.keywords = keywords

class DisconnectionMessage(Message):
    """
    Standard incoming connection request message
    """
    def __init__(self, socket_):
        msg_id = ('disconnection_' + socket_.getsockname()[0] + '_' +
                 str(datetime.datetime.utcnow())) 
        super(DisconnectionMessage, self).__init__(msg_id, 'disconnection')
        self.sock = socket_

class ShutdownSignal(Message):
    """
    Shutdown message type to notify consumer threads to exit
    """
    def __init__(self):
        msg_id = 'shutdown_' + str(datetime.datetime.utcnow())
        super(ShutdownSignal, self).__init__(msg_id, 'shutdown')

