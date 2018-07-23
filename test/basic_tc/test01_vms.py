from test.base_test import BaseTest
from parameterized import parameterized
import random, uuid, time, traceback, logging
from termcolor import colored


class VMTestCases(BaseTest):
    def setUp(self):
        print(colored('\n [*] SetUp .. ', 'yellow'))
        super().setUp()
        self.vmtemplate = 'github.com/jumpscale/digital_me/vm/0.0.1'
        self.service_name = self.generate_random_txt()

    def tearDown(self):
        print(colored(' [*] TearDown .. ', 'yellow'))
        if 'vmservice' in self.__dict__:
            print(colored(' [*] Remove the VM ', 'white'))
            self.vmservice.schedule_action('uninstall').wait(die=True)
            print(colored(' [*] No. of VMs : {}'.format(len(self.node_client.kvm.list())), 'white'))

    def vm_action(self, action, data={}):
        if action == 'install':
            self.vmservice = self.robot.services.find_or_create(self.vmtemplate, service_name=self.service_name,
                                                                data=data)
            self.vmservice.schedule_action('install').wait(die=True)
        elif action == 'uninstall':
            self.vmservice.schedule_action('uninstall').wait(die=True)
        elif action == 'shutdown':
            self.vmservice.schedule_action('shutdown').wait(die=True)
        elif action == 'info':
            info = self.vmservice.schedule_action('info').wait(die=True)
            return info
        elif action == 'pause':
            self.vmservice.schedule_action('pause').wait(die=True)

    def generate_random_vm_params(self):
        vm_parms = {'cpu': random.randint(1, BaseTest.node_info['core']),
                    'memory': random.randint(1, BaseTest.node_info['memory']),
                    'filesystem': random.choice(['ext4', 'ext3', 'ext2', 'btrfs'])
                    }
        if (BaseTest.node_info['hdd'] != 0) and (BaseTest.node_info['ssd'] != 0):
            disk_type = random.choice(['hdd', 'ssd'])
            disk_size = random.randint(1, BaseTest.node_info[disk_type])
        elif BaseTest.node_info['hdd'] != 0:
            disk_type = 'hdd'
            disk_size = random.randint(1, BaseTest.node_info[disk_type])
        else:
            disk_type = 'ssd'
            disk_size = random.randint(1, BaseTest.node_info[disk_type])
        vm_parms['diskType'] = disk_type
        vm_parms['size'] = disk_size
        return vm_parms

    def ssh_vm_execute_command(self, cmd):
        self.vm_ip = self.get_vm_zt_ip(vmservice=self.vmservice)
        return self.execute_command(ip=self.vm_ip, cmd=cmd)

    def install_vm(self, operating_system):
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
            'image': operating_system,
            'cpu': self.vm_parms['cpu'],
            'memory': self.vm_parms['memory'],
            'zerotier': {'id': self.zt_network.id, 'ztClient': self.zt_client_instance},
            'configs': [{'path': '/root/.ssh/authorized_keys',
                         'content': self.ssh,
                         'name': 'sshkey'}]
        }
        print(colored(' [*] Install a vm, assert its working well', 'white'))
        self.kvm_before = len(self.node_client.kvm.list())
        self.vm_action(action='install', data=data)
        self.kvm_after = len(self.node_client.kvm.list())
        self.assertEqual(self.kvm_before+1, self.kvm_after)
        print(colored(' [*] Done!', 'green'))

    @parameterized.expand(['ubuntu', 'zero-os'])
    def test001_create_vm(self, operating_system):
        """ DM-001 Install a vm test case

        **Test Scenario:**

        #. Install a vm, assert its working well
        """
        print(colored(' [*] Create VM with %s OS' % operating_system, 'white'))
        data = {
            'nodeId': self.nodeId,
            'image': operating_system,
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
        self.assertIn(operating_system, self.kvm['params']['flist'])

    def test003_reinstall_vm(self):
        """ DM-002 Re-install a vm test case

        **Test Scenario:**

        #. Install a vm, assert its working well
        #, Create a file in the mounted disk
        #. remove the vm, assert it was deleted
        #. Install it again, It should working fine
        #. Assert the created file isn't there
        """
        self.install_vm(operating_system='ubuntu')

        print(colored(' [*] Create a file in the mounted disk'), 'white')
        time.sleep(60)
        res, err = self.ssh_vm_execute_command(cmd='touch /mnt/text.txt')

        print(colored(' [*] Uninstall a vm, assert its working well', 'white'))
        self.vm_action(action='uninstall')
        kvm_after_uninstall = len(self.node_client.kvm.list())
        self.assertEqual(kvm_after_uninstall, self.kvm_before)
        print(colored(' [*] Done!', 'green'))

        print(colored(' [*] Install it again, It should working fine', 'white'))
        self.vmservice.schedule_action('install').wait(die=True)
        kvm_after_reinstall = len(self.node_client.kvm.list())
        self.assertEqual(kvm_after_reinstall, self.kvm_after)
        print(colored(' [*] Done!', 'green'))

        print(colored(" [*] Assert the created file isn't there", 'white'))
        result, error = self.ssh_vm_execute_command(cmd='ls /mnt')
        self.assertEqual(len(result), 0)

    @parameterized.expand(['ubuntu', 'zero-os'])
    def test004_delete_vm(self, operating_system):
        """ DM-003 Delete the vm

        **Test Scenario:**

        #. Install a vm, assert its working well
        #. remove the vm, assert it was deleted
        """
        self.install_vm(operating_system)

        print(colored(' [*] Uninstall a vm, assert its working well', 'white'))
        self.vm_action(action='uninstall')
        kvm_after_uninstall = len(self.node_client.kvm.list())
        self.assertEqual(kvm_after_uninstall, self.kvm_before)
        print(colored(' [*] Done!', 'green'))

    @parameterized.expand(['ubuntu', 'zero-os'])
    def test005_shutdown_vm(self, operating_system):
        """ DM-004 Shutdown the vm

         **Test Scenario:**

         #. Install a vm, assert its working well
         #, Create a file in the mounted disk
         #. Shutdown the vm, assert it was deleted
         #. Get machine status, It should be halted
         #. Install it again, It should working fine
         #. Assert the created file is there
         """
        self.install_vm(operating_system=operating_system)

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
    def test006_pause_resume_vm(self, operating_system):
        """ DM-005 pause the vm

         **Test Scenario:**

         #. Install a vm, assert its working well
         #, pause the vm, its state should be paused
         #, You can't access the vm in case of its status is pause
         #. resume the vm, its state should be ok
         """
        self.install_vm(operating_system)
        self.vm_action(action='pause')
        self.vm_info = self.vm_action(action='info')
        self.assertEqual(self.vm_info.result['status'], 'paused')

        print(colored(' [*] Resume the vm, its state should be ok', 'white'))
        self.vmservice.schedule_action('resume').wait(die=True)
        self.vm_info = self.vm_action(action='info')
        self.assertEqual(self.vm_info.result['status'], 'running')

    def test007_reboot_vm(self):
        """ DM-006
         *pause the vm*

         **Test Scenario:**

         #. Install a vm, assert its working well
         #, Create a file in the attached disk
         #, Reboot the vm, should succeed
         #. Check the created file, should be there
        """
        self.install_vm(operating_system='ubuntu')

        print(colored(' [*] Create a file in the mounted disk'), 'white')
        time.sleep(60)
        res, err = self.ssh_vm_execute_command(cmd='touch /mnt/text.txt')

        print(colored(' [*] Reboot the vm, should succeed', 'white'))
        self.vmservice.schedule_action('reboot').wait(die=True)
        print(colored(' [*] Done!', 'green'))

        print(colored(" [*] Assert the created file is there", 'white'))
        result, error = self.ssh_vm_execute_command(cmd='ls /mnt')
        self.assertEqual(len(result), 1)


    def test008_reinstall_vm_with_many_disks(self):
        """ DM-008

         *Install a vm with many disks*

         **Test Scenario:**

         #. Install a vm with many disks, assert its working well
         #. Uninstall it
         #. Install it again
        """
