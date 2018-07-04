import time, argparse, uuid, requests
from termcolor import colored
from js9 import j


class Setup:
    """
        Goal: Create Account, Create CSs, ZOS machine, ubuntu machine with js9
    """
    def __init__(self, ovc_data, zt_token):
        self.client_ovc = j.clients.openvcloud.get(data=ovc_data)
        self.zt_token = zt_token
        self.zt_members = {}
        self.ipxe = 'ipxe: https://bootstrap.gig.tech/ipxe/v.1.4.1/c7c8172af1f387a6/farmer_id=eyJhbGciOiJFUzM4NCIsInR5cCI6IkpXVCJ9.eyJhenAiOiJ0aHJlZWZvbGQuZmFybWVycyIsImV4cCI6MTUzMDEwNDA3NSwiaXNzIjoiaXRzeW91b25saW5lIiwicmVmcmVzaF90b2tlbiI6ImtVazZEdmlWSHpJMENqYTAxSFBhTXhNOWpMckkiLCJzY29wZSI6WyJ1c2VyOm1lbWJlcm9mOmZhcm1pbmciXSwidXNlcm5hbWUiOiJ4dHJlbXgifQ.9YkyZ_6i9NMtVfn_YameKTrmPrG3TkI_5PRBbZkO-g0-0l5yEto2jOBypKSbeNiNBOzxh7HpXijqXY1x8uvyo7Tf_j2VcwEQ1XR679hsCku1A_c-Rpia0UtScz2BDJjO%20development'

    # def install_zt_host(self):
    #     print(colored(' [*] Install zerotier client', 'white'))
    #     try:
    #         j.tools.prefab.local.network.zerotier.install()
    #         j.tools.prefab.local.network.zerotier.start()
    #     except:
    #         pass
    #
    # def create_zerotier_nw(self):
    #     print(colored(' [*] Create zerotier network.', 'white'))
    #     zt_config_instance_name = str(uuid.uuid4()).replace('-', '')[:10]
    #     self.zt_name = str(uuid.uuid4()).replace('-', '')[:10]
    #     self.zt_client = j.clients.zerotier.get(instance=zt_config_instance_name, data={'token_': self.zt_token})
    #     self.zt_network = self.zt_client.network_create(public=False, name=self.zt_name, auto_assign=True,
    #                                                     subnet='10.147.19.0/24')
    #     self.ipxe = 'ipxe: http://unsecure.bootstrap.gig.tech/ipxe/development/{}/console=ttyS1,115200%20development'.format(
    #         self.zt_network.id)
    #     print(colored(' [*] ZT ID: {} '.format(self.zt_network.id), 'green'))

    # def host_join_zt(self):
    #     print(colored(' [*] Host join zt network)', 'white'))
    #     j.tools.prefab.local.network.zerotier.network_join(network_id=self.zt_network.id)
    #     zt_machine_addr = j.tools.prefab.local.network.zerotier.get_zerotier_machine_address()
    #     time.sleep(60)
    #     host_member = self.zt_network.member_get(address=zt_machine_addr)
    #     host_member.authorize()
    #     self.zt_members[host_member.address] = host_member.private_ip
    #     print(colored(' [*] Host IP {}'.format(host_member.private_ip), 'green'))

    def create_account(self):
        print(colored(' [*] Create Account', 'white'))
        self.acount_name = str(uuid.uuid4()).replace('-', '')[:10]
        self.account_client = self.client_ovc.account_get(self.acount_name)
        print(colored(' [*] Account: %s' % self.acount_name, 'green'))

    def create_cloudspace(self):
        print(colored(' [*] Create CS', 'white'))
        cs_name = str(uuid.uuid4()).replace('-', '')[:10]
        self.cs_client = self.account_client.space_get(cs_name)
        print(colored(' [*] CS: %s' % cs_name, 'green'))

    def create_zos_node(self):
        print(colored(' [*] Create ZOS machine', 'white'))
        zos_name = str(uuid.uuid4()).replace('-', '')[:10]
        self.zos_vm = self.cs_client.machine_create(name=zos_name, memsize=8, disksize=10, datadisks=[50],
                                                    image='ipxe boot', authorize_ssh=False, userdata=self.ipxe)
        time.sleep(180)
        #self.zos_ip = self._authorize_zos()
        #zos_cfg = {"host": self.zos_ip}
        #self.zos_client = j.clients.zos.get(instance=zos_name, data=zos_cfg)
        #self.zos_node = j.clients.zos.sal.get_node(instance=zos_name)
        print(colored(' [*] ZOS: %s' % zos_name, 'green'))

    # def _authorize_zos(self):
    #     zt_memebrs = self.zt_network.members_list()
    #     for zt_member in zt_memebrs:
    #         if zt_member.address not in self.zt_members.keys():
    #             zt_member.authorize()
    #             self.zt_members[zt_member.address] = zt_member.private_ip
    #             return zt_member.private_ip


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-ci", dest="client_id", help="IYO Client ID")
    parser.add_argument("-cs", dest="client_secret", help="IYO Client Secret")
    parser.add_argument("-zt", dest="zerotier_token", help="Zerotier Token")
    args = parser.parse_args()

    IYO_CLIENT_ID = args.client_id
    IYO_CLIENT_SECRET = args.client_secret
    ZT_TOKEN = args.zerotier_token

    OVC_DATA = {"address": "be-g8-3.demo.greenitglobe.com",
                "location": "be-g8-3",
                "port": 443}

    print(colored(' [*] Get jwt', 'white'))
    get_jwt = requests.post(
        'https://itsyou.online/v1/oauth/access_token?grant_type=client_credentials&client_id=%s&client_secret=%s&response_type=id_token' % (
            IYO_CLIENT_ID, IYO_CLIENT_SECRET))
    jwt = get_jwt.text

    OVC_DATA['jwt_'] = jwt

    obj = Setup(ovc_data=OVC_DATA, zt_token=ZT_TOKEN)
    # obj.install_zt_host()
    # obj.create_zerotier_nw()
    # obj.host_join_zt()
    obj.create_account()
    obj.create_cloudspace()
    obj.create_zos_node()

    #farmer_id=eyJhbGciOiJFUzM4NCIsInR5cCI6IkpXVCJ9.eyJhenAiOiJ0aHJlZWZvbGQuZmFybWVycyIsImV4cCI6MTUzMDEwNDA3NSwiaXNzIjoiaXRzeW91b25saW5lIiwicmVmcmVzaF90b2tlbiI6ImtVazZEdmlWSHpJMENqYTAxSFBhTXhNOWpMckkiLCJzY29wZSI6WyJ1c2VyOm1lbWJlcm9mOmZhcm1pbmciXSwidXNlcm5hbWUiOiJ4dHJlbXgifQ.9YkyZ_6i9NMtVfn_YameKTrmPrG3TkI_5PRBbZkO-g0-0l5yEto2jOBypKSbeNiNBOzxh7HpXijqXY1x8uvyo7Tf_j2VcwEQ1XR679hsCku1A_c-Rpia0UtScz2BDJjO
    #IPXE = https://bootstrap.gig.tech/ipxe/development/c7c8172af1f387a6/farmer_id=eyJhbGciOiJFUzM4NCIsInR5cCI6IkpXVCJ9.eyJhenAiOiJ0aHJlZWZvbGQuZmFybWVycyIsImV4cCI6MTUzMDEwNDA3NSwiaXNzIjoiaXRzeW91b25saW5lIiwicmVmcmVzaF90b2tlbiI6ImtVazZEdmlWSHpJMENqYTAxSFBhTXhNOWpMckkiLCJzY29wZSI6WyJ1c2VyOm1lbWJlcm9mOmZhcm1pbmciXSwidXNlcm5hbWUiOiJ4dHJlbXgifQ.9YkyZ_6i9NMtVfn_YameKTrmPrG3TkI_5PRBbZkO-g0-0l5yEto2jOBypKSbeNiNBOzxh7HpXijqXY1x8uvyo7Tf_j2VcwEQ1XR679hsCku1A_c-Rpia0UtScz2BDJjO


