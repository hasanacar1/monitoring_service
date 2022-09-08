# (C) Copyright 2014-2017 Hewlett Packard Enterprise Development LP
# Copyright 2017 FUJITSU LIMITED
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Persister Module

   The Persister reads metrics and alarms from Kafka and then stores them
   in into either Influxdb or Cassandra

   Start the perister as stand-alone process by running 'persister.py
   --config-file <config file>'
"""
import multiprocessing
import os
import signal
import sys
import time

#from oslo_config import cfg
from oslo_log import log

from repositories.influxdb.metrics_repository import MetricInfluxdbRepository
from kafka import confluent_kafka_persister


LOG = log.getLogger(__name__)

processors = []  # global list to facilitate clean signal handling
exiting = False


def start_process():
    LOG.warning("Process Start")
    m_persister = confluent_kafka_persister.ConfluentKafkaPersister()
    LOG.warning("Persister Object")
    LOG.warning(m_persister)
    m_persister.run()

def prepare_processes():
    processors.append(multiprocessing.Process(
                 target=start_process))

def main():
    """Start persister."""

    prepare_processes()

    # Start
    try:
        for process in processors:
            process.start()

        while True:
            time.sleep(10)

    except Exception:
        LOG.exception('Error! Exiting.')


if __name__ == "__main__":
    sys.exit(main())
