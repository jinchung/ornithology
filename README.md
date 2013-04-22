#Ornithology

Ornithology's purpose is for real-time monitoring of 
arbitrary keywords in popular social media. 

Currently, the sources are Twitter, Facebook, and the New York Times.

##Architecture
###supervisor
* Entry point of the application
* Spawns all producer threads and the consumer thread
* Manages application metrics (total message count, throughput, queue size, latency)
* Listen for client connections / disconnections

###producers
* Abstract class implemented by subclasses for each social media
* Manages connections to external APIs and pushes data to consumer via queue
* replayproducer is a special producer for dev mode which replays saved messages

###consumer
* Single consumer which reads data from producers and searches for keywords
specified by clients 
* Dispatches matching messages to relevant clients 
* Updates metrics after processing messages

###messages
The supervisor communicates with the clients via a shared queue of messages
* Media - standard message for social media input
* Connection - new connection request from client
* Disconnection - disconnection from client
* ShutdownSignal - termination of application

##Installation
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
* update README given websocket changes
* fix the clean exit

###Concurrency Model
* Testing should not be the same as dev mode
* Create consumer vs dispatcher model
* Manage dev mode for setting up fake initial connection msg for replay prod
* supervisor select should not wait for metrics to occur before reading any other selects - shouldn't be in same while loop
* Consumer to have tokenizer functionality
* Separate out concurrency model concerns (msg queue, periodic execution for monitoring)
* Various concurrency models in separate class - config to switch between them

###Client-side
* more hygienic handling of buffer input
* Frontend visualization
* Pretty logging?

###Long-Term TBD
* More architecture thought needed for having monitors as downstream consumers
* Test suite / unit testing
* Add one or two more APIs
* Indexing on incoming data (hashing)
* Zope.interface

