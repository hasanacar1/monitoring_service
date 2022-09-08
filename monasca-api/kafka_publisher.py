# Copyright 2014,2017 Hewlett-Packard
#
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

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

os.chdir('../')

from monasca_common import client_factory

#import monasca_common.kafka_lib.common as kafka_common
from oslo_config import cfg
#from oslo_log import log

#from monasca_api.common.messaging import exceptions
import publisher

#LOG = log.getLogger(__name__)
'''
class KafkaPublisher(publisher.Publisher):
    def __init__(self, topic):
        self.topic = topic

    def send_message(self, message):
        print("*******************")
        print({self.topic})
        print("*******************")

'''
class KafkaPublisher(publisher.Publisher):
    def __init__(self, topic):

        self.uri = '10.8.134.107:9092'
        self.topic = 'metrics'
        self.group = 'api'
        self.wait_time = 1
        self.is_async = True
        self.ack_time = 20
        self.max_retry = 3
        self.auto_commit = False
        self.compact = True
        #self.partitions = 3
        self.drop_data = False

        if not self.uri:
            raise Exception('Kafka is not configured correctly! '
                            'Use configuration file to specify Kafka '
                            'uri, for example: '
                            'uri=192.168.1.191:9092')

        config = {'queue.buffering.max.messages':
                  1000}
        self._producer = client_factory.get_kafka_producer(
            self.uri, False, **config)


    def close(self):
        pass
    
    def send_message(self, message):

        self._producer.publish(self.topic, message)

        
    # def send_message(self, message):
    #     try:
    #         self._producer.publish(self.topic, message)

    #     except (kafka_common.KafkaUnavailableError,
    #             kafka_common.LeaderNotAvailableError):
    #         LOG.exception('Error occurred while posting data to Kafka.')
    #         raise exceptions.MessageQueueException()
    #     except Exception:
    #         LOG.exception('Unknown error.')
    #         raise exceptions.MessageQueueException()