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
import logging
from multiprocessing.dummy import Pool
import os
import socket
import sys
import threading
import time

import common.metrics
from common import util
from common import emitter


log = logging.getLogger(__name__)


MAX_THREADS_COUNT = 50
MAX_CPU_PCT = 10
FLUSH_LOGGING_PERIOD = 10
FLUSH_LOGGING_INITIAL = 5


class Collector(util.Dimensions):

    """The collector is responsible for collecting data from each check and

    passing it along to the emitters, who send it to their final destination.
    """

    def __init__(self, agent_config, checksd):
        super(Collector, self).__init__(agent_config)
        self.agent_config = agent_config
        self.plugins = None
        socket.setdefaulttimeout(15)
        self.run_count = 0
        self.continue_running = True
        self.collection_metrics = {}

        # is of type {check_name: check}
        initialized_checks_d = checksd['initialized_checks']

        self.pool_size = 1
        log.info('Using %d Threads for Collector' % self.pool_size)
        self.pool = Pool(self.pool_size)
        self.pool_full_count = 0
        self.collection_times = {}
        self.collection_results = {}
        self.collect_runs = 0

        self.check_name_list = list()
        for check in initialized_checks_d:
            self.check_name_list.append(check)
            
        self.pool_full_max_retries = 4


    def run(self, check_frequency):
        """Collect data from each check and submit their data.

        Also, submit a metric which is how long the checks_d took
        """

        # checks_d checks
        self.run_checks_d(check_frequency)

        dimensions = {'component': 'monasca-agent', 'service': 'monitoring'}


    def run_single_check(self, check):
        """Run a single check

        returns number of measurement collected, collection time
        """
        # Run the check.
        print("Check run for {}".format(check))
        check.run()

        current_check_metrics = check.get_metrics()
        self._emit(current_check_metrics)
        print(current_check_metrics)
        print("-------------------------")
        print("-------------------------")
        print("-------------------------")


    def start_checks_in_thread_pool(self, start_time):
        """Add the checks that are not already running to the Thread Pool
        """

        # Sort by the last collection time so the checks that take the
        # least amount of time are run first so they are more likely to
        # complete within the check_frequency

        for check in self.check_name_list:
            # print('*******************')
            # print(check)
            # print('*******************')
            async_result = self.pool.apply_async(self.run_single_check, [check])
            self.collection_results[check.name] = {'result': async_result,
                                                   'start_time': start_time}

            # print("Async Result : {x}".format(x = self.collection_results))

    def run_checks_d(self, check_frequency):
        """Run defined checks_d checks using the Thread Pool.

        returns number of Measurements.
        """
        start_time = time.time()
        self.start_checks_in_thread_pool(start_time)

    
    def _emit(self, payload):
        """Send the payload via the emitter.
        """
        print("emit_step_1")
        #emitter.http_emitter(payload, 'http://localhost:17123')
        emitter.http_emitter(payload, self.agent_config['Main']['forwarder_url'])
