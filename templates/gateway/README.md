## template: github.com/jumpscale/digital_me/gateway/0.0.1

### Description:

This Gateway template provides a bridge between your own personal `private` gateway and a (public gateway)[https://github.com/zero-os/0-templates/tree/master/templates/public_gateway]
It abstracts all the logic required to create public forwards and http(s) proxies.

### Schema:

- `hostname`: Container hostname.
- `domain`: Domain for the private networks
- `nodeRobot`: Instance of the noderobot to connect to deploy private gateway
- `publicGatewayRobot`: Instance of the noderobot to connecto deploy public gateway service (will be picked automaticly)
- `portforwards`: list of Portforward tcp/udp forwards from public network to private network
- `httpproxies`: list of HTTPProxy. Reverse http/https proxy to allow one public ip to host multiple http services
- `networks`: Private networks to connect to, (public will be automaticly connected to a public gateway)

Network:
- `type`: value from enum NetworkType indicating the network type. 
- `id`: vxlan or vlan id.
- `config`: a dict of NetworkConfig.
- `name`: network's name.
- `ztClient`: reference to zerotier client to authorize this node into the zerotier network
- `hwaddr`: hardware address.
- `dhcpserver`: Config for dhcp entries to be services for this network.

NetworkConfig:
- `dhcp`: boolean indicating to use dhcp or not.
- `cidr`: cidr for this network.
- `gateway`: gateway address
- `dns`: list of dns

NetworkType enum:
- `default`
- `zerotier`
- `vlan`
- `vxlan`
- `bridge`

DHCPServer:
- `nameservers`: IPAddresses of upstream dns servers
- `hosts`: Host entries to provided leases for

Host:
- `hostname`: Hostname to pass to lease info
- `macaddress`: MACAddress used to identify lease info
- `ipaddress`: IPAddress service for this host
- `ip6address`: IP6Address service for this host
- `cloudinit`: Cloud-init data for this host

CloudInit:
- `userdata`: Userdata as string (yaml string)
- `metadata`: Metadata as string (yaml string)

PortForward:
- `protocols`: IPProtocol enum
- `srcport`: Port to forward from
- `vm`: Name of a digital me vm to connect to
- `dstport`: Port to forward to
- `name`: portforward name

IPProtocol enum:
- `tcp`
- `udp`

HTTPProxy:
- `host`: http proxy host
- `destinations`: list of destinations
- `types`: list of HTTPType enum
- `name`: http proxy name

HTTPType enum:
- `http`
- `https`

HTTPDestination:
- `vm`: Name of a digital me vm to connect to
- `port`: Port on digital me vm to connect to


### Actions:
- `install`: creates a gateway on nodeRobot, starts it and configures all services
- `add_portforward`: Adds a portforward to the firewall
- `remove_portforward`: Removes a portforward from the firewall
- `add_http_porxy`: Adds a httpproxy to the http server
- `remove_http_porxy`: Removes a httpproxy from the http server
- `add_network`: Adds a network to the gateway
- `remove_network`: Remove a network from the gateway
- `info`: Retreive information about your gateway


### Examples:

#### DSL (api interface)

```python
# create dm gw
DM_GW_UID = 'github.com/jumpscale/digital_me/gateway/0.0.1'                                            
MPYPRIVATE = 'e4da7455b2c4c429'

api = j.clients.zrobot.robots['main']
data = {
    'hostname': 'mygw',
    'domain': 'lan',
    'nodeRobot': 'main',
    'networks': [{
        'name': 'private',
        'type': 'zerotier',
        'public': False,
        'id': MPYPRIVATE,
        'ztClient': 'work'
    }],
}                                                                                           
dmgw = api.services.find_or_create(DM_GW_UID, service_name='dm_gw', data=data)         
# install
dmgw.schedule_action('install').wait(die=True)

# add proxy
proxy = {'name': 'myproxy', 'host': '192.168.59.200', 'types': ['http'], 'destinations': [{'vm': 'dmvm', 'port': 8080}]}
dmgw.schedule_action('add_http_proxy', args={'proxy': proxy}).wait(die=True) 

# remove it again
dmgw.schedule_action('add_http_proxy', args={'proxy': proxy}).wait(die=True) 
```
