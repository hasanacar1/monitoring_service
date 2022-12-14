#
# Copyright 2012 Red Hat, Inc
# (C) Copyright 2015-2016 Hewlett Packard Enterprise Development LP
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
"""Implementation of Inspector abstraction for libvirt."""

import logging

from lxml import etree
import os
from oslo_utils import units

from virt import inspector as virt_inspector
# import monasca_agent.common.config as configuration
# import monasca_agent.common.util as util

libvirt = None

log = logging.getLogger(__name__)


# Relevant configuration options must be set in 'conf.d/libvirt.yaml'
# file under 'init_config'.
# eg.
# init_config:
#   libvirt_type: kvm
#   libvirt_uri: qemu:///system
#
# 'libvirt_type' valid choices: ('kvm', 'lxc', 'qemu', 'uml', 'xen')
# 'libvirt_uri' is dependent on 'libvirt_type'

# paths = util.Paths()
# conf_path = os.path.join(paths.get_confd_path(), 'libvirt.yaml')

# config = configuration.Config()


def retry_on_disconnect(function):
    def decorator(self, *args, **kwargs):
        try:
            return function(self, *args, **kwargs)
        except libvirt.libvirtError as e:
            if (e.get_error_code() == libvirt.VIR_ERR_SYSTEM_ERROR and
                e.get_error_domain() in (libvirt.VIR_FROM_REMOTE,
                                         libvirt.VIR_FROM_RPC)):
                self.connection = None
                return function(self, *args, **kwargs)
            else:
                raise
    return decorator


