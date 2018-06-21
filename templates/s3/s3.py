import json
import math
import time
import requests

from js9 import j

from zerorobot.template.base import TemplateBase

VM_TEMPLATE_UID = 'github.com/jumpscale/digital_me/vm/0.0.1'
MINIO_TEMPLATE_UID = 'github.com/zero-os/0-templates/minio/0.0.1'
NS_TEMPLATE_UID = 'github.com/zero-os/0-templates/namespace/0.0.1'


class S3(TemplateBase):
    version = '0.0.1'
    template_name = "s3"

    def __init__(self, name=None, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)
        self._nodes = []

    def _get_zrobot(self, name, url):
        j.clients.zrobot.get(name, data={'url': url})
        return j.clients.zrobot.robots[name]

    def validate(self):
        if self.data['parityShards'] > self.data['dataShards']:
            raise ValueError('parityShards must be equal to or less than dataShards')

        capacity = j.clients.grid_capacity.get(interactive=False)
        self._nodes = json.loads(capacity.api.ListCapacity(query_params={'farmer': self.data['farmerIyoOrg']})[1].content.decode('utf-8'))
        if not self._nodes:
            raise ValueError('There are no nodes in this farm')

    def _create_namespace(self, index, storage_key, password):
        final_index = index
        while True:
            next_index = final_index + 1 if final_index < len(self._nodes) - 2 else 0
            if self._nodes[final_index][storage_key] >= self.data['storageSize']:
                best_node = self._nodes[final_index]
                robot = self._get_zrobot(best_node['node_id'], best_node['robot_address'])
                #robot = self._get_zrobot('main', 'http://localhost:6600')
                data = {
                    'disktype': self.data['storageType'],
                    'mode': 'user',
                    'password': password,
                    'public': True,
                    'size': self.data['storageSize'],
                    'nsName': self.guid,
                }
                namespace = robot.services.create(
                    service_name=j.data.idgenerator.generateXCharID(16),
                    template_uid=NS_TEMPLATE_UID, data=data)
                available = namespace.schedule_action('install', args={'if_available': True}).wait(die=True).result
                if available:
                    best_node[storage_key] = best_node[storage_key] - self.data['storageSize']
                    self.data['namespaces'].append({'name': namespace.name, 'url': best_node['robot_address'], 'node': best_node['node_id']})
                    return namespace, next_index
                namespace.delete()
            if next_index == index:
                raise RuntimeError('Looped all nodes and could not find a suitable node')
            final_index = next_index
        
    def install(self):
        zdb_count = 1
        if self.data['dataShards'] and not self.data['parityShards']:
            zdb_count = self.data['dataShards']
        else:
            max = self.data['dataShards'] + self.data['parityShards']
            min = self.data['dataShards'] - self.data['parityShards']
            zdb_count = math.ceil(max + ((max - min)/2))

        storage_key = 'sru' if self.data['storageType'] == 'ssd' else 'hru'
        ns_password = j.data.idgenerator.generateXCharID(32)
        zdbs_connection = list()
        self._nodes = sorted(self._nodes, key=lambda k: k[storage_key], reverse=True)

        node_index = 0
        for i in range(zdb_count):
            namespace, node_index = self._create_namespace(node_index, storage_key, ns_password)
            result = namespace.schedule_action('connection_info').wait(die=True).result
            zdbs_connection.append('{}:{}'.format(result['ip'], result['port']))

        self._nodes = sorted(self._nodes, key=lambda k: k[storage_key], reverse=True)

        vm_data = {
            'memory': 2000,
            'image': 'zero-os',
            'zerotier': {
                'id': self.data['vmZerotier']['id'],
                'ztClient': self.data['vmZerotier']['ztClient'],
            },
            'disks': [{
                'diskType': 'hdd',
                'size': self.data['vmDiskSize'],
                'mountPoint': '/mnt',
                'filesystem': 'btrfs',
                'name': 's3vm'
            }],
            'nodeId': self._nodes[0]['node_id'],
        }
        vm = self.api.services.create(VM_TEMPLATE_UID, self.guid, vm_data)
        vm.schedule_action('install').wait(die=True)
        zt_identity = vm.schedule_action('zt_identity').wait(die=True).result
        id = zt_identity.split(':', 1)[0]
        zt_client = j.clients.zerotier.get(self.data['vmZerotier']['ztClient'])
        network = zt_client.network_get(self.data['vmZerotier']['id'])

        now = time.time()

        while time.time() < now + 600:
            members = network.members_list(True)
            for member in members:
                if member['config']['id'] == id:
                    break
            else:
                raise RuntimeError('Failed to find vm in zerotier network')
            if not member['config']['ipAssignments']:
                time.sleep(10)

        if not member['config']['ipAssignments']:
            raise RuntimeError('VM has no ip assignments in zerotier network')

        vm_robot = self._get_zrobot(vm.name, 'http://{}:6600'.format(member['config']['ipAssignments'][0]))
        minio_data = {
            'zerodbs': zdbs_connection,
            'namespace': self.guid,
            'nsSecret': ns_password,
            'login': self.data['minioLogin'],
            'password': self.data['minioPassword'],
        }

        now = time.time()
        minio = None
        while time.time() < now + 1200:
            try:
                minio = vm_robot.services.find_or_create(MINIO_TEMPLATE_UID, self.guid, minio_data)
            except requests.ConnectionError:
                time.sleep(10)

        if not minio:
            raise RuntimeError('Failed to create minio service')

        minio.schedule_action('install').wait(die=True)
        minio.schedule_action('start').wait(die=True)
        # port = minio.schedule_action('node_port').wait(die=True).result
        # self.data['minioUrl'] = 'http://{}:{}'.format(member['config']['ipAssignments'][0], port)
        self.data['minioUrl'] = 'http://{}:{}'.format(member['config']['ipAssignments'][0], 9000)

    def uninstall(self):
        for namespace in self.data['namespaces']:
            robot = self._get_zrobot(namespace['node'], namespace['url'])
            ns = robot.services.get(template_uid=NS_TEMPLATE_UID, name=namespace['name'])
            ns.schedule_action('uninstall').wait(die=True)
            self.data['namespaces'].remove(namespace)

        vm = self.api.services.get(template_uid=VM_TEMPLATE_UID, name=self.guid)
        vm.schedule_action('uninstall').wait(die=True)

