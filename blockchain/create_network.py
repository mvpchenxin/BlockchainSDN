#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Create a mininet based network for the IoT
'''

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import TCLink

class IoTTopo(Topo):
    "A star shaped network"
    def build(self, **opts):
        switch = self.addSwitch(f"s1")
        for i in range(opts["n"]):
            self.addLink(
                self.addHost(f"h{i}"),
                switch,
                **{
                    "bw": 0.1,
                    "delay": "5ms",
                    "loss": 0,
                    "max_queue_size": 1000,
                    "use_htb": True
                }
            )

def run_network(n=5):
    '''
    Start up and run the network
    :param n: Number of hosts
    '''
    topo = IoTTopo(n=n)
    net = Mininet(
        topo=topo,
        link=TCLink,
        switch=OVSSwitch,
        controller=RemoteController
    )
    net.start()
    info("*** Starting a server on all hosts")
    for host in net.hosts:
        host.cmd(
            "export FLASK_APP=Server.py && flask run --host=0.0.0.0 --port=80 &"
        )
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run_network()