class LibvirtInspector(virt_inspector.Inspector):

    per_type_uris = dict(uml='uml:///system', xen='xen:///', lxc='lxc:///')

    def __init__(self):
        self.connection = None

    def _get_connection(self):
        if not self.connection:
            global libvirt
            if libvirt is None:
                libvirt = __import__('libvirt')
            self.connection = libvirt.openReadOnly(None)

        return self.connection

    @retry_on_disconnect
    def _lookup_by_uuid(self, instance):
        instance_name = instance.name()
        try:
            return self._get_connection().lookupByUUIDString(instance.UUIDString())
        except Exception as ex:
            if not libvirt or not isinstance(ex, libvirt.libvirtError):
                raise virt_inspector.InspectorException(str(ex))
            error_code = ex.get_error_code()
            if (error_code == libvirt.VIR_ERR_SYSTEM_ERROR and
                ex.get_error_domain() in (libvirt.VIR_FROM_REMOTE,
                                          libvirt.VIR_FROM_RPC)):
                raise
            msg = ("Error from libvirt while looking up instance "
                   "<name=%(name)s, id=%(id)s>: "
                   "[Error Code %(error_code)s] "
                   "%(ex)s") % {'name': instance_name(),
                                'id': instance.ID(),
                                'error_code': error_code,
                                'ex': ex}
            raise virt_inspector.InstanceNotFoundException(msg)

    def inspect_cpus(self, instance):
        domain = self._lookup_by_uuid(instance)
        dom_info = domain.info()
        return virt_inspector.CPUStats(number=dom_info[3], time=dom_info[4])

    def _get_domain_not_shut_off_or_raise(self, instance):
        instance_name = instance.name()
        domain = self._lookup_by_uuid(instance)

        state = domain.info()[0]
        if state == libvirt.VIR_DOMAIN_SHUTOFF:
            msg = ('Failed to inspect data of instance '
                   '<name=%(name)s, id=%(id)s>, '
                   'domain state is SHUTOFF.') % {
                'name': instance_name, 'id': instance.ID()}
            raise virt_inspector.InstanceShutOffException(msg)

        return domain

    def inspect_vnics(self, instance):
        domain = self._get_domain_not_shut_off_or_raise(instance)

        tree = etree.fromstring(domain.XMLDesc(0))
        for iface in tree.findall('devices/interface'):
            target = iface.find('target')
            if target is not None:
                name = target.get('dev')
            else:
                continue
            mac = iface.find('mac')
            if mac is not None:
                mac_address = mac.get('address')
            else:
                continue
            fref = iface.find('filterref')
            if fref is not None:
                fref = fref.get('filter')

            params = dict((p.get('name').lower(), p.get('value'))
                          for p in iface.findall('filterref/parameter'))
            interface = virt_inspector.Interface(name=name, mac=mac_address,
                                                 fref=fref, parameters=params)
            dom_stats = domain.interfaceStats(name)
            stats = virt_inspector.InterfaceStats(rx_bytes=dom_stats[0],
                                                  rx_packets=dom_stats[1],
                                                  rx_errors=dom_stats[2],
                                                  rx_dropped=dom_stats[3],
                                                  tx_bytes=dom_stats[4],
                                                  tx_packets=dom_stats[5],
                                                  tx_errors=dom_stats[6],
                                                  tx_dropped=dom_stats[7])
            yield (interface, stats)

    def inspect_disks(self, instance):
        domain = self._get_domain_not_shut_off_or_raise(instance)

        tree = etree.fromstring(domain.XMLDesc(0))
        for device in filter(
                bool,
                [target.get("dev")
                 for target in tree.findall('devices/disk/target')]):
            disk = virt_inspector.Disk(device=device)
            block_stats = domain.blockStats(device)
            stats = virt_inspector.DiskStats(read_requests=block_stats[0],
                                             read_bytes=block_stats[1],
                                             write_requests=block_stats[2],
                                             write_bytes=block_stats[3],
                                             errors=block_stats[4])
            yield (disk, stats)

    def inspect_memory_usage(self, instance, duration=None):
        instance_name = instance.name()
        domain = self._get_domain_not_shut_off_or_raise(instance)

        try:
            memory_stats = domain.memoryStats()
            if (memory_stats and
                    memory_stats.get('available') and
                    memory_stats.get('unused')):
                memory_used = (memory_stats.get('available') -
                               memory_stats.get('unused'))
                # Stat provided from libvirt is in KB, converting it to MB.
                memory_used = memory_used / units.Ki
                return virt_inspector.MemoryUsageStats(usage=memory_used)
            else:
                msg = ('Failed to inspect memory usage of instance '
                       '<name=%(name)s, id=%(id)s>, '
                       'can not get info from libvirt.') % {
                    'name': instance_name, 'id': instance.ID()}
                raise virt_inspector.NoDataException(msg)
        # memoryStats might launch an exception if the method is not supported
        # by the underlying hypervisor being used by libvirt.
        except libvirt.libvirtError as e:
            msg = ('Failed to inspect memory usage of %(instance_uuid)s, '
                   'can not get info from libvirt: %(error)s') % {
                'instance_uuid': domain.ID(), 'error': e}
            raise virt_inspector.NoDataException(msg)

    def inspect_disk_info(self, instance):
        domain = self._get_domain_not_shut_off_or_raise(instance)

        tree = etree.fromstring(domain.XMLDesc(0))
        for disk in tree.findall('devices/disk'):
            disk_type = disk.get('type')
            if disk_type:
                if disk_type == 'network':
                    log.debug('Inspection disk usage of network disk '
                              '%(instance_uuid)s unsupported by libvirt' % {
                                  'instance_uuid': instance.ID()})
                    continue
                target = disk.find('target')
                device = target.get('dev')
                if device:
                    dsk = virt_inspector.Disk(device=device)
                    block_info = domain.blockInfo(device)
                    info = virt_inspector.DiskInfo(capacity=block_info[0],
                                                   allocation=block_info[1],
                                                   physical=block_info[2])
                    yield (dsk, info)

    def inspect_memory_resident(self, instance, duration=None):
        domain = self._get_domain_not_shut_off_or_raise(instance)
        memory = domain.memoryStats()['rss'] / units.Ki
        return virt_inspector.MemoryResidentStats(resident=memory)
