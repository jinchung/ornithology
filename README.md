#Ornithology

Ornithology's purpose is for real-time monitoring of 
arbitrary keywords in popular social media. 

Currently, the sources are Twitter, Facebook, and the New York Times.

##Architecture
###main
* Entry point of the application
* Parse arguments and application config file
* Launch Twisted reactor event loop
* Launch server and monitor
* Initiate clean exit 

###server
* Spawns all producer threads and the consumer thread
* Listen for client connections / disconnections

###monitor
* Manages application metrics (total message count, throughput, queue size, latency)
* Listen for admin connections / disconnections
* Broadcast metrics to admin pages

###producers
* Abstract class implemented by subclasses for each social media
* Manages connections to external APIs and pushes data to consumer via queue
* replayproducer is a special producer for dev mode which replays saved messages

###consumer
* Single consumer which reads data from producers and searches for keywords
specified by clients 
* Dispatches matching messages to relevant client websockets 
* Updates metrics after processing messages

###messages
The supervisor communicates with the clients via a shared queue of messages
* Media - standard message for social media input
* Connection - new connection request from client
* Disconnection - disconnection from client
* ShutdownSignal - termination of application

##Installation
###Configuration File
* Application uses Python ConfigParser
* Contains social media accounts
* Server and Monitor sockets

Example config file looks like:
<pre>
[Twitter]
username : exampleUser
password : examplePwd

[NYT]
email :  exampleUser
password : examplePwd

api\_key : sampleApiKey1234567890

[ServerSocket]
host : 12.3.45.67
port : 9000

[MonitorSocket]
host : 12.3.45.67
port : 8888
</pre>

###Requirements
Ornithology requires Twisted, zope.interface, setuptools
<pre>
$ pip install -r requires.txt
</pre>

##Usage
<pre>
usage: supervisor.py [-h] [-d]

optional arguments:
  -h, --help  show this help message and exit
  -d, --dev   Specify dev mode or not (default is PROD)
</pre>

##Wish List (in order)
###Concurrency Model
* thread unsafe datetime.strptime http://bugs.python.org/issue7980
* Testing should not be the same as dev mode
* Manage dev mode for setting up fake initial connection msg for replay prod
* Separate out concurrency model concerns (msg queue, periodic execution for monitoring)

###Client-side
* Frontend visualization

###Long-Term TBD
* More architecture thought needed for having monitors as downstream consumers
* Test suite / unit testing
* Add one or two more APIs
* Indexing on incoming data (hashing)

