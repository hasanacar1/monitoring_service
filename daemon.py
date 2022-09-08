#!/usr/bin/env python
# (C) Copyright 2015-2017 Hewlett Packard Enterprise Development LP
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# Core modules
import glob
import io
import logging
import os
import pstats
import signal
import sys
import time

from common import util
from collector import Collector

# todo the collector has daemon code but is always run in foreground mode
# from the supervisor, is there a reason for the daemon code then?
class CollectorDaemon():

    """The agent class is a daemon that runs the collector in a background process.

    """
    def __init__(self):
        self.run_forever = True
        self.collector = None
        self.start_event = True
        

    def run(self, config):
        # Load the checks_d checks
        checksd = util.load_check_directory()

        print("-- check directory was loaded")
        print("Cheksd : {x}".format(x=checksd))

        self.collector = Collector(config, checksd)

        check_frequency = 15

        # Initialize the auto-restarter
        self.agent_start = time.time()

        # Run the main loop.
        while self.run_forever:
            collection_start = time.time()

            # Do the work.
            print("Collector run at {x}".format(x = collection_start))
            self.collector.run(check_frequency)

            # Only plan for the next loop if we will continue,
            # otherwise just exit quickly.
            if self.run_forever:
                collection_time = time.time() - collection_start
                if collection_time < check_frequency:
                    time.sleep(check_frequency - collection_time)


def main():
    print("-- Main function started")
    collector_config = {'Main': {'check_freq': 15,
                'forwarder_url': 'http://localhost:17123',
                'hostname': None,
                'dimensions': None,
                'listen_port': None,
                'version': '',
                'additional_checksd': '/usr/lib/monasca/agent/custom_checks.d',
                'limit_memory_consumption': None,
                'skip_ssl_validation': False,
                'autorestart': True,
                'non_local_traffic': False,
                'sub_collection_warn': 6,
                'collector_restart_interval': 24},
        'Api': {'is_enabled': False,
                'url': '',
                'project_name': '',
                'project_id': '',
                'project_domain_name': '',
                'project_domain_id': '',
                'ca_file': '',
                'insecure': False,
                'username': '',
                'password': '',
                'use_keystone': True,
                'keystone_timeout': 20,
                'keystone_url': '',
                'max_buffer_size': 1000,
                'max_measurement_buffer_size': -1,
                'write_timeout': 10,
                'backlog_send_rate': 5,
                'max_batch_size': 0},
        'Statsd': {'recent_point_threshold': None,
                    'monasca_statsd_interval': 20,
                    'monasca_statsd_forward_host': None,
                    'monasca_statsd_forward_port': 8125,
                    'monasca_statsd_port': 8125},
        'Logging': {'disable_file_logging': False,
                    'log_level': None,
                    'collector_log_file': '/collector.log',
                    'forwarder_log_file': '/forwarder.log',
                    'statsd_log_file':  '/statsd.log',
                    'jmxfetch_log_file': '/jmxfetch.log',
                    'enable_logrotate': True,
                    'log_to_event_viewer': False,
                    'log_to_syslog': False,
                    'syslog_host': None,
                    'syslog_port': None}}


    agent = CollectorDaemon()

    print("-- agent object was created by using CollectorDaemon")

    agent.run(collector_config)

    return 0



if __name__ == '__main__':

    sys.exit(main())

