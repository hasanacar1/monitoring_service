# Copyright 2014 IBM Corp
# (C) Copyright 2015,2016 Hewlett Packard Enterprise Development LP
# Copyright 2017 Fujitsu LIMITED
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os

import falcon
#from monasca_common.simport import simport
# from oslo_config import cfg
# from oslo_log import log
import paste.deploy

# from monasca_api.api.core import request
#from monasca_api import config

from reference import metrics

# LOG = log.getLogger(__name__)
#CONF = config.CONF


def launch():
    #config.parse_args()

    #app = falcon.API(request_type=request.Request)
    app = falcon.API()
    # NOTE(dszumski): Falcon 2.0.0 switches the default for this from True
    # to False so we explicitly set it here to prevent the behaviour
    # changing between versions.
    app.req_options.strip_url_path_trailing_slash = True

    # versions = simport.load(cfg.CONF.dispatcher.versions)()
    # app.add_route("/", versions)
    # app.add_route("/{version_id}", versions)

    # The following resource is a workaround for a regression in falcon 0.3
    # which causes the path '/v2.0' to not route to the versions resource
    # version_2_0 = simport.load(cfg.CONF.dispatcher.version_2_0)()
    # app.add_route("/v2.0", version_2_0)

    # healthchecks = simport.load(cfg.CONF.dispatcher.healthchecks)()
    # app.add_route("/healthcheck", healthchecks)

    launch_metrics_api(app)

    # if cfg.CONF.enable_logs_api:
    #     launch_log_api(app)

    #LOG.debug('Dispatcher drivers have been added to the routes!')
    print('Dispatcher drivers have been added to the routes!')
    return app


def launch_metrics_api(app):
    #metrics = simport.load(cfg.CONF.dispatcher.metrics)()
    metrics_2 = metrics.Metrics()
    app.add_route("/v2.0/metrics", metrics_2)

    '''
    # metrics_measurements = simport.load(
    #     cfg.CONF.dispatcher.metrics_measurements)()
    metrics_measurements = reference.metrics.MetricsMeasurements()
    app.add_route("/v2.0/metrics/measurements", metrics_measurements)

    #metrics_statistics = simport.load(cfg.CONF.dispatcher.metrics_statistics)()
    metrics_statistics = reference.metrics.MetricsStatistics()
    app.add_route("/v2.0/metrics/statistics", metrics_statistics)

    #metrics_names = simport.load(cfg.CONF.dispatcher.metrics_names)()
    metrics_names = reference.metrics.MetricsNames()
    app.add_route("/v2.0/metrics/names", metrics_names)

    # alarm_definitions = simport.load(cfg.CONF.dispatcher.alarm_definitions)()
    # app.add_route("/v2.0/alarm-definitions/", alarm_definitions)
    # app.add_route("/v2.0/alarm-definitions/{alarm_definition_id}",
    #               alarm_definitions)

    # alarms = simport.load(cfg.CONF.dispatcher.alarms)()
    # app.add_route("/v2.0/alarms", alarms)
    # app.add_route("/v2.0/alarms/{alarm_id}", alarms)

    # alarm_count = simport.load(cfg.CONF.dispatcher.alarms_count)()
    # app.add_route("/v2.0/alarms/count/", alarm_count)

    # alarms_state_history = simport.load(
    #     cfg.CONF.dispatcher.alarms_state_history)()
    # app.add_route("/v2.0/alarms/state-history", alarms_state_history)
    # app.add_route("/v2.0/alarms/{alarm_id}/state-history",
    #               alarms_state_history)

    # notification_methods = simport.load(
    #     cfg.CONF.dispatcher.notification_methods)()
    # app.add_route("/v2.0/notification-methods", notification_methods)
    # app.add_route("/v2.0/notification-methods/{notification_method_id}",
    #               notification_methods)

    #dimension_values = simport.load(cfg.CONF.dispatcher.dimension_values)()
    dimension_values = reference.metrics.DimensionValues()
    app.add_route("/v2.0/metrics/dimensions/names/values", dimension_values)

    #dimension_names = simport.load(cfg.CONF.dispatcher.dimension_names)()
    dimension_names = reference.metrics.DimensionNames()
    app.add_route("/v2.0/metrics/dimensions/names", dimension_names)

    # notification_method_types = simport.load(
    #     cfg.CONF.dispatcher.notification_method_types)()
    # app.add_route("/v2.0/notification-methods/types", notification_method_types)
    '''

# def launch_log_api(app):
#     logs = simport.load(
#         cfg.CONF.dispatcher.logs)()
#     app.add_route("/v2.0/logs", logs)


# def get_wsgi_app(config_base_path=None, **kwargs):

#     # allow to override names of the configuration files
#     config_file = kwargs.get('config_file', 'monasca-api.conf')
#     paste_file = kwargs.get('paste_file', 'api-config.ini')

#     # if config_base_path is None:
#     #     # allow monasca-api to be run in dev mode from __main__
#     #     config_base_path = os.path.join(
#     #         os.path.dirname(os.path.realpath(__file__)), '../../etc')

#     config_file = os.path.join(config_base_path, config_file)
#     global_conf = {'config_file': config_file}

#     # LOG.debug('Initializing WSGI application using configuration from %s',
#     #           config_base_path)
#     print("Initializing WSGI application using configuration from {}".format(config_base_path))

#     print(paste_file)
#     print(config_base_path)
#     print(global_conf)

#     return (
#         paste.deploy.loadapp(
#             'config:%s' % paste_file,
#             relative_to=config_base_path,
#             global_conf=global_conf
#         )
#     )


def get_wsgi_app():
    #if __name__ == '__main__':
    from wsgiref import simple_server
    wsgi_app = launch()
    httpd = simple_server.make_server('127.0.0.1', 8071, wsgi_app)
    httpd.serve_forever()
