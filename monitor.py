"""
Monitor for application metrics
"""
import datetime

class Monitor(object):

    def __init__(self):
        self.qlength = 0
        self.num_msg = 0
        self.throughput = 0.0
        self.latency = 0.0
        self.num_clients = 0
   
        self.old_timestamp = datetime.datetime.utcnow()
        self.old_num_msg = 0

        template = '{0:^25}{1:^25}{2:^25}{3:^15}{4:^15}'
        print '\n'
        print template.format('Cumulative # of Msgs', 'Throughput (msg/s)', 
                                   'Queue Length (msgs)', 'Latency (s)',
                                   'Num of Clients')
        
    def update(self, qsize):
        """
        Start monitoring of system metrics
        """
        self.qlength = qsize
        
        now = datetime.datetime.utcnow()
        time_delta = now - self.old_timestamp
        num_msg_delta = self.num_msg - self.old_num_msg
        self.throughput = (num_msg_delta / time_delta.total_seconds())
        self.old_timestamp = now
        self.old_num_msg = self.num_msg

        self.print_metrics()
   
    def inc_clients(self):
        self.num_clients += 1

    def dec_clients(self):
        self.num_clients -= 1
     
    def metrics_callback(self, latency):
        """
        Callback to consumer to update metrics
        """
        self.num_msg += 1
        self.latency = latency
    
    def print_metrics(self):
        """
        Pretty print metrics to shell
        """
        template = '{0:^25}{1:^25.2f}{2:^25}{3:^15.2f}{4:^15}'
        print template.format(self.num_msg, self.throughput, 
                              self.qlength, self.latency, self.num_clients)
        #row += "{0:.2f}".format().rjust(20)
        #row += str().rjust(20)
        #row += "{0:.2f}".format).rjust(20)
        #row += str(self.num_clients).rjust(20)
        #print row
    
