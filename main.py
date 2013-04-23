
from twisted.internet import reactor
from twisted.internet import task

from autobahn.websocket import listenWS

import argparse
import ConfigParser
import signal

import server
import monitor

def parse_args():
    """
    Argument setup and parsing
    """
    parser = argparse.ArgumentParser()
   
    parser.add_argument('-d', '--dev',
                        help='Specify dev mode or not (default is PROD)',
                        action='store_true')

    return parser.parse_args()

def get_config():
    """
    Retrieve and parse system config file
    """
    config = ConfigParser.RawConfigParser()
    config.read('ornithology.cfg')
    return {section:dict(config.items(section)) 
            for section in config.sections()}

def clean_exit(*unused):
    server_factory.clean_exit()
    reactor.stop()

if __name__ == "__main__":
    ARGS = parse_args()
    CONFIG = get_config()

    monitor_host = CONFIG['MonitorSocket']['host']
    monitor_port = CONFIG['MonitorSocket']['port']
    monitor_url = 'ws://' + monitor_host + ':' + monitor_port

    monitor_factory = monitor.MonitorServerFactory(monitor_url)
    monitor_factory.protocol = monitor.MonitorServerProtocol
    listenWS(monitor_factory)

    server_host = CONFIG['ServerSocket']['host']
    server_port = CONFIG['ServerSocket']['port']
    server_url = 'ws://' + server_host + ':' + server_port

    server_factory = server.ServerFactory(server_url, monitor_factory, CONFIG, ARGS.dev)
    signal.signal(signal.SIGINT, clean_exit)
    server_factory.protocol = server.ServerProtocol
    server_factory.setup()
    listenWS(server_factory)

    monitor_task = task.LoopingCall(server_factory.monitor_callback)
    monitor_task.start(1)
    reactor.run()

