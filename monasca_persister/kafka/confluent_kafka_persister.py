#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

from repositories import persister
#from repositories import singleton

import os, sys, inspect

#currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname('/opt/stack/monitoring_service/monasca_persister')
sys.path.insert(0,parentdir)

os.chdir('../')


from monasca_common import client_factory


class ConfluentKafkaPersister(persister.Persister):

    def __init__(self, client_id=""):
        super(ConfluentKafkaPersister, self).__init__()
        self._consumer = client_factory.get_kafka_consumer(
            kafka_url='10.8.134.107:9092',
            kafka_consumer_group='1_metrics',
            kafka_topic='metrics',
            client_id=client_id,
            repartition_callback=ConfluentKafkaPersister.flush,
            commit_callback=self._flush,
            max_commit_interval=30
        )

    @staticmethod
    def flush(kafka_consumer, partitions):
        p = ConfluentKafkaPersister()
        p._flush()
