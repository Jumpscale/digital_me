from js9 import j
from zerorobot.template.base import TemplateBase
from zerorobot.template.state import StateCheckError

VDISK_TEMPLATE_UID = 'github.com/zero-os/0-templates/vdisk/0.0.1'
VM_TEMPLATE_UID = 'github.com/zero-os/0-templates/vm/0.0.1'
ZT_TEMPLATE_UID = 'github.com/zero-os/0-templates/zerotier_client/0.0.1'
BASEFLIST = 'https://hub.gig.tech/gig-bootable/{}.flist'
ZEROOSFLIST = "https://hub.gig.tech/gig-bootable/zero-os-bootable.flist"
IPXEURL = 'https://bootstrap.gig.tech/ipxe/{}/{}/development ztid={}'


class Vm(TemplateBase):

    version = '0.0.1'
    template_name = "vm"

    def __init__(self, name, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)

        # self.recurring_action('_monitor', 30)  # every 30 seconds
        self._node_api = None

    def validate(self):
        if not self.data['nodeId']:
            raise ValueError('Invalid input, Vm requires nodeId')

        capacity = j.clients.grid_capacity.get(interactive=False)
        nodes = capacity.api.ListCapacity(query_params={'node_id': self.data['nodeId']})[0]
        if not nodes:
            raise ValueError('Node {} does not exist'.format(self.data['nodeId']))

        j.clients.zrobot.get(self.data['nodeId'], data={'url': nodes[0].robot_address})
        self._node_api = j.clients.zrobot.robots[self.data['nodeId']]
        # self._node_api = j.clients.zrobot.robots['main']

        if self.data['image'].partition(':')[0] not in ['zero-os', 'ubuntu']:
            raise ValueError('Invalid image')

        for key in ['id', 'ztClient']:
            if not self.data['zerotier'].get(key):
                raise ValueError('Invalid input, zerotier requires {}'.format(key))

    @property
    def _node_vm(self):
        return self._node_api.services.get(name=self.guid)

    def _monitor(self):
        self.logger.info('Monitor vm %s' % self.name)
        self.state.check('actions', 'install', 'ok')
        state = self._node_vm.state
        try:
            state.check('status', 'running', 'ok')
            self.state.set('status', 'running', 'ok')
            return
        except StateCheckError:
            self.state.delete('status', 'running')

    def install(self):
        self.logger.info('Installing vm %s' % self.name)
    
        zt_name = self.data['zerotier']['ztClient']
        zt_client = self.api.services.get(name=zt_name, template_uid=ZT_TEMPLATE_UID)
        token = zt_client.schedule_action('token').wait(die=True).result
        self._node_api.services.find_or_create(ZT_TEMPLATE_UID, zt_name, {'token': token})

        vm_disks = []
        for disk in self.data['disks']:
            vdisk = self._node_api.services.create(VDISK_TEMPLATE_UID, '_'.join([self.guid, disk['name']]), data=disk)
            vdisk.schedule_action('install').wait(die=True)
            url = vdisk.schedule_action('private_url').wait(die=True).result
            vm_disks.append({
                'url': url,
                'name': disk['name'],
                'mountPoint': disk['mountPoint'],
                'filesystem': disk['filesystem'],
            })

        vm_data = {
            'memory': self.data['memory'],
            'cpu': self.data['cpu'],
            'disks': vm_disks,
            'configs': self.data['configs'],
            'ztIdentity': self.data['ztIdentity'],
            'nics': [{
                'id': self.data['zerotier']['id'],
                'type': 'zerotier',
                'ztClient': self.data['zerotier']['ztClient'],
                'name': 'zerotier_nic',
            },
            {'name': 'test',
             'type': 'default'
            }]
        }

        image, _, version = self.data['image'].partition(':')
        if image == 'zero-os':
            version = version or 'development'
            vm_data['flist'] = ZEROOSFLIST
        else:
            version = version or 'lts'
            flist = '{}:{}'.format(image, version)
            vm_data['flist'] = BASEFLIST.format(flist)

        vm = self._node_api.services.create(VM_TEMPLATE_UID, self.guid, data=vm_data)

        if image == 'zero-os':
            if not self.data['ztIdentity']:
                self.data['ztIdentity'] = vm.schedule_action('generate_identity').wait(die=True).result
            url = IPXEURL.format(version, self.data['zerotier']['id'], self.data['ztIdentity'])
            vm.schedule_action('update_ipxeurl', args={'url': url}).wait(die=True)

        vm.schedule_action('install').wait(die=True)
        self.data['ztIdentity'] = vm.schedule_action('zt_identity').wait(die=True).result

        self.state.set('actions', 'install', 'ok')
        self.state.set('status', 'running', 'ok')

    def zt_identity(self):
        return self.data['ztIdentity']

    def uninstall(self):
        self.logger.info('Uninstalling vm %s' % self.name)
        self.state.check('actions', 'install', 'ok')
        self._node_vm.schedule_action('uninstall').wait(die=True)
        self.state.delete('actions', 'install')
        self.state.delete('status', 'running')

    def info(self):
        self.state.check('actions', 'install', 'ok')
        info = self._node_vm.schedule_action('info').wait(die=True).result
        nics = info.pop('nics')
        info['zerotier'] = {'id': nics[0]['id'], 'ztClient': nics[0]['ztClient']}
        return info

    def shutdown(self):
        self.logger.info('Shuting down vm %s' % self.name)
        self.state.check('status', 'running', 'ok')
        self._node_vm.schedule_action('shutdown').wait(die=True)
        self.state.delete('status', 'running')
        self.state.set('status', 'shutdown', 'ok')

    def pause(self):
        self.logger.info('Pausing vm %s' % self.name)
        self.state.check('status', 'running', 'ok')
        self._node_vm.schedule_action('pause').wait(die=True)
        self.state.delete('status', 'running')
        self.state.set('actions', 'pause', 'ok')

    def resume(self):
        self.logger.info('Resuming vm %s' % self.name)
        self.state.check('actions', 'pause', 'ok')
        self._node_vm.schedule_action('resume').wait(die=True)
        self.state.delete('actions', 'pause')
        self.state.set('status', 'running', 'ok')

    def reboot(self):
        self.logger.info('Rebooting vm %s' % self.name)
        self.state.check('actions', 'install', 'ok')
        self._node_vm.schedule_action('reboot').wait(die=True)
        self.state.set('status', 'rebooting', 'ok')

    def reset(self):
        self.logger.info('Resetting vm %s' % self.name)
        self.state.check('actions', 'install', 'ok')
        self._node_vm.schedule_action('reset').wait(die=True)

    def enable_vnc(self):
        self.logger.info('Enable vnc for vm %s' % self.name)
        self.state.check('actions', 'install', 'ok')
        self._node_vm.schedule_action('enable_vnc').wait(die=True)

    def disable_vnc(self):
        self.logger.info('Disable vnc for vm %s' % self.name)
        self.state.check('actions', 'install', 'ok')
        self._node_vm.schedule_action('disable_vnc').wait(die=True)
