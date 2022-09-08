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

def get_neutron_client():
    sess = get_session()
    n_client = neutron_client.Client(session=sess)
    return n_client

def get_tenant_name(tenants, tenant_id):
    tenant_name = None
    for tenant in tenants:
        if tenant.id == tenant_id:
            tenant_name = tenant.name
            break
    return tenant_name

'''

id_cache = {}
nova_client = get_nova_client()
keystone_client = get_keystone_client()

tenants = keystone_client.projects.list()
#inst_flavor = nova_client.flavors.get()

instances = nova_client.servers.list(search_opts={'all_tenants': 1,
                          'host': 'dev-monasca'})

instance = instances[0]


insp = LibvirtInspector()

cpu_info = insp.inspect_cpus(instance)
print(cpu_info)

inspect_vnics



**********************************************************
inst_name = instance.__getattr__('OS-EXT-SRV-ATTR:instance_name')
inst_az = instance.__getattr__('OS-EXT-AZ:availability_zone')

inst_flavor = nova_client.flavors.get(instance.flavor['id'])
print(inst_flavor)

nu = get_neutron_client()
port_cache = nu.list_ports()['ports']

if port_cache:
    instance_ports = [p['id'] for p in port_cache if p['device_id'] == instance.id]

id_cache[inst_name] = {'instance_uuid': instance.id,
                        'hostname': instance.name,
                        'zone': inst_az,
                        'created': instance.created,
                        'tenant_id': instance.tenant_id,
                        'vcpus': inst_flavor.vcpus,
                        'ram': inst_flavor.ram,
                        'disk': inst_flavor.disk,
                        'instance_ports': instance_ports}


tenant_name = get_tenant_name(tenants, instance.tenant_id)

id_cache[inst_name]['tenant_name'] = tenant_name

id_cache['last_update'] = int(time.time())

print(id_cache)

'''
# VERSION = 2.1
# USERNAME = 'admin'
# PASSWORD = 'admin'
# PROJECT_ID = '309ec5ca3587465bb196ade44aecd025'
# AUTH_URL = 'http://10.8.134.29/identity'

# loader = loading.get_plugin_loader('password')
# auth = loader.load_from_options(auth_url=AUTH_URL,
#                                 username=USERNAME,
#                                 password=PASSWORD,
#                                 project_id=PROJECT_ID,
#                                 user_domain_id="default")
# sess = session.Session(auth=auth)
# nova = client.Client(VERSION, session=sess)

# keystone = ksclient.Client(session=sess)


# print(nova.servers.list(search_opts={'all_tenants': 1,
#                          'host': 'dev-monasca'}))

# print(keystone.projects.list())






# from novaclient import client
    
# VERSION = 2.1
# USERNAME = 'admin'
# PASSWORD = 'admin'
# PROJECT_ID = '309ec5ca3587465bb196ade44aecd025'
# AUTH_URL = 'http://10.8.134.29/identity'
# with client.Client(VERSION, USERNAME, PASSWORD,
#                     PROJECT_ID, AUTH_URL) as nova:
#      print(nova.servers.list())
#      print(nova.flavors.list())