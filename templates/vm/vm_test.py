from unittest import TestCase
from unittest.mock import MagicMock, patch, call
import tempfile
import shutil
import os

import pytest

from js9 import j
from vm import Vm, ZT_TEMPLATE_UID, VDISK_TEMPLATE_UID, VM_TEMPLATE_UID
from zerorobot.template.state import StateCheckError
from zerorobot import config
from zerorobot.template_uid import TemplateUID

from JumpScale9Zrobot.test.utils import ZrobotBaseTest


class TestVmTemplate(ZrobotBaseTest):

    @classmethod
    def setUpClass(cls):
        super().preTest(os.path.dirname(__file__), Vm)
        cls.valid_data = {
            'cpu': 1,
            'image': 'ubuntu',
            'memory': 128,
            'zerotier': {
                'id': 'id',
                'ztClient': 'main',
            },
            'disks': [{
                'diskType': 'hdd',
                'size': 10,
                'mountPoint': '/mnt',
                'filesystem': 'btrfs',
                'name': 'test',
            }],
            'configs': [],
            'ztIdentity': '',
            'nodeRobot': 'main',
            'nodeVm': '',
        }
        cls.vnc_port = 5900

    def setUp(self):
        patch('js9.j.clients', MagicMock()).start()

    def tearDown(self):
        patch.stopall()

    def test_invalid_data(self):
        """
        Test creating a vm with invalid data
        """
        with pytest.raises(ValueError, message='template should fail to instantiate if data dict is missing the nodeRobot'):
            vm = Vm(name='vm', data={})
            vm.validate()

        with pytest.raises(ValueError, message='template should fail to instantiate if image is not valid'):
            vm = Vm(name='vm', data={'nodeRobot': 'main', 'image': 'test'})
            vm.validate()

        with pytest.raises(ValueError, message='template should fail to instantiate if zerotier dict is missing id'):
            vm = Vm(name='vm', data={'nodeRobot': 'main', 'image': 'ubuntu', 'zerotier': {'id': ''}})
            vm.validate()

        with pytest.raises(ValueError, message='template should fail to instantiate if zerotier dict is missing ztClient'):
            vm = Vm(name='vm', data={'nodeRobot': 'main', 'image': 'ubuntu', 'zerotier': {'id': 'id'}})
            vm.validate()

    def test_valid_data(self):
        """
        Test creating a vm service with valid data
        """
        vm = Vm('vm', data=self.valid_data)
        vm.validate()
        assert vm.data == self.valid_data

    def test_node_api(self):
        """
        Test the _node_api property
        """
        vm = Vm('vm', data=self.valid_data)
        patch('js9.j.clients.zrobot',  MagicMock(robots={'main': 'node_api'})).start()

        assert vm._node_api == 'node_api'

    def test_node_vm(self):
        """
        Test the _node_api property
        """
        vm = Vm('vm', data=self.valid_data)
        vm._node_api.services.get = MagicMock(return_value='service')
        assert vm._node_vm == 'service'

    def test_install_vm(self):
        """
        Test successfully creating a vm
        """
        disk = self.valid_data['disks'][0]
        vm = Vm('vm', data=self.valid_data)
        zt_client = MagicMock()
        zt_client.schedule_action.return_value.wait.return_value.result = 'token'
        vm.api.services.get = MagicMock(return_value=zt_client)
        create = vm._node_api.services.create
        create.return_value.schedule_action.return_value.wait.return_value.result = 'url'
        vm.install()
        zt_client.schedule_action.assert_called_once_with('token')
        vm._node_api.services.find_or_create.assert_called_once_with(ZT_TEMPLATE_UID, self.valid_data['zerotier']['ztClient'], {'token': 'token'})
        create.return_value.schedule_action.assert_has_calls([call('install'), call('private_url'), call('install')], any_order=True)

        disks = [{
            'url': 'url',
            'name': disk['name'],
            'mountPoint': disk['mountPoint'],
            'filesystem': disk['filesystem'],
        }]

        vm_data = {
            'memory': self.valid_data['memory'],
            'cpu': self.valid_data['cpu'],
            'disks': disks,
            'configs': self.valid_data['configs'],
            'ztIdentity': self.valid_data['ztIdentity'],
            'nics': [{
                'id': self.valid_data['zerotier']['id'],
                'type': 'zerotier',
                'ztClient': self.valid_data['zerotier']['ztClient'],
                'name': 'zerotier_nic',
            }],
            'flist': 'https://hub.gig.tech/gig-bootable/ubuntu:lts.flist'
        }
        vdisk_create = call(VDISK_TEMPLATE_UID, '_'.join([vm.guid, disk['name']]), data=disk)
        vm_create = call(VM_TEMPLATE_UID, vm.guid, data=vm_data)
        create.assert_has_calls([vdisk_create, vm_create], any_order=True)
        vm.state.check('actions', 'install', 'ok')
        vm.state.check('status', 'running', 'ok')

    def test_uninstall_vm(self):
        """
        Test successfully destroying the vm
        """
        vm = Vm('vm', data=self.valid_data)
        vm.state.set('actions', 'install', 'ok')
        vm.uninstall()

        vm._node_vm.schedule_action.assert_called_with('uninstall')
        with pytest.raises(StateCheckError):
            vm.state.check('actions', 'install', 'ok')
        with pytest.raises(StateCheckError):
            vm.state.check('status', 'running', 'ok')

    def test_uninstall_vm_not_installed(self):
        """
        Test uninstalling vm before install
        """
        with pytest.raises(StateCheckError, message='uninstall vm before install should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.uninstall()

    def test_shutdown_vm_not_running(self):
        """
        Test shutting down the vm without creation
        """
        with pytest.raises(StateCheckError, message='Shuting down vm that is not running should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.shutdown()

    def test_shutdown_vm(self):
        """
        Test successfully shutting down the vm
        """
        vm = Vm('vm', data=self.valid_data)
        vm.state.set('status', 'running', 'ok')
        vm.state.delete = MagicMock()

        vm.shutdown()

        vm._node_vm.schedule_action.assert_called_with('shutdown')
        vm.state.check('status', 'shutdown', 'ok')
        vm.state.delete.assert_called_with('status', 'running')

    def test_pause_vm_not_running(self):
        """
        Test pausing the vm without creation
        """
        with pytest.raises(StateCheckError, message='Pausing vm that is not running'):
            vm = Vm('vm', data=self.valid_data)
            vm.pause()

    def test_pause_vm(self):
        """
        Test successfully pausing the vm
        """
        vm = Vm('vm', data=self.valid_data)
        vm.state.set('status', 'running', 'ok')
        vm.state.delete = MagicMock()

        vm.pause()

        vm._node_vm.schedule_action.assert_called_with('pause')
        vm.state.delete.assert_called_once_with('status', 'running')
        vm.state.check('actions', 'pause', 'ok')

    def test_resume_vm_not_pause(self):
        """
        Test resume the vm without creation
        """
        with pytest.raises(StateCheckError, message='Resuming vm before pause should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.resume()

    def test_resume_vm(self):
        """
        Test successfully resume the vm
        """
        vm = Vm('vm', data=self.valid_data)
        vm.state.set('actions', 'pause', 'ok')
        vm.state.delete = MagicMock()
        vm.resume()

        vm._node_vm.schedule_action.assert_called_with('resume')
        vm.state.check('status', 'running', 'ok')
        vm.state.delete.assert_called_once_with('actions', 'pause')

    def test_reboot_vm_not_installed(self):
        """
        Test reboot the vm without creation
        """
        with pytest.raises(StateCheckError, message='Rebooting vm before install should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.reboot()

    def test_reboot_vm(self):
        """
        Test successfully reboot the vm
        """
        vm = Vm('vm', data=self.valid_data)
        vm.state.set('actions', 'install', 'ok')
        vm.reboot()
        vm._node_vm.schedule_action.assert_called_with('reboot')
        vm.state.check('status', 'rebooting', 'ok')

    def test_reset_vm_not_installed(self):
        """
        Test reset the vm without creation
        """
        with pytest.raises(StateCheckError, message='Resetting vm before install should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.reset()

    def test_reset_vm(self):
        """
        Test successfully reset the vm
        """
        vm = Vm('vm', data=self.valid_data)
        vm.state.set('actions', 'install', 'ok')
        vm.reset()
        vm._node_vm.schedule_action.assert_called_with('reset')

    def test_enable_vnc_vm_not_installed(self):
        """
        Test enable_vnc vm not installed
        """
        with pytest.raises(StateCheckError, message='enable vnc before install should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.enable_vnc()

    def test_enable_vnc(self):
        vm = Vm('vm', data=self.valid_data)
        vm.state.set('actions', 'install', 'ok')
        vm.enable_vnc()
        vm._node_vm.schedule_action.assert_called_with('enable_vnc')

    def test_disable_vnc(self):
        """
        Test disable_vnc when there is a vnc port
        """
        vm = Vm('vm', data=self.valid_data)
        vm.state.set('vnc', 90, 'ok')
        vm.state.set('actions', 'install', 'ok')
        vm.disable_vnc()
        vm._node_vm.schedule_action.assert_called_with('disable_vnc')

    def test_disable_vnc_before_enable(self):
        """
        Test disable vnc before enable
        :return:
        """
        with pytest.raises(StateCheckError, message='disable vnc before enable should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.disable_vnc()

    def test_monitor_vm_not_running(self):
        """
        Test monitor vm not running
        """
        vm = Vm('vm', data=self.valid_data)
        vm._node_vm.state.check.side_effect = StateCheckError
        vm.state.delete = MagicMock()
        vm.state.set('actions', 'install', 'ok')

        vm._monitor()
        vm.state.delete.assert_called_once_with('status', 'running')

    def test_monitor_vm_running(self):
        """
        Test monitor vm running
        """
        vm = Vm('vm', data=self.valid_data)
        vm.state.delete = MagicMock()

        vm._monitor()
        assert vm.state.delete.call_count == 0
