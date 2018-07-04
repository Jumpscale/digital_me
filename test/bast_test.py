from selenium import webdriver
from testconfig import config
from termcolor import colored
import unittest
from js9 import j
import uuid, time
import subprocess


class BaseTest(unittest.TestCase):
    zerotier = ''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nodeId = config['main']['nodeId']
        self.zt_token = config['main']['ztoken']
        self.ssh = config['main']['ssh']
        self.robot = j.clients.zrobot.robots['main']

    @classmethod
    def setUpClass(cls):
        # Create a zerotier for VMS
        # Create SSH key
        self = cls()
        self.create_zerotier_nw()
        self.host_join_zt()
        j.clients.zerotier.get('zt_main', data={'token_': config['main']['ztoken']})

    def setUp(self):
        self.create_zerotier_nw()
        self.host_join_zt()

    def tearDown(self):
        self.delete_zerotier_nw()
        self.host_leave_zt()

    def create_zerotier_nw(self):
        print(colored(' [*] Create zerotier network.', 'white'))
        zt_config_instance_name = str(uuid.uuid4()).replace('-', '')[:10]
        self.zt_name = str(uuid.uuid4()).replace('-', '')[:10]
        self.zt_client = j.clients.zerotier.get(instance=zt_config_instance_name, data={'token_': self.zt_token})
        self.zt_network = self.zt_client.network_create(public=False, name=self.zt_name, auto_assign=True,
                                                        subnet='10.147.19.0/24')
        print(colored(' [*] ZT ID: {} '.format(self.zt_network.id), 'green'))
        BaseTest.zerotier = self.zt_network.id

    def delete_zerotier_nw(self):
        print(colored(' [*] delete zt', 'white'))
        self.zt_client.network_delete(self.zt_network.id)

    def host_join_zt(self):
        print(colored(' [*] Host join zt network)', 'white'))
        j.tools.prefab.local.network.zerotier.network_join(network_id=self.zt_network.id)
        zt_machine_addr = j.tools.prefab.local.network.zerotier.get_zerotier_machine_address()
        time.sleep(60)
        host_member = self.zt_network.member_get(address=zt_machine_addr)
        host_member.authorize()
        self.host_ip = host_member.private_ip
        print(colored(' [*] Host IP {}'.format(self.host_ip), 'green'))

    def host_leave_zt(self):
        j.tools.prefab.local.network.zerotier.network_leave(self.zt_network.id)

    def create_ztClient_service(self):
        self.ztClient = self.generate_random_txt()
        data = {
            'token': self.zt_token,
        }
        self.robot.services.create('github.com/zero-os/0-templates/zerotier_client/0.0.1', self.ztClient, data)
        return self.ztClient

    def execute_command(self, ip, cmd):
        target = "ssh root@%s '%s'" % (ip, cmd)
        ssh = subprocess.Popen(target,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

        result = ssh.stdout.readlines()
        error = ssh.stderr.readlines()
        return result, error

    def generate_random_txt(self):
        return str(uuid.uuid4()).replace('-', '')[:10]

    def get_zos_cliene(self, ip):
        self.node_client = j.clients.zos.get('host', data={'host': ip})

    def get_vm_info(self, vmservice):
        return vmservice.schedule_action('info').wait(die=True)

    def get_vm_zt_ip(self, vmservice):
        info = self.get_vm_info(vmservice)
        return info.result['zerotier']['ip']
