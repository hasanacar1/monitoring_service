import psutil

import time

import requests
import json
import datetime
from check import AgentCheck
PROCESS_GAUGE = ('start_time',
                'period',
                'service',
                'process.thread_count',
                'process.cpu_perc',
                'process.mem.rss_mbytes',
                'process.open_file_descriptors',
                'process.io.read_count',
                'process.io.write_count',
                'process.io.read_kbytes',
                'process.io.write_kbytes')

class ProcessCheck(AgentCheck):
    def __init__(self, name, init_config, agent_config, instances=None):
        super(ProcessCheck, self).__init__(name, init_config, agent_config,
                                           instances)
        self.check_frequency = 15

    def _safely_increment_var(self, var, value):
            if var:
                return var + value
            else:
                return value


    def prepare_run(self):
        self.process_list = []
        self.service_name_list = []
        for process in psutil.process_iter():

            self.process_dict = process.as_dict(
                attrs=['name', 'pid', 'username', 'cmdline'])
            

            if self.process_dict not in self.process_list:
                self.service_name_list.append(self.process_dict['name'])
                self.process_list.append(self.process_dict)


    def check(self):
        #print("CHECK START")
        #print(self.service_name_list)
        data_list = []
        for service_name in self.service_name_list:
            total_thr = None
            total_cpu = None
            total_rss = None
            total_open_file_descriptors = None
            total_read_count = None
            total_write_count = None
            total_read_kbytes = None
            total_write_kbytes = None
            pid_list = []
            for process in self.process_list:
                if service_name == process['name']:
                    pid_list.append(process['pid'])
            
            # print("PID LIST")
            # print(service_name)
            # print(pid_list)
            for pid in pid_list:
                p = psutil.Process(pid)
                mem = p.memory_info_ex()
                #print(mem)

                try :
                    total_rss = self._safely_increment_var(total_rss, float(mem.rss / 1048576))
                    #print("TOTAL RSS")
                    #print(total_rss)
                except :
                    total_rss = 0
                
                try :
                    total_thr = self._safely_increment_var(total_thr, p.num_threads())
                    #print("TOTAL THR")
                    #print(total_thr)
                except :
                    total_thr = 0

                try :
                    total_open_file_descriptors = self._safely_increment_var(total_open_file_descriptors, float(p.num_fds()))
                
                    #print("total_open_file_descriptors")
                    #print(total_open_file_descriptors)
                except : 
                    total_open_file_descriptors = 0

                try : 
                    total_cpu = self._safely_increment_var(total_cpu, p.cpu_percent(interval=None))

                    #print("TOTAL cpu")
                    #print(total_cpu)
                except :
                    total_cpu = 0

                try : 
                    io_counters = p.io_counters()
                    #print("io_counters")
                    #print(io_counters)
                    total_read_count = self._safely_increment_var(
                            total_read_count, io_counters.read_count)
                    #print("total_read_count")
                    #print(total_read_count)        
                    total_write_count = self._safely_increment_var(
                            total_write_count, io_counters.write_count)
                    #print("total_write_count")
                    #print(total_write_count)
                    total_read_kbytes = self._safely_increment_var(
                            total_read_kbytes, float(io_counters.read_bytes / 1024))
                    total_write_kbytes = self._safely_increment_var(
                            total_write_kbytes, float(io_counters.write_bytes / 1024))
                except :
                    total_read_count = 0
                    total_write_count = 0
                    total_read_kbytes = 0
                    total_write_kbytes = 0

            start_time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

            data = dict(zip(PROCESS_GAUGE,
                        (start_time,
                        self.check_frequency,
                        service_name,
                        total_thr,
                        total_cpu,
                        total_rss,
                        total_open_file_descriptors,
                        total_read_count,
                        total_write_count,
                        total_read_kbytes,
                        total_write_kbytes)))
            data_list.append(data)
            #print("DATA LIST : {x}".format(x=data_list))
        
        return data_list           



