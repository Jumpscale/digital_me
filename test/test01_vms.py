from test.bast_test import BaseTest
from parameterized import parameterized
import random, uuid, time, traceback, logging
from termcolor import colored


class VMTestCases(BaseTest):
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
            print(colored(' [*] Installing ...', 'white'))
            self.vmservice.schedule_action('uninstall').wait(die=True)
            print(colored(' [*] Done!', 'green'))

    def generate_random_vm_params(self):
        vm_parms = {'cpu': random.choice([1, 2, 4, 8]),
                    'memory': random.choice([1024, 2048, 4096]),
                    'diskType': random.choice('hdd', 'ssd'),
                    'size': random.choice(10, 20, 30),
                    'filesystem': random.choice('ext4', 'ext3', 'ext2', 'btrfs')
                    }
        return vm_parms

    def ssh_vm_execute_command(self, cmd):
        vm_ip = self.get_vm_zt_ip(vmservice=self.vmservice)
        return self.execute_command(ip=vm_ip, cmd=cmd)

    @parameterized.expand(['ubuntu', 'zero-os'])
    def test001_create_vm(self, operting_system):
        print(colored(' [*] Create VM with %s OS' % operting_system, 'white'))
        data = {
            'nodeId': self.nodeId,
            'image': operting_system,
            'memory': random.choice([1024, 2048, 4096]),
            'zerotier': {'id': self.zt_network.id, 'ztClient': self.zt_client_instance},
            'configs': [{'path': '/root/.ssh/authorized_keys',
                         'content': self.ssh,
                         'name': 'sshkey'}]
        }
        self.vm_action(action='install', data=data)
        print(colored(' [*] Get VM info', 'white'))
        self.vm_info = self.get_vm_info(self.vmservice)
        self.kvm = self.get_kvm_by_vnc(vnc_port=self.vm_info.result['vnc'])
        self.assertIn(operting_system, self.kvm['params']['flist'])

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

    @parameterized.expand(['ubuntu', 'zero-os'])
    def test003_reinstall_vm(self, operting_system):
        """ DM-003
        *Re-install a vm test case*

        **Test Scenario:**

        #. Install a vm, assert its working well
        #, Create a file in the mounted disk
        #. remove the vm, assert it was deleted
        #. Install it again, It should working fine
        #. Assert the created file isn't there
        """
        self.vm_parms = self.generate_random_vm_params()
        print(colored(
            ' [*] Create an ubuntu machine with: {} {} {} {} {}'.format(self.vm_parms['memory'], self.vm_parms['cpu'],
                                                                        self.vm_parms['filesystem'], self.vm_parms['diskType'],
                                                                        self.vm_parms['size']), 'white'))
        data = {
            'nodeId': self.nodeId,
            'disks': [{
                'diskType': self.vm_parms['diskType'],
                'size': self.vm_parms['size'],
                'mountPoint': '/mnt',
                'filesystem': self.vm_parms['filesystem'],
                'label': str(uuid.uuid4()).replace('-', '')[:10],
            }],
            'image': operting_system,
            'cpu': self.vm_parms['cpu'],
            'memory': self.vm_parms['memory'],
            'zerotier': {'id': self.zt_network.id, 'ztClient': self.zt_client_instance},
            'configs': [{'path': '/root/.ssh/authorized_keys',
                         'content': self.ssh,
                         'name': 'sshkey'}]
        }
        print(colored(' [*] Install a vm, assert its working well', 'white'))
        kvm_before = len(self.node_client.kvm.list())
        self.vm_action(action='install', data=data)
        kvm_after = len(self.node_client.kvm.list())
        self.assertEqual(kvm_before+1, kvm_after)
        print(colored(' [*] Done!', 'green'))

        print(colored(' [*] Create a file in the mounted disk'), 'white')
        self.ssh_vm_execute_command(cmd='touch /mnt/text.txt')

        print(colored(' [*] Install a vm, assert its working well', 'white'))
        self.vm_action(action='uninstall')
        kvm_after_uninstall = len(self.node_client.kvm.list())
        self.assertEqual(kvm_after_uninstall, kvm_before)
        print(colored(' [*] Done!', 'green'))

        print(colored(' [*] Install it again, It should working fine', 'white'))
        self.vmservice.schedule_action('install').wait(die=True)
        kvm_after_reinstall = len(self.node_client.kvm.list())
        self.assertEqual(kvm_after_reinstall, kvm_after)
        print(colored(' [*] Done!', 'green'))

        print(colored(" [*] Assert the created file isn't there", 'white'))
        self.ssh_vm_execute_command(cmd='ls /mnt')

    def test004_delete_vm(self):
        """ DM-004
        *Delete the vm*

        **Test Scenario:**

        #. Install a vm, assert its working well
        #. remove the vm, assert it was deleted
        #. assert the attached disk, has been deleted too
        """

    def test005_shutdown_vm(self):
        """ DM-003
         *Shutdown the vm*

         **Test Scenario:**

         #. Install a vm, assert its working well
         #, Create a file in the mounted disk
         #. remove the vm, assert it was deleted
         #. Install it again, It should working fine
         #. Assert the created file is there
         """

    def test006_pause_resume_vm(self):
        """ DM-003
         *pause the vm*

         **Test Scenario:**

         #. Install a vm, assert its working well
         #, pause the vm, its state should be paused
         #, You can't access the vm in case of its status is pause
         #. resume the vm, its state should be ok
         """

    def test007_reboot_vm(self):
        """ DM-003
         *pause the vm*

         **Test Scenario:**

         #. Install a vm, assert its working well
         #, Create a file in the attached disk
         #, Reboot the vm, should succeed
         #. Check the created file, should be there
        """

    def test008_disable_enable_vnc(self):
        """ DM-003
         *Disable vnc port*

         **Test Scenario:**

         #. Install a vm, assert its working well
         #, Disable vnc port, make sure u can't access it via vnc
         #, enable vnc port, make sure u can access it via vnc
        """

    def test009_reinstall_vm_with_many_disks(self):
        """ DM-003
         *Install a vm with many disks*

         **Test Scenario:**

         #. Install a vm with many disks, assert its working well
         #. Uninstall it
         #. Install it again
        """
