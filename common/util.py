import itertools
import os
import inspect
import importlib.util
import glob
import socket
import subprocess
import yaml


def load_module(name, path):
    module_spec = importlib.util.spec_from_file_location(
        name, path
    )
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module

def get_checksd_path():
    cur_path = os.path.dirname(os.path.realpath(__file__))
    cur_path = '/opt/stack/monitoring_service/'
    checksd_path = os.path.join(cur_path, 'checks_d')

    if os.path.exists(checksd_path):
        return checksd_path

def get_confd_path():
    cur_path = '/opt/stack/monitoring_service/'
    confd_path = os.path.join(cur_path, 'conf.d')

    if os.path.exists(confd_path):
        return confd_path


def load_check_directory():
    """Return the initialized checks from checks_d, and a mapping of checks that failed to
    initialize. Only checks that have a configuration
    file in conf.d will be returned.
    """

    from check import AgentCheck

    agent_config = {'check_freq': 15,
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
                'collector_restart_interval': 24}

    initialized_checks = {}
    init_failed_checks = {}

    checks_paths = []

    checksd_path = get_checksd_path()
    print(checksd_path)
    checks_paths.append(glob.glob(os.path.join(checksd_path, '*.py')))
    print(checks_paths)

    confd_path = get_confd_path()
    print(confd_path)
    # For backwards-compatability with old style checks, we have to load every
    # checks_d module and check for a corresponding config OR check if the old
    # config will "activate" the check.
    #
    # Once old-style checks aren't supported, we'll just read the configs and
    # import the corresponding check module
    for check in itertools.chain(*checks_paths):
        check_name = os.path.basename(check).split('.')[0]
        if check_name in initialized_checks or check_name in init_failed_checks:
            continue
      
        check_module = load_module('checksd_%s' % check_name, check)


        conf_path = os.path.join(confd_path, '%s.yaml' % check_name)
        # print("aaaaaaaaaaaa")
        # print(conf_path)
        # print("aaaaaaaaaaaa")
        f = open(conf_path)
        check_config = yaml.safe_load(f.read())
        # print("bbbbbbbbbbbbbbb")
        # print(check_config)
        # print("bbbbbbbbbbbbbbb")
        f.close()
        

        check_class = None
        classes = inspect.getmembers(check_module, inspect.isclass)

        for _, clsmember in classes:
            if clsmember == AgentCheck:
                continue
            if issubclass(clsmember, AgentCheck):
                check_class = clsmember
                if AgentCheck in clsmember.__bases__:
                    continue
                else:
                    break

        if not check_class:
            if not check_name == '__init__':
                continue
        

        # Init all of the check's classes with
        init_config = check_config.get('init_config', {})
        # print("ccccccccccccccc")
        # print(init_config)
        # print("cccccccccccccc")
        # init_config: in the configuration triggers init_config to be defined
        # to None.

        if init_config is None:
            init_config = {}

        instances = check_config['instances']
        # print("ddddddddddddddd")
        # print(instances)
        # print("ddddddddddddddd")
        try:
            try:
                c = check_class(check_name, init_config=init_config,
                                agent_config=agent_config, instances=instances)
            except TypeError:
                # Backwards compatibility for checks which don't support the
                # instances argument in the constructor.
                c = check_class(check_name, init_config=init_config,
                                agent_config=agent_config)
                c.instances = instances
        except Exception as e:
            traceback_message = ""
            init_failed_checks[check_name] = {'error': e, 'traceback': traceback_message}
        else:
            initialized_checks[check_name] = c

    return {'initialized_checks': initialized_checks.values(),
            'init_failed_checks': init_failed_checks,
            }

class Dimensions(object):
    """Class to update the default dimensions.
    """

    def __init__(self, agent_config):
        self.agent_config = agent_config

    def _set_dimensions(self, dimensions, instance=None):
        """Method to append the default dimensions and per instance dimensions from the config files.
        """
        #new_dimensions = {'hostname': get_hostname()}
        new_dimensions = {'hostname': 'localhost'}           

        default_dimensions = self.agent_config.get('dimensions', {})
        if default_dimensions:
            # Add or update any default dimensions that were set in the agent config file
            new_dimensions.update(default_dimensions)
        if dimensions is not None:
            # Add or update any dimensions from the plugin itself
            new_dimensions.update(dimensions.copy())
        if instance:
            # Add or update any per instance dimensions that were set in the plugin config file
            new_dimensions.update(instance.get('dimensions', {}))
        return new_dimensions

