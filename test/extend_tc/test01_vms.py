from test.base_test import BaseTest
from parameterized import parameterized
import random, uuid, time, traceback, logging
from termcolor import colored


class VMTestCasesExtend(BaseTest):
    def setUp(self):
        super().setUp()
        self.vmtemplate = 'github.com/jumpscale/digital_me/vm/0.0.1'
        self.service_name = self.generate_random_txt()

    def tearDown(self):
        print(colored(' [*] Remove the VM ', 'white'))
        self.vmservice.schedule_action('uninstall').wait(die=True)
        print(colored(' [*] len(node_client.kvm.list()) = {}'.format(len(self.node_client.kvm.list())), 'white'))

    def vm_action(self, action, data={}):
        if action == 'install':
            print(colored(' [*] Installing ...', 'white'))
            self.vmservice = self.robot.services.find_or_create(self.vmtemplate, service_name=self.service_name,
                                                                data=data)
            self.vmservice.schedule_action('install').wait(die=True)
            print(colored(' [*] Done!', 'green'))
        elif action == 'uninstall':
            print(colored(' [*] Uninstalling ...', 'white'))
            self.vmservice.schedule_action('uninstall').wait(die=True)
            print(colored(' [*] Done!', 'green'))
        elif action == 'shutdown':
            print(colored(' [*] shutdown ...', 'white'))
            self.vmservice.schedule_action('shutdown').wait(die=True)
            print(colored(' [*] Done!', 'green'))
        elif action == 'info':
            print(colored(' [*] Get info ...', 'white'))
            info = self.vmservice.schedule_action('info').wait(die=True)
            print(colored(' [*] Done!', 'green'))
            return info

    def generate_random_vm_params(self):
        vm_parms = {'cpu': random.choice([1, 2, 4, 8]),
                    'memory': random.choice([1024, 2048, 4096]),
                    'diskType': random.choice(['hdd', 'ssd']),
                    'size': random.choice([10, 20, 30]),
                    'filesystem': random.choice(['ext4', 'ext3', 'ext2', 'btrfs'])
                    }
        return vm_parms

    def ssh_vm_execute_command(self, cmd):
        vm_ip = self.get_vm_zt_ip(vmservice=self.vmservice)
        return self.execute_command(ip=vm_ip, cmd=cmd)

    @parameterized.expand([(2048, 10, 'btrfs', 'hdd', 1), (2048, 10, 'btrfs', 'hdd', 2), (2048, 10, 'btrfs', 'hdd', 4),
                           (2048, 10, 'btrfs', 'hdd', 8), (2048, 10, 'btrfs', 'ssd', 1), (2048, 10, 'btrfs', 'ssd', 2),
                           (2048, 10, 'btrfs', 'ssd', 4), (2048, 10, 'btrfs', 'ssd', 8), (2048, 10, 'ext4', 'hdd', 1),
                           (2048, 10, 'ext4', 'hdd', 2), (2048, 10, 'ext4', 'hdd', 4), (2048, 10, 'ext4', 'hdd', 8),
                           (2048, 10, 'ext4', 'ssd', 1), (2048, 10, 'ext4', 'ssd', 2), (2048, 10, 'ext4', 'ssd', 4),
                           (2048, 10, 'ext4', 'ssd', 8), (2048, 10, 'ext3', 'hdd', 1), (2048, 10, 'ext3', 'hdd', 2),
                           (2048, 10, 'ext3', 'hdd', 4), (2048, 10, 'ext3', 'hdd', 8), (2048, 10, 'ext3', 'ssd', 1),
                           (2048, 10, 'ext3', 'ssd', 2), (2048, 10, 'ext3', 'ssd', 4), (2048, 10, 'ext3', 'ssd', 8),
                           (2048, 10, 'ext2', 'hdd', 1), (2048, 10, 'ext2', 'hdd', 2), (2048, 10, 'ext2', 'hdd', 4),
                           (2048, 10, 'ext2', 'hdd', 8), (2048, 10, 'ext2', 'ssd', 1), (2048, 10, 'ext2', 'ssd', 2),
                           (2048, 10, 'ext2', 'ssd', 4), (2048, 10, 'ext2', 'ssd', 8), (2048, 20, 'btrfs', 'hdd', 1),
                           (2048, 20, 'btrfs', 'hdd', 2), (2048, 20, 'btrfs', 'hdd', 4), (2048, 20, 'btrfs', 'hdd', 8),
                           (2048, 20, 'btrfs', 'ssd', 1), (2048, 20, 'btrfs', 'ssd', 2), (2048, 20, 'btrfs', 'ssd', 4),
                           (2048, 20, 'btrfs', 'ssd', 8), (2048, 20, 'ext4', 'hdd', 1), (2048, 20, 'ext4', 'hdd', 2),
                           (2048, 20, 'ext4', 'hdd', 4), (2048, 20, 'ext4', 'hdd', 8), (2048, 20, 'ext4', 'ssd', 1),
                           (2048, 20, 'ext4', 'ssd', 2), (2048, 20, 'ext4', 'ssd', 4), (2048, 20, 'ext4', 'ssd', 8),
                           (2048, 20, 'ext3', 'hdd', 1), (2048, 20, 'ext3', 'hdd', 2), (2048, 20, 'ext3', 'hdd', 4),
                           (2048, 20, 'ext3', 'hdd', 8), (2048, 20, 'ext3', 'ssd', 1), (2048, 20, 'ext3', 'ssd', 2),
                           (2048, 20, 'ext3', 'ssd', 4), (2048, 20, 'ext3', 'ssd', 8), (2048, 20, 'ext2', 'hdd', 1),
                           (2048, 20, 'ext2', 'hdd', 2), (2048, 20, 'ext2', 'hdd', 4), (2048, 20, 'ext2', 'hdd', 8),
                           (2048, 20, 'ext2', 'ssd', 1), (2048, 20, 'ext2', 'ssd', 2), (2048, 20, 'ext2', 'ssd', 4),
                           (2048, 20, 'ext2', 'ssd', 8), (4096, 10, 'btrfs', 'hdd', 1), (4096, 10, 'btrfs', 'hdd', 2),
                           (4096, 10, 'btrfs', 'hdd', 4), (4096, 10, 'btrfs', 'hdd', 8), (4096, 10, 'btrfs', 'ssd', 1),
                           (4096, 10, 'btrfs', 'ssd', 2), (4096, 10, 'btrfs', 'ssd', 4), (4096, 10, 'btrfs', 'ssd', 8),
                           (4096, 10, 'ext4', 'hdd', 1), (4096, 10, 'ext4', 'hdd', 2), (4096, 10, 'ext4', 'hdd', 4),
                           (4096, 10, 'ext4', 'hdd', 8), (4096, 10, 'ext4', 'ssd', 1), (4096, 10, 'ext4', 'ssd', 2),
                           (4096, 10, 'ext4', 'ssd', 4), (4096, 10, 'ext4', 'ssd', 8), (4096, 10, 'ext3', 'hdd', 1),
                           (4096, 10, 'ext3', 'hdd', 2), (4096, 10, 'ext3', 'hdd', 4), (4096, 10, 'ext3', 'hdd', 8),
                           (4096, 10, 'ext3', 'ssd', 1), (4096, 10, 'ext3', 'ssd', 2), (4096, 10, 'ext3', 'ssd', 4),
                           (4096, 10, 'ext3', 'ssd', 8), (4096, 10, 'ext2', 'hdd', 1), (4096, 10, 'ext2', 'hdd', 2),
                           (4096, 10, 'ext2', 'hdd', 4), (4096, 10, 'ext2', 'hdd', 8), (4096, 10, 'ext2', 'ssd', 1),
                           (4096, 10, 'ext2', 'ssd', 2), (4096, 10, 'ext2', 'ssd', 4), (4096, 10, 'ext2', 'ssd', 8),
                           (4096, 20, 'btrfs', 'hdd', 1), (4096, 20, 'btrfs', 'hdd', 2), (4096, 20, 'btrfs', 'hdd', 4),
                           (4096, 20, 'btrfs', 'hdd', 8), (4096, 20, 'btrfs', 'ssd', 1), (4096, 20, 'btrfs', 'ssd', 2),
                           (4096, 20, 'btrfs', 'ssd', 4), (4096, 20, 'btrfs', 'ssd', 8), (4096, 20, 'ext4', 'hdd', 1),
                           (4096, 20, 'ext4', 'hdd', 2), (4096, 20, 'ext4', 'hdd', 4), (4096, 20, 'ext4', 'hdd', 8),
                           (4096, 20, 'ext4', 'ssd', 1), (4096, 20, 'ext4', 'ssd', 2), (4096, 20, 'ext4', 'ssd', 4),
                           (4096, 20, 'ext4', 'ssd', 8), (4096, 20, 'ext3', 'hdd', 1), (4096, 20, 'ext3', 'hdd', 2),
                           (4096, 20, 'ext3', 'hdd', 4), (4096, 20, 'ext3', 'hdd', 8), (4096, 20, 'ext3', 'ssd', 1),
                           (4096, 20, 'ext3', 'ssd', 2), (4096, 20, 'ext3', 'ssd', 4), (4096, 20, 'ext3', 'ssd', 8),
                           (4096, 20, 'ext2', 'hdd', 1), (4096, 20, 'ext2', 'hdd', 2), (4096, 20, 'ext2', 'hdd', 4),
                           (4096, 20, 'ext2', 'hdd', 8), (4096, 20, 'ext2', 'ssd', 1), (4096, 20, 'ext2', 'ssd', 2),
                           (4096, 20, 'ext2', 'ssd', 4), (4096, 20, 'ext2', 'ssd', 8), (8192, 10, 'btrfs', 'hdd', 1),
                           (8192, 10, 'btrfs', 'hdd', 2), (8192, 10, 'btrfs', 'hdd', 4), (8192, 10, 'btrfs', 'hdd', 8),
                           (8192, 10, 'btrfs', 'ssd', 1), (8192, 10, 'btrfs', 'ssd', 2), (8192, 10, 'btrfs', 'ssd', 4),
                           (8192, 10, 'btrfs', 'ssd', 8), (8192, 10, 'ext4', 'hdd', 1), (8192, 10, 'ext4', 'hdd', 2),
                           (8192, 10, 'ext4', 'hdd', 4), (8192, 10, 'ext4', 'hdd', 8), (8192, 10, 'ext4', 'ssd', 1),
                           (8192, 10, 'ext4', 'ssd', 2), (8192, 10, 'ext4', 'ssd', 4), (8192, 10, 'ext4', 'ssd', 8),
                           (8192, 10, 'ext3', 'hdd', 1), (8192, 10, 'ext3', 'hdd', 2), (8192, 10, 'ext3', 'hdd', 4),
                           (8192, 10, 'ext3', 'hdd', 8), (8192, 10, 'ext3', 'ssd', 1), (8192, 10, 'ext3', 'ssd', 2),
                           (8192, 10, 'ext3', 'ssd', 4), (8192, 10, 'ext3', 'ssd', 8), (8192, 10, 'ext2', 'hdd', 1),
                           (8192, 10, 'ext2', 'hdd', 2), (8192, 10, 'ext2', 'hdd', 4), (8192, 10, 'ext2', 'hdd', 8),
                           (8192, 10, 'ext2', 'ssd', 1), (8192, 10, 'ext2', 'ssd', 2), (8192, 10, 'ext2', 'ssd', 4),
                           (8192, 10, 'ext2', 'ssd', 8), (8192, 20, 'btrfs', 'hdd', 1), (8192, 20, 'btrfs', 'hdd', 2),
                           (8192, 20, 'btrfs', 'hdd', 4), (8192, 20, 'btrfs', 'hdd', 8), (8192, 20, 'btrfs', 'ssd', 1),
                           (8192, 20, 'btrfs', 'ssd', 2), (8192, 20, 'btrfs', 'ssd', 4), (8192, 20, 'btrfs', 'ssd', 8),
                           (8192, 20, 'ext4', 'hdd', 1), (8192, 20, 'ext4', 'hdd', 2), (8192, 20, 'ext4', 'hdd', 4),
                           (8192, 20, 'ext4', 'hdd', 8), (8192, 20, 'ext4', 'ssd', 1), (8192, 20, 'ext4', 'ssd', 2),
                           (8192, 20, 'ext4', 'ssd', 4), (8192, 20, 'ext4', 'ssd', 8), (8192, 20, 'ext3', 'hdd', 1),
                           (8192, 20, 'ext3', 'hdd', 2), (8192, 20, 'ext3', 'hdd', 4), (8192, 20, 'ext3', 'hdd', 8),
                           (8192, 20, 'ext3', 'ssd', 1), (8192, 20, 'ext3', 'ssd', 2), (8192, 20, 'ext3', 'ssd', 4),
                           (8192, 20, 'ext3', 'ssd', 8), (8192, 20, 'ext2', 'hdd', 1), (8192, 20, 'ext2', 'hdd', 2),
                           (8192, 20, 'ext2', 'hdd', 4), (8192, 20, 'ext2', 'hdd', 8), (8192, 20, 'ext2', 'ssd', 1),
                           (8192, 20, 'ext2', 'ssd', 2), (8192, 20, 'ext2', 'ssd', 4), (8192, 20, 'ext2', 'ssd', 8)]
                          )
    def test002_create_vm_with_disk(self, memory, disk_size, disk_fs, disk_type, cpu):
        print(colored(
            ' [*] Create an ubuntu machine with: {} {} {} {} {}'.format(memory, disk_size, disk_fs, disk_type, cpu),
            'white'))
        data = {
            'nodeId': self.nodeId,
            'disks': [{
                'diskType': disk_type,
                'size': disk_size,
                'mountPoint': '/mnt',
                'filesystem': disk_fs,
                'label': str(uuid.uuid4()).replace('-', '')[:10],
            }],
            'image': 'ubuntu',
            'memory': memory,
            'cpu': cpu,
            'zerotier': {'id': self.zt_network.id, 'ztClient': self.zt_client_instance},
            'configs': [{'path': '/root/.ssh/authorized_keys',
                         'content': self.ssh,
                         'name': 'sshkey'}]
        }

        self.vm_action(action='install', data=data)

        print(colored(' [*] Get VM info', 'white'))
        self.vm_info = self.get_vm_info(self.vmservice)
        self.kvm = self.get_kvm_by_vnc(vnc_port=self.vm_info.result['vnc'])
        self.assertEqual(memory, self.kvm['params']['memory'])
        self.assertEqual(cpu, self.kvm['params']['cpu'])
        self.assertEqual(len(data['disks']), len(self.kvm['params']['media']))
        self.assertIn(str(disk_size + 'G'), self.kvm['params']['media'][0]['url'])
