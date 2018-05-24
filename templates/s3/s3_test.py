from js9 import j
data = {
    'vmDiskSize': 10,
    'vmZerotier': {
        'id': 'test',
        'ztClient': 'test',
    },
    'nodeRobot': 'local',
}
api = j.clients.zrobot.robots['local']
vm = api.services.create('github.com/jumpscale/digital_me/s3/0.0.1','s3test', data)
vm.schedule_action('install')
# service = api.services.get(name="s3test")
# service.delete()
# service = api.services.get(name="vm1")
# service.delete()