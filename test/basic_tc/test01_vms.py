from test.base_test import BaseTest
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
        elif action == 'pause':
            print(colored(' [*] Get info ...', 'white'))
            self.vmservice.schedule_action('pause').wait(die=True)
            print(colored(' [*] Done!', 'green'))

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

    def install_vm(self, operting_system):
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

    def test003_reinstall_vm(self):
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
            'image': 'ubuntu',
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

        print(colored(' [*] Uninstall a vm, assert its working well', 'white'))
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
        result, error = self.ssh_vm_execute_command(cmd='ls /mnt')
        self.assertEqual(len(result), 1)

    @parameterized.expand(['ubuntu', 'zero-os'])
    def test004_delete_vm(self, operting_system):
        """ DM-004
        *Delete the vm*

        **Test Scenario:**

        #. Install a vm, assert its working well
        #. remove the vm, assert it was deleted
        """
        kvm_before = len(self.node_client.kvm.list())
        self.install_vm(operting_system)

        print(colored(' [*] Uninstall a vm, assert its working well', 'white'))
        self.vm_action(action='uninstall')
        kvm_after_uninstall = len(self.node_client.kvm.list())
        self.assertEqual(kvm_after_uninstall, kvm_before)
        print(colored(' [*] Done!', 'green'))

    @parameterized.expand(['ubuntu', 'zero-os'])
    def test005_shutdown_vm(self, operting_system):
        """ DM-003
         *Shutdown the vm*

         **Test Scenario:**

         #. Install a vm, assert its working well
         #, Create a file in the mounted disk
         #. Shutdown the vm, assert it was deleted
         #. Get machine status, It should be halted
         #. Install it again, It should working fine
         #. Assert the created file is there
         """
        self.install_vm(operting_system=operting_system)

        print(colored(' [*] Create a file in the mounted disk'), 'white')
        self.ssh_vm_execute_command(cmd='touch /mnt/text.txt')

        print(colored(' [*] Shutdown the vm, assert it was deleted', 'white'))
        self.vm_action(action='shutdown')

        print(colored(' [*] Get machine status, It should be halted', 'white'))
        self.vm_info = self.vm_action(action='info')
        self.assertEqual(self.vm_info.result['status'], 'halted')

        print(colored(' [*] Install it again, It should working fine', 'white'))
        self.vmservice.schedule_action('install').wait(die=True)

        print(colored(" [*] Assert the created file is still existing", 'white'))
        result, error = self.ssh_vm_execute_command(cmd='ls /mnt')
        self.assertEqual(len(result), 2)

    @parameterized.expand(['ubuntu', 'zero-os'])
    def test006_pause_resume_vm(self, operting_system):
        """ DM-003
         *pause the vm*

         **Test Scenario:**

         #. Install a vm, assert its working well
         #, pause the vm, its state should be paused
         #, You can't access the vm in case of its status is pause
         #. resume the vm, its state should be ok
         """
        self.install_vm(operting_system)
        self.vm_action(action='pause')
        self.vm_info = self.vm_action(action='info')
        self.assertEqual(self.vm_info.result['status'], 'pause')

        print(colored(' [*] Resume the vm, its state should be ok', 'white'))
        self.vmservice.schedule_action('install').wait(die=True)
        self.vm_info = self.vm_action(action='info')
        self.assertEqual(self.vm_info.result['status'], 'running')

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
