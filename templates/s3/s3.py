import json
import math

from js9 import j

from zerorobot.template.base import TemplateBase

VM_TEMPLATE_UID = 'github.com/jumpscale/digital_me/vm/0.0.1'


class S3(TemplateBase):
    version = '0.0.1'
    template_name = "s3"

    def __init__(self, name=None, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)

    def _get_zrobot(self, name, url):
        j.clients.zrobot.get(name, data={'url': url})
        return j.clients.zrobot.robots[name]

    def validate(self):
        if self.data['parityShards'] > self.data['dataShards']:
            raise ValueError('parityShards must be equal to or less than dataShards')

    def _create_namespace(self, nodes, index, storage_key, password):
        final_index = index
        while True:
            next_index = final_index + 1 if final_index < len(nodes) - 2 else 0
            if nodes[final_index][storage_key] >= self.data['storageSize']:
                best_node = nodes[final_index]
                robot = self._get_zrobot(best_node['_id'], best_node['robot_address'])
                robot = self._get_zrobot('main', 'http://localhost:6601')
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
                    template_uid='github.com/zero-os/0-templates/namespace/0.0.1', data=data)
                available = namespace.schedule_action('install', args={'if_available': True}).wait(die=True).result
                if available:
                    best_node[storage_key] = best_node[storage_key] - self.data['storageSize']
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

        capacity = j.clients.grid_capacity.get(interactive=False)

        storage_key = 'sru' if self.data['storageType'] == 'ssd' else 'hru'
        nodes = json.loads(capacity.nodes.ListCapacity(
            query_params={'farmer': self.data['farmerIyoOrg']}).content.decode('utf8'))
        if not nodes:
            raise RuntimeError('There are not nodes in this farm')
        ns_password = j.data.idgenerator.generateXCharID(32)
        zdbs_connection = list()
        nodes = sorted(nodes, key=lambda k: k[storage_key], reverse=True)

        node_index = 0
        for i in range(zdb_count):
            namespace, node_index = self._create_namespace(nodes, node_index, storage_key, ns_password)
            result = namespace.schedule_action('connection_info').wait(die=True).result
            zdbs_connection.append('{}:{}'.format(result['ip'], result['port']))

        nodes = sorted(nodes, key=lambda k: k[storage_key], reverse=True)

        vm_data = {
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
            # 'nodeRobot': nodes[0]['_id'],
            'nodeRobot': 'main',
        }
        vm = self.api.services.create(VM_TEMPLATE_UID, self.guid, vm_data)
        vm.schedule_action('install').wait(die=True)
        zt_identity = vm.schedule_action('zt_identity').wait(die=True).result
        zt_client = j.clients.zerotier.get(self.data['vmZerotier']['ztClient'])
        network = zt_client.network_get(self.data['vmZerotier']['id'])
        members = network.members_list(True)

        for member in members:
            if member['config']['identity'] == zt_identity:
                break
        else:
            raise RuntimeError('Failed to find vm in zerotier network')

        vm_robot = self._get_zrobot(vm.name, 'http://{}:6601'.format(member['physicalAddress']))
        minio_data = {
            'zerodbs': zdbs_connection,
            'namespace': self.guid,
            'nsSecret': ns_password,
        }
        minio = vm_robot.services.create('github.com/zero-os/0-templates/minio/0.0.1', self.guid, minio_data)
        minio.schedule_action('install').wait(die=True)
        minio.schedule_action('start').wait(die=True)

















