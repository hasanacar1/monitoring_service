from keystoneauth1 import loading
from keystoneauth1 import session
from novaclient import client
from keystoneclient.v3 import client as ksclient
from neutronclient.v2_0 import client as neutron_client
import time

from virt.libvirt.inspector import LibvirtInspector


def get_session():
    VERSION = 2.1
    USERNAME = 'admin'
    PASSWORD = '1234qweR'
    PROJECT_ID = '37550090964b4f0dbd9df45a174b1d1d'
    AUTH_URL = 'http://10.8.134.107/identity'

    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(auth_url=AUTH_URL,
                                    username=USERNAME,
                                    password=PASSWORD,
                                    project_id=PROJECT_ID,
                                    user_domain_id="default")
    sess = session.Session(auth=auth)

    return sess

def get_nova_client():
    VERSION = 2.1
    sess = get_session()
    nova_client = client.Client(VERSION, session=sess)
    return nova_client

def get_keystone_client():
    sess = get_session()
    ks_client = ksclient.Client(session=sess)
    return ks_client

nova_client = get_nova_client()

instances = nova_client.servers.list(
            search_opts={'all_tenants': 1})
print(instances)

keystone_client = get_keystone_client()
tenants = keystone_client.projects.list()

print(tenants)