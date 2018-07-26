from testconfig import config
from termcolor import colored
import unittest
from js9 import j
import uuid, time
import subprocess


class BaseTest(unittest.TestCase):
    node_info = {'ssd': 0, 'hdd': 0, 'core': 0, 'memory': 0}
    robot = j.clients.zrobot.robots['main']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nodeId = config['main']['nodeid']
        self.nodeIP = config['main']['nodeip']
        self.zt_token = config['main']['ztoken']

    @classmethod
    def setUpClass(cls):
        self = cls()
        BaseTest.zt_client_instance = self.generate_random_txt()
        BaseTest.ssh = self.load_ssh_key()

        self.create_zerotier_nw()
        self.host_join_zt()
        self.create_ztClient_service()

        BaseTest.node_client = j.clients.zos.get('host', data={'host': config['main']['nodeip']})
        BaseTest.node_sal_client = j.clients.zos.sal.get_node('host')
        self.get_zos_info()

    @classmethod
    def tearDownClass(cls):
        self = cls()
        self.zt_network = BaseTest.zerotier_nw
        self.zt_client = BaseTest.zerotier_cl
        self.host_leave_zt()
        self.delete_zerotier_nw()
        self.delete_ztClient_service()

    def setUp(self):
        self.ssh = BaseTest.ssh
        self.zt_network = BaseTest.zerotier_nw
        self.node_client = BaseTest.node_client
        self.node_sal_client = BaseTest.node_sal_client

    def tearDown(self):
        print(colored(' [*] Tear down', 'white'))

    def create_zerotier_nw(self):
        print(colored(' [*] Create zerotier network.', 'white'))
        zt_config_instance_name = str(uuid.uuid4()).replace('-', '')[:10]
        self.zt_name = str(uuid.uuid4()).replace('-', '')[:10]
        self.zt_client = j.clients.zerotier.get(instance=zt_config_instance_name, data={'token_': self.zt_token})
        self.zt_network = self.zt_client.network_create(public=False, name=self.zt_name, auto_assign=True,
                                                        subnet='10.147.19.0/24')
        print(colored(' [*] ZT ID: {} '.format(self.zt_network.id), 'green'))
        BaseTest.zerotier_cl = self.zt_client
        BaseTest.zerotier_nw = self.zt_network

    def delete_zerotier_nw(self):
        print(colored(' [*] delete zt', 'white'))
        self.zt_client.network_delete(self.zt_network.id)

    def host_join_zt(self):
        print(colored(' [*] Host join zt network', 'white'))
        j.tools.prefab.local.network.zerotier.network_join(network_id=self.zt_network.id)
        zt_machine_addr = j.tools.prefab.local.network.zerotier.get_zerotier_machine_address()
        time.sleep(30)
        for _ in range(20):
            try:
                host_member = self.zt_network.member_get(address=zt_machine_addr)
                break
            except:
                time.sleep(30)
        else:
            host_member = self.zt_network.member_get(address=zt_machine_addr)
        host_member.authorize()
        time.sleep(30)
        self.host_ip = host_member.private_ip
        print(colored(' [*] Host IP {}'.format(self.host_ip), 'green'))

    def host_leave_zt(self):
        print(colored(' [*] Host leave zt network', 'white'))
        j.tools.prefab.local.network.zerotier.network_leave(self.zt_network.id)

    def create_ztClient_service(self):
        data = {
            'token': self.zt_token,
        }
        self.robot.services.create('github.com/zero-os/0-templates/zerotier_client/0.0.1', self.zt_client_instance,
                                   data)

    def delete_ztClient_service(self):
        zt = self.robot.services.get(name=self.zt_client_instance)
        zt.schedule_action('delete')
        zt.delete()

    def execute_command(self, ip, cmd):
        target = """ssh -o "StrictHostKeyChecking no" root@%s '%s'""" % (ip, cmd)
        ssh = subprocess.Popen(target, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = ssh.stdout.readlines()
        error = ssh.stderr.readlines()
        return result, error

    def load_ssh_key(self):
        with open('/root/.ssh/id_rsa.pub', 'r') as file:
            ssh = file.readline().replace('\n', '')
        if not ssh:
            cmd = 'mkdir /root/.ssh; ssh-keygen -t rsa -f /root/.ssh/id_rsa -q -P ""'
            subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.load_ssh_key()
        return ssh

    def generate_random_txt(self):
        return str(uuid.uuid4()).replace('-', '')[:10]

    def get_vm_info(self, vmservice):
        return vmservice.schedule_action('info').wait(die=True)

    def get_vm_zt_ip(self, vmservice):
        for _ in range(10):
            info = self.get_vm_info(vmservice)
            ip = info.result['zerotier']['ip']
            if ip:
               return ip
            else:
                print(colored(" [*] VM is trying to get zt IP ... ", 'yellow'))
                time.sleep(15)
        else:
            raise RuntimeError(colored(" [*] VM doesn't have zt IP.", 'yellow'))

    def get_kvm_by_vnc(self, vnc_port):
        kvms = self.node_client.kvm.list()
        for kvm in kvms:
            if vnc_port == kvm['vnc']:
                return kvm
            else:
                return None

    def get_zos_info(self):
        info = self.node_sal_client.capacity.total_report()
        BaseTest.node_info = {'ssd': int(info.SRU), 'hdd': int(info.HRU), 'core': info.CRU,
                              'memory': int(info.MRU)}
