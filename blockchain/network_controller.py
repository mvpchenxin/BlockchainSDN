
import sys

import pox3.lib.packet as pac
from pox3.boot import boot
from pox3.core import core

import pox3.opennew_chain.libopennew_chain_01 as of

from Blockchain import Blockchain


if __name__ != "__main__":
    LOG = core.getLogger()


class Controller(object):


    def __init__(self, connection):
        self.connection = connection
        connection.addListeners(self)
        self.mac_to_port = {}
        self.blockchain = Blockchain()

    def packet_resend(self, packet_in, out_port):
        message = of.ofp_packet_out()
        message.data = packet_in
        action = of.ofp_action_output(port=out_port)
        message.actions.append(action)
        self.connection.send(message)

    def chain_new_chain(self, new_chain):
        for b in self.blockchain.chain:
            if b.transactions == new_chain:
                return True
        return False

    def act_like_switch(self, packet, packet_in):
        '''
        Act like a switch by learning the mappings between the MACs and ports
        :param packet The packet processed at this point
        :param packet_in The packet to pass
        '''
        pl = packet.payload
        if len(packet_in.data) == packet_in.total_len:
            self.mac_to_port[packet.src] = packet_in.in_port
            if isinstance(pl, pac.ipv4):
                if pl.protocol == pac.ipv4.TCP_PROTOCOL:
                    src = pl.srcip
                    dst = pl.dstip
                    new_chain = f"{src} -> {dst}"
                    tcp_pl = pl.next.payload.decode()
                    if tcp_pl.find("GET") == 0:
                        route = tcp_pl[4:tcp_pl.find("HTTP") - 1]
                        if "data" in route:
                            if not self.chain_new_chain(new_chain):
                                LOG.debug("new_chain %s is not allowed", new_chain)
                                return
                        elif "add" in route:
                            if self.blockchain.mining(new_chain):
                                LOG.debug("Added acceptable new_chain %s", new_chain)
                            else:
                                return
            if self.mac_to_port.get(packet.dst):
                self.packet_resend(packet_in, self.mac_to_port[packet.dst])
            else:
                self.packet_resend(packet_in, of.OFPP_ALL)


def controller_start():
    '''
    controller_start this controller
    '''
    def start_switch(event):
        '''
        Start up the switch
        :param event Event that triggered this
        '''
        LOG.debug("Controlling %s with this", (event.connection,))
        Controller(event.connection,)
    core.opennew_chain.addListenerByName("ConnectionUp", start_switch)


if __name__ == '__main__':
    boot(
        (["log.level", "--DEBUG"] if "--debug" in sys.argv else []) +
        ["network_controller"]
    )
