from js9 import j

from zerorobot.template.base import TemplateBase

VM_TEMPLATE_UID = 'github.com/jumpscale/digital_me/vm/0.0.1'

class S3(TemplateBase):
    version = '0.0.1'
    template_name = "s3"

    def __init__(self, name=None, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)
        self._node_api = None

    @property
    def node_api(self):
        if not self._node_api:
            self._node_api = j.clients.zrobot.robots[self.data['nodeRobot']]
        return self._node_api

    def install(self):
        vm_data = {
            'image': 'zero-os',
            'zerotier': {
                'id': self.data['vmZerotier']['id'],
                'ztClient': self.data['vmZerotier']['ztClient'],
            },
            'disks':[{
                'diskType': 'hdd',
                'size': self.data['vmDiskSize'],
                'mountPoint': '/mnt',
                'filesystem': 'btrfs',
                'name': 's3vm'
            }],
        }
        vm = self.node_api.services.create(VM_TEMPLATE_UID,'vm', vm_data)
        vm.schedule_action('install')
