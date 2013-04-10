#Ornithology

Exploring threading module in Python for a sample producer-consumer problem
with filtering API feeds for specified keywords. 

##Architecture
###supervisor
* Entry point of the application
* Spawns all producer threads and the consumer thread
* Manages benchmark metrics

###producer
* Abstract class implemented by subclasses for each social media
* Extends Thread class
* Manages connections to external APIs and pushes data to consumer via queue
* replayproducer is a special producer for dev mode which replays saved messages

###consumer
* Extends Thread class
* Single consumer which reads data from producers and searches for keywords
specified by user (or default)
* Updates metrics after processing messages

###output
* Application metrics (total message count, throughput, queue size, latency) are printed to the console
* Messages with matching keywords are saved in logs/pretty_log.txt
* Every message is appended as a json to logs/log.json

##Usage
<pre>
usage: supervisor.py [-h] [-u USERNAME] [-p PASSWORD] [-d]
                     [-k KEYWORDS [KEYWORDS ...]]

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Please enter username for social accounts
  -p PASSWORD, --password PASSWORD
                        Please enter password for social accounts
  -d, --dev             Specify dev mode or not (default is PROD)
  -k KEYWORDS [KEYWORDS ...], --keywords KEYWORDS [KEYWORDS ...]
                        Optional list of keywords withwhich to search social
                        media
</pre>

##Wish List (in order)
* Creating class for message dictionary with own to_json method (can't rely on __dict__ always)
* Hide API keys, username, password in config files in .gitignore or use an encryption library

* Separate out concurrency model concerns (generating producers, consumers, msg queue, periodic execution)
* Using generators for producers and consumers
* Anything in a while True loop: extract body into own method
* Various concurrency models in separate class - config to switch between them

* Composition > Inheritance - anything shared should be in separate class not just in parent
* Get rid of all subclassing of threading.Thread (use target)
* Supervisor class - breaking out the launch function
* Metrics should be separated into separate class (Monitor)
* Zope.interface

* Clean exit -add a signal handler to handle ctrl-C (send kill messages for each consumer into queue)
* Handling error of not having a logs directory

* More architecture thought needed for having monitors as downstream consumers
* Map / reduce behavior for funneling back in messages to write to logs without running into problems
* Pretty log and json log should be separate consumer classes
* Thinking about multiple users and hashing input

* Frontend visualization
* Test suite / unit testing
* Add one or two more APIs
* Indexing on incoming data

* Glyph - Touch upon benchmarking - are these good? Are they proper?
* Glyph - Dive deep into line by line for a weaker part of the app

