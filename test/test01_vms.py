from test.bast_test import BaseTest
from parameterized import parameterized
import random, uuid, time
from termcolor import colored


class VMTestCases(BaseTest):

    @parameterized.expand(['ubuntu', 'zero-os'])
    def test001_create_vm(self, operting_system):
        data = {
            'nodeId': self.nodeId,
            'image': operting_system,
            'memory': random.choice([1024, 2048, 4096]),
            'zerotier': {'id': self.zt_network.id, 'ztClient': 'zt_main'},
            'configs': [{'path': '/root/.ssh/authorized_keys',
                         'content': self.ssh,
                         'name': 'sshkey'}]
        }
        vmservice = self.robot.services.find_or_create('github.com/jumpscale/digital_me/vm/0.0.1', service_name='vm107',
                                                       data=data)
        vmservice.schedule_action('install').wait(die=True)

    @parameterized.expand([('ubuntu', 1024, 10, 'btrfs', 'hdd'), ('ubuntu', 1024, 10, 'btrfs', 'ssd'),
                           ('ubuntu', 1024, 10, 'ext4', 'hdd'), ('ubuntu', 1024, 10, 'ext4', 'ssd'),
                           ('ubuntu', 1024, 10, 'ext3', 'hdd'), ('ubuntu', 1024, 10, 'ext3', 'ssd'),
                           ('ubuntu', 1024, 10, 'ext2', 'hdd'), ('ubuntu', 1024, 10, 'ext2', 'ssd'),
                           ('ubuntu', 1024, 50, 'btrfs', 'hdd'), ('ubuntu', 1024, 50, 'btrfs', 'ssd'),
                           ('ubuntu', 1024, 50, 'ext4', 'hdd'), ('ubuntu', 1024, 50, 'ext4', 'ssd'),
                           ('ubuntu', 1024, 50, 'ext3', 'hdd'), ('ubuntu', 1024, 50, 'ext3', 'ssd'),
                           ('ubuntu', 1024, 50, 'ext2', 'hdd'), ('ubuntu', 1024, 50, 'ext2', 'ssd'),
                           ('ubuntu', 1024, 100, 'btrfs', 'hdd'), ('ubuntu', 1024, 100, 'btrfs', 'ssd'),
                           ('ubuntu', 1024, 100, 'ext4', 'hdd'), ('ubuntu', 1024, 100, 'ext4', 'ssd'),
                           ('ubuntu', 1024, 100, 'ext3', 'hdd'), ('ubuntu', 1024, 100, 'ext3', 'ssd'),
                           ('ubuntu', 1024, 100, 'ext2', 'hdd'), ('ubuntu', 1024, 100, 'ext2', 'ssd'),
                           ('ubuntu', 1024, 200, 'btrfs', 'hdd'), ('ubuntu', 1024, 200, 'btrfs', 'ssd'),
                           ('ubuntu', 1024, 200, 'ext4', 'hdd'), ('ubuntu', 1024, 200, 'ext4', 'ssd'),
                           ('ubuntu', 1024, 200, 'ext3', 'hdd'), ('ubuntu', 1024, 200, 'ext3', 'ssd'),
                           ('ubuntu', 1024, 200, 'ext2', 'hdd'), ('ubuntu', 1024, 200, 'ext2', 'ssd'),
                           ('ubuntu', 2048, 10, 'btrfs', 'hdd'), ('ubuntu', 2048, 10, 'btrfs', 'ssd'),
                           ('ubuntu', 2048, 10, 'ext4', 'hdd'), ('ubuntu', 2048, 10, 'ext4', 'ssd'),
                           ('ubuntu', 2048, 10, 'ext3', 'hdd'), ('ubuntu', 2048, 10, 'ext3', 'ssd'),
                           ('ubuntu', 2048, 10, 'ext2', 'hdd'), ('ubuntu', 2048, 10, 'ext2', 'ssd'),
                           ('ubuntu', 2048, 50, 'btrfs', 'hdd'), ('ubuntu', 2048, 50, 'btrfs', 'ssd'),
                           ('ubuntu', 2048, 50, 'ext4', 'hdd'), ('ubuntu', 2048, 50, 'ext4', 'ssd'),
                           ('ubuntu', 2048, 50, 'ext3', 'hdd'), ('ubuntu', 2048, 50, 'ext3', 'ssd'),
                           ('ubuntu', 2048, 50, 'ext2', 'hdd'), ('ubuntu', 2048, 50, 'ext2', 'ssd'),
                           ('ubuntu', 2048, 100, 'btrfs', 'hdd'), ('ubuntu', 2048, 100, 'btrfs', 'ssd'),
                           ('ubuntu', 2048, 100, 'ext4', 'hdd'), ('ubuntu', 2048, 100, 'ext4', 'ssd'),
                           ('ubuntu', 2048, 100, 'ext3', 'hdd'), ('ubuntu', 2048, 100, 'ext3', 'ssd'),
                           ('ubuntu', 2048, 100, 'ext2', 'hdd'), ('ubuntu', 2048, 100, 'ext2', 'ssd'),
                           ('ubuntu', 2048, 200, 'btrfs', 'hdd'), ('ubuntu', 2048, 200, 'btrfs', 'ssd'),
                           ('ubuntu', 2048, 200, 'ext4', 'hdd'), ('ubuntu', 2048, 200, 'ext4', 'ssd'),
                           ('ubuntu', 2048, 200, 'ext3', 'hdd'), ('ubuntu', 2048, 200, 'ext3', 'ssd'),
                           ('ubuntu', 2048, 200, 'ext2', 'hdd'), ('ubuntu', 2048, 200, 'ext2', 'ssd'),
                           ('ubuntu', 4096, 10, 'btrfs', 'hdd'), ('ubuntu', 4096, 10, 'btrfs', 'ssd'),
                           ('ubuntu', 4096, 10, 'ext4', 'hdd'), ('ubuntu', 4096, 10, 'ext4', 'ssd'),
                           ('ubuntu', 4096, 10, 'ext3', 'hdd'), ('ubuntu', 4096, 10, 'ext3', 'ssd'),
                           ('ubuntu', 4096, 10, 'ext2', 'hdd'), ('ubuntu', 4096, 10, 'ext2', 'ssd'),
                           ('ubuntu', 4096, 50, 'btrfs', 'hdd'), ('ubuntu', 4096, 50, 'btrfs', 'ssd'),
                           ('ubuntu', 4096, 50, 'ext4', 'hdd'), ('ubuntu', 4096, 50, 'ext4', 'ssd'),
                           ('ubuntu', 4096, 50, 'ext3', 'hdd'), ('ubuntu', 4096, 50, 'ext3', 'ssd'),
                           ('ubuntu', 4096, 50, 'ext2', 'hdd'), ('ubuntu', 4096, 50, 'ext2', 'ssd'),
                           ('ubuntu', 4096, 100, 'btrfs', 'hdd'), ('ubuntu', 4096, 100, 'btrfs', 'ssd'),
                           ('ubuntu', 4096, 100, 'ext4', 'hdd'), ('ubuntu', 4096, 100, 'ext4', 'ssd'),
                           ('ubuntu', 4096, 100, 'ext3', 'hdd'), ('ubuntu', 4096, 100, 'ext3', 'ssd'),
                           ('ubuntu', 4096, 100, 'ext2', 'hdd'), ('ubuntu', 4096, 100, 'ext2', 'ssd'),
                           ('ubuntu', 4096, 200, 'btrfs', 'hdd'), ('ubuntu', 4096, 200, 'btrfs', 'ssd'),
                           ('ubuntu', 4096, 200, 'ext4', 'hdd'), ('ubuntu', 4096, 200, 'ext4', 'ssd'),
                           ('ubuntu', 4096, 200, 'ext3', 'hdd'), ('ubuntu', 4096, 200, 'ext3', 'ssd'),
                           ('ubuntu', 4096, 200, 'ext2', 'hdd'), ('ubuntu', 4096, 200, 'ext2', 'ssd'),
                           ('ubuntu', 8192, 10, 'btrfs', 'hdd'), ('ubuntu', 8192, 10, 'btrfs', 'ssd'),
                           ('ubuntu', 8192, 10, 'ext4', 'hdd'), ('ubuntu', 8192, 10, 'ext4', 'ssd'),
                           ('ubuntu', 8192, 10, 'ext3', 'hdd'), ('ubuntu', 8192, 10, 'ext3', 'ssd'),
                           ('ubuntu', 8192, 10, 'ext2', 'hdd'), ('ubuntu', 8192, 10, 'ext2', 'ssd'),
                           ('ubuntu', 8192, 50, 'btrfs', 'hdd'), ('ubuntu', 8192, 50, 'btrfs', 'ssd'),
                           ('ubuntu', 8192, 50, 'ext4', 'hdd'), ('ubuntu', 8192, 50, 'ext4', 'ssd'),
                           ('ubuntu', 8192, 50, 'ext3', 'hdd'), ('ubuntu', 8192, 50, 'ext3', 'ssd'),
                           ('ubuntu', 8192, 50, 'ext2', 'hdd'), ('ubuntu', 8192, 50, 'ext2', 'ssd'),
                           ('ubuntu', 8192, 100, 'btrfs', 'hdd'), ('ubuntu', 8192, 100, 'btrfs', 'ssd'),
                           ('ubuntu', 8192, 100, 'ext4', 'hdd'), ('ubuntu', 8192, 100, 'ext4', 'ssd'),
                           ('ubuntu', 8192, 100, 'ext3', 'hdd'), ('ubuntu', 8192, 100, 'ext3', 'ssd'),
                           ('ubuntu', 8192, 100, 'ext2', 'hdd'), ('ubuntu', 8192, 100, 'ext2', 'ssd'),
                           ('ubuntu', 8192, 200, 'btrfs', 'hdd'), ('ubuntu', 8192, 200, 'btrfs', 'ssd'),
                           ('ubuntu', 8192, 200, 'ext4', 'hdd'), ('ubuntu', 8192, 200, 'ext4', 'ssd'),
                           ('ubuntu', 8192, 200, 'ext3', 'hdd'), ('ubuntu', 8192, 200, 'ext3', 'ssd'),
                           ('ubuntu', 8192, 200, 'ext2', 'hdd'), ('ubuntu', 8192, 200, 'ext2', 'ssd'),
                           ('zero-os', 1024, 10, 'btrfs', 'hdd'), ('zero-os', 1024, 10, 'btrfs', 'ssd'),
                           ('zero-os', 1024, 10, 'ext4', 'hdd'), ('zero-os', 1024, 10, 'ext4', 'ssd'),
                           ('zero-os', 1024, 10, 'ext3', 'hdd'), ('zero-os', 1024, 10, 'ext3', 'ssd'),
                           ('zero-os', 1024, 10, 'ext2', 'hdd'), ('zero-os', 1024, 10, 'ext2', 'ssd'),
                           ('zero-os', 1024, 50, 'btrfs', 'hdd'), ('zero-os', 1024, 50, 'btrfs', 'ssd'),
                           ('zero-os', 1024, 50, 'ext4', 'hdd'), ('zero-os', 1024, 50, 'ext4', 'ssd'),
                           ('zero-os', 1024, 50, 'ext3', 'hdd'), ('zero-os', 1024, 50, 'ext3', 'ssd'),
                           ('zero-os', 1024, 50, 'ext2', 'hdd'), ('zero-os', 1024, 50, 'ext2', 'ssd'),
                           ('zero-os', 1024, 100, 'btrfs', 'hdd'), ('zero-os', 1024, 100, 'btrfs', 'ssd'),
                           ('zero-os', 1024, 100, 'ext4', 'hdd'), ('zero-os', 1024, 100, 'ext4', 'ssd'),
                           ('zero-os', 1024, 100, 'ext3', 'hdd'), ('zero-os', 1024, 100, 'ext3', 'ssd'),
                           ('zero-os', 1024, 100, 'ext2', 'hdd'), ('zero-os', 1024, 100, 'ext2', 'ssd'),
                           ('zero-os', 1024, 200, 'btrfs', 'hdd'), ('zero-os', 1024, 200, 'btrfs', 'ssd'),
                           ('zero-os', 1024, 200, 'ext4', 'hdd'), ('zero-os', 1024, 200, 'ext4', 'ssd'),
                           ('zero-os', 1024, 200, 'ext3', 'hdd'), ('zero-os', 1024, 200, 'ext3', 'ssd'),
                           ('zero-os', 1024, 200, 'ext2', 'hdd'), ('zero-os', 1024, 200, 'ext2', 'ssd'),
                           ('zero-os', 2048, 10, 'btrfs', 'hdd'), ('zero-os', 2048, 10, 'btrfs', 'ssd'),
                           ('zero-os', 2048, 10, 'ext4', 'hdd'), ('zero-os', 2048, 10, 'ext4', 'ssd'),
                           ('zero-os', 2048, 10, 'ext3', 'hdd'), ('zero-os', 2048, 10, 'ext3', 'ssd'),
                           ('zero-os', 2048, 10, 'ext2', 'hdd'), ('zero-os', 2048, 10, 'ext2', 'ssd'),
                           ('zero-os', 2048, 50, 'btrfs', 'hdd'), ('zero-os', 2048, 50, 'btrfs', 'ssd'),
                           ('zero-os', 2048, 50, 'ext4', 'hdd'), ('zero-os', 2048, 50, 'ext4', 'ssd'),
                           ('zero-os', 2048, 50, 'ext3', 'hdd'), ('zero-os', 2048, 50, 'ext3', 'ssd'),
                           ('zero-os', 2048, 50, 'ext2', 'hdd'), ('zero-os', 2048, 50, 'ext2', 'ssd'),
                           ('zero-os', 2048, 100, 'btrfs', 'hdd'), ('zero-os', 2048, 100, 'btrfs', 'ssd'),
                           ('zero-os', 2048, 100, 'ext4', 'hdd'), ('zero-os', 2048, 100, 'ext4', 'ssd'),
                           ('zero-os', 2048, 100, 'ext3', 'hdd'), ('zero-os', 2048, 100, 'ext3', 'ssd'),
                           ('zero-os', 2048, 100, 'ext2', 'hdd'), ('zero-os', 2048, 100, 'ext2', 'ssd'),
                           ('zero-os', 2048, 200, 'btrfs', 'hdd'), ('zero-os', 2048, 200, 'btrfs', 'ssd'),
                           ('zero-os', 2048, 200, 'ext4', 'hdd'), ('zero-os', 2048, 200, 'ext4', 'ssd'),
                           ('zero-os', 2048, 200, 'ext3', 'hdd'), ('zero-os', 2048, 200, 'ext3', 'ssd'),
                           ('zero-os', 2048, 200, 'ext2', 'hdd'), ('zero-os', 2048, 200, 'ext2', 'ssd'),
                           ('zero-os', 4096, 10, 'btrfs', 'hdd'), ('zero-os', 4096, 10, 'btrfs', 'ssd'),
                           ('zero-os', 4096, 10, 'ext4', 'hdd'), ('zero-os', 4096, 10, 'ext4', 'ssd'),
                           ('zero-os', 4096, 10, 'ext3', 'hdd'), ('zero-os', 4096, 10, 'ext3', 'ssd'),
                           ('zero-os', 4096, 10, 'ext2', 'hdd'), ('zero-os', 4096, 10, 'ext2', 'ssd'),
                           ('zero-os', 4096, 50, 'btrfs', 'hdd'), ('zero-os', 4096, 50, 'btrfs', 'ssd'),
                           ('zero-os', 4096, 50, 'ext4', 'hdd'), ('zero-os', 4096, 50, 'ext4', 'ssd'),
                           ('zero-os', 4096, 50, 'ext3', 'hdd'), ('zero-os', 4096, 50, 'ext3', 'ssd'),
                           ('zero-os', 4096, 50, 'ext2', 'hdd'), ('zero-os', 4096, 50, 'ext2', 'ssd'),
                           ('zero-os', 4096, 100, 'btrfs', 'hdd'), ('zero-os', 4096, 100, 'btrfs', 'ssd'),
                           ('zero-os', 4096, 100, 'ext4', 'hdd'), ('zero-os', 4096, 100, 'ext4', 'ssd'),
                           ('zero-os', 4096, 100, 'ext3', 'hdd'), ('zero-os', 4096, 100, 'ext3', 'ssd'),
                           ('zero-os', 4096, 100, 'ext2', 'hdd'), ('zero-os', 4096, 100, 'ext2', 'ssd'),
                           ('zero-os', 4096, 200, 'btrfs', 'hdd'), ('zero-os', 4096, 200, 'btrfs', 'ssd'),
                           ('zero-os', 4096, 200, 'ext4', 'hdd'), ('zero-os', 4096, 200, 'ext4', 'ssd'),
                           ('zero-os', 4096, 200, 'ext3', 'hdd'), ('zero-os', 4096, 200, 'ext3', 'ssd'),
                           ('zero-os', 4096, 200, 'ext2', 'hdd'), ('zero-os', 4096, 200, 'ext2', 'ssd'),
                           ('zero-os', 8192, 10, 'btrfs', 'hdd'), ('zero-os', 8192, 10, 'btrfs', 'ssd'),
                           ('zero-os', 8192, 10, 'ext4', 'hdd'), ('zero-os', 8192, 10, 'ext4', 'ssd'),
                           ('zero-os', 8192, 10, 'ext3', 'hdd'), ('zero-os', 8192, 10, 'ext3', 'ssd'),
                           ('zero-os', 8192, 10, 'ext2', 'hdd'), ('zero-os', 8192, 10, 'ext2', 'ssd'),
                           ('zero-os', 8192, 50, 'btrfs', 'hdd'), ('zero-os', 8192, 50, 'btrfs', 'ssd'),
                           ('zero-os', 8192, 50, 'ext4', 'hdd'), ('zero-os', 8192, 50, 'ext4', 'ssd'),
                           ('zero-os', 8192, 50, 'ext3', 'hdd'), ('zero-os', 8192, 50, 'ext3', 'ssd'),
                           ('zero-os', 8192, 50, 'ext2', 'hdd'), ('zero-os', 8192, 50, 'ext2', 'ssd'),
                           ('zero-os', 8192, 100, 'btrfs', 'hdd'), ('zero-os', 8192, 100, 'btrfs', 'ssd'),
                           ('zero-os', 8192, 100, 'ext4', 'hdd'), ('zero-os', 8192, 100, 'ext4', 'ssd'),
                           ('zero-os', 8192, 100, 'ext3', 'hdd'), ('zero-os', 8192, 100, 'ext3', 'ssd'),
                           ('zero-os', 8192, 100, 'ext2', 'hdd'), ('zero-os', 8192, 100, 'ext2', 'ssd'),
                           ('zero-os', 8192, 200, 'btrfs', 'hdd'), ('zero-os', 8192, 200, 'btrfs', 'ssd'),
                           ('zero-os', 8192, 200, 'ext4', 'hdd'), ('zero-os', 8192, 200, 'ext4', 'ssd'),
                           ('zero-os', 8192, 200, 'ext3', 'hdd'), ('zero-os', 8192, 200, 'ext3', 'ssd'),
                           ('zero-os', 8192, 200, 'ext2', 'hdd'), ('zero-os', 8192, 200, 'ext2', 'ssd')])
    def test002_create_vm_with_disk(self, operting_system, memory, disk_size, disk_fs, disk_type):
        print(colored(' [*] Create a machine with: %s %d %d %s %s') % (operting_system, memory, disk_size, disk_fs,
                                                                       disk_type), 'white')

        data = {
            'nodeId': self.nodeId,
            'disks': [{
                'diskType': disk_type,
                'size': disk_size,
                'mountPoint': '/mnt',
                'filesystem': disk_fs,
                'label': str(uuid.uuid4()).replace('-', '')[:10],
            }],
            'image': operting_system,
            'memory': memory,
            'zerotier': {'id': self.zt_network.id, 'ztClient': 'zt_main'},
            'configs': [{'path': '/root/.ssh/authorized_keys',
                         'content': self.ssh,
                         'name': 'sshkey'}]
        }

        vmservice = self.robot.services.find_or_create('github.com/jumpscale/digital_me/vm/0.0.1', service_name='vm107',
                                                       data=data)
        vmservice.schedule_action('install').wait(die=True)
        time.sleep(30)
        self.vm_ip = self.get_vm_zt_ip()
        import ipdb; ipdb.set_trace()

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

