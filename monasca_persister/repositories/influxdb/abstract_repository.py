# (C) Copyright 2016-2017 Hewlett Packard Enterprise Development LP
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
import abc
import influxdb
#from oslo_config import cfg

from repositories import abstract_repository
from repositories import data_points

DATABASE_NOT_FOUND_MSG = "database not found"


class AbstractInfluxdbRepository(abstract_repository.AbstractRepository, metaclass=abc.ABCMeta):

    def __init__(self):
        super(AbstractInfluxdbRepository, self).__init__()
        self.database_name = 'mon'
        self._influxdb_client = influxdb.InfluxDBClient(
            'localhost',
            8086,
            'mon_persister',
            '1234qweR')
        self.db_per_tenant = False
        if self.db_per_tenant:
            self.data_points_class = data_points.DataPointsAsDict
        else:
            self.data_points_class = data_points.DataPointsAsList

    def write_batch(self, data_points):
        if self.db_per_tenant:
            for tenant_id, tenant_data_points in data_points.items():
                database = '%s_%s' % (self.database_name,
                                      tenant_id)
                self._write_batch(tenant_data_points, database)
        else:
            self._write_batch(data_points, self.database_name)

    def _write_batch(self, data_points, database):
        # NOTE (brtknr): Loop twice to ensure database is created if missing.
        for retry in range(2):
            try:
                batch_size = 10000
                self._influxdb_client.write_points(data_points, 'ms',
                                                   protocol='line',
                                                   database=database,
                                                   batch_size=batch_size)
                break
            except influxdb.exceptions.InfluxDBClientError as ex:
                # When a databse is not found, the returned exception resolves
                # to: {"error":"database not found: \"test\""}
                if DATABASE_NOT_FOUND_MSG in str(ex):
                    self._influxdb_client.create_database(database)
                    # NOTE (brtknr): Only apply default retention policy at
                    # database creation time so that existing policies are
                    # not overridden since administrators may want different
                    # retention policy per tenant.
                    default_retention_hours = 0
                    hours = default_retention_hours
                    if hours > 0:
                        rp = '{}h'.format(hours)
                        default_rp = dict(database=database, default=True,
                                          name=rp, duration=rp,
                                          replication='1')
                        self._influxdb_client.create_retention_policy(**default_rp)
                else:
                    raise
