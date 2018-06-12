from zerorobot.template.base import TemplateBase
from js9 import j
import random
import copy

PUBLIC_ZT = "9f77fc393e094c66"
PUBLIC_GW_ROBOTS = ["http://10.103.54.126:6600", "http://10.103.199.4:6600", "http://10.103.107.41:6600"]

GW_UID = 'github.com/zero-os/0-templates/gateway/0.0.1'
PGW_UID = 'github.com/zero-os/0-templates/public_gateway/0.0.1'
DM_VM_UID = 'github.com/jumpscale/digital_me/vm/0.0.1'

class Gateway(TemplateBase):
    version = '0.0.1'
    template_name = 'gateway'

    def __init__(self, name, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)


    @property
    def robot_api(self):
        return j.clients.zrobot.robots[self.data['nodeRobot']]

    @property
    def public_robot_api(self):
        if not self.data.get('publicGatewayRobot'):
            self.data['publicGatewayRobot'] = random.choice(PUBLIC_GW_ROBOTS)
        return j.clients.zrobot.robots[self.data['publicGatewayRobot']]

    def get_gw_service(self):
        return self.robot_api.services.get(template_uid=GW_UID, name=self.guid)


    def get_pgw_service(self):
        return self.public_robot_api.services.get(template_uid=PGW_UID, name=self.guid)

    def install(self):
        gwdata = copy.deepcopy(self.data)
        gwdata.pop('nodeRobot')
        pgwdata = {
            'httpproxies': gwdata.pop('publicHttpproxies', []),
            'portforwards': gwdata.pop('publicPortforwards', []),
        }
        networks = gwdata.setdefault('networks', [])
        for network in networks:
            network['public'] = False
        networks.append({
            'name': 'publicgw',
            'type': 'zerotier',
            'id': PUBLIC_ZT,
            'public': True
        })
        gwservice = self.robot_api.services.find_or_create(GW_UID, self.guid, gwdata)
        gwservice.schedule_action('install').wait(die=True)
        pgwservice = self.public_robot_api.services.find_or_create(PGW_UID, self.guid, pgwdata)
        pgwservice.schedule_action('install').wait(die=True)

    def _get_vm_ip(self, vm):
        vmservice = self.api.services.get(name=vm, template_uid=DM_VM_UID)
        info = vmservice.schedule_action('info').wait(die=True).result
        for network in self.data['networks']:
            if network['type'] == 'zerotier' and network['id'] == info['zerotier']['id']:
                break
        else:
            raise LookupError('Gateway is not part of the same Zerotier as the VM {}'.format(vm))
        zcl = j.clients.zerotier.get(info['zerotier']['ztClient'], interactive=False)
        network = zcl.network_get(info['zerotier']['id'])
        member = network.member_get(info['ztIdentity'].split(':')[0])
        return member.private_ip

    def info(self):
        pgw_info = self.get_pgw_service().schedule_action('info').die(True).result
        data = {
            'publicip': pgw_info['publicip'],
            'networks': self.data['networks'],
            'httpproxies': self.data['httpproxies'],
            'publicHttpproxies': self.data['publicHttpproxies'],
            'portforwards': self.data['portforwards'],
            'publicPortforwards': self.data['publicPortforwards'],
        }
        return data

    def add_portforward(self, name, srcport, vm, dstport, protocols=None):
        protocols = protocols or ['tcp']
        forward = {
            'srcnetwork': 'publicgw',
            'srcport': srcport,
            'dstport': dstport,
            'dstip': self._get_vm_ip(vm),
            'protocols': protocols,
            'name': name
        }
        gwservice = self.get_gw_service()
        gwservice.schedule_action('add_portforward', args={'forward': forward}).wait(die=True)
        self.data.setdefault('portforwards', []).append(forward)

    def remove_portforward(self, name):
        gwservice = self.get_gw_service()
        gwservice.schedule_action('remove_portforward', args={'name': name}).wait(die=True)
        for forward in self.data.get('portforwards', []):
            if forward['name'] == name:
                self.data['portforwards'].remove(forward)
                return

    def add_public_portforward(self, name, srcport, dstport, protocols=None):
        info = self.get_gw_service().schedule_action('info').wait(die=True).result
        for network in info['networks']:
            if network['public']:
                break
        else:
            raise LookupError('Could not find Public interface')
        dstip = network['config']['cidr'].split('/')[0]
        protocols = protocols or ['tcp']
        forward = {
            'name': name,
            'srcport': srcport,
            'dstport': dstport,
            'dstip': dstip,
        }
        pgwservice = self.get_pgw_service()
        pgwservice.schedule_action('add_portforward', args={'forward': forward}).wait(die=True)
        self.data.setdefault('publicPortforwards', []).append(forward)

    def remove_public_portforward(self, name):
        pgwservice = self.get_pgw_service()
        pgwservice.schedule_action('remove_portforward', args={'name': name}).wait(die=True)
        for forward in self.data.get('publicPortforwards', []):
            if forward['name'] == name:
                self.data['publicPortforwards'].remove(forward)
                return

    def add_public_http_proxy(self, name, host, destinations, types=None):
        types = types or ['https']
        pgwservice = self.get_pgw_service()
        proxy = {
            'name': name,
            'host': host,
            'destinations': destinations,
            'types': types
        }
        pgwservice.schedule_action('add_http_proxy', args={'proxy': proxy}).wait(die=True)
        self.data.setdefault('publicHttpproxies', []).append(proxy)

