import asyncio
from enum import Enum
import config
import ip_tools
from sorted_structs import SortedDict
from messages import *


#################################################################################
# TYPES
#################################################################################
class NodeColor(Enum):
    INIT = 1
    RED = 2
    GREEN = 3


class ElectionState(Enum):
    SENT_LEADER_REQUEST = 1  # This node has sent a LEADER REQUEST message
    SENT_ELECTION_BROADCAST = 2
    ELECTION_MSG_RECEIVED = 3  # This node has received an ELECTION message
    ELECTION_MSG_LONG_DELAY = 4  # This node has already been in state ELECTION_MSG_RECEIVED for one timeout period


#################################################################################
# GLOBAL STATE
#################################################################################

nodes_table = SortedDict()
my_ip = None
leader = None
my_color = NodeColor.INIT
election_state = None


#################################################################################
# MESSAGE PROCESSING
#################################################################################


def process_msg(sender_addr, msg: str):
    ### Get our IP
    global my_ip
    if my_ip is None:
        my_ip = ip_tools.get_ip(config.IP_PREFIX)
    if sender_addr[0] == my_ip:
        return

    ### Process each message depending on the type
    sender_ip = sender_addr[0]
    global leader, election_state, my_color
    print("Node {} received UDP message from {}:{}".format(my_ip,sender_addr, msg))

    if int(msg) == MessageType.ELECTION.value:
        if ip_tools.is_higher_ip(sender_ip, my_ip):
            # There is a node with higher IP in the election
            election_state = ElectionState.ELECTION_MSG_RECEIVED
        else:
            # This node has lower IP than us, inform it
            send_election_unicast(sender_ip)
            election_state = None  # TODO: Maybe SENT_LEADER_REQUEST?
            leader = None

    elif int(msg) == MessageType.VICTORY.value:
        # Another node has won the election
        leader = sender_ip
        election_state = None

    elif int(msg) == MessageType.LEADER_REQUEST.value:
        if leader == "THIS":
            # We are the leader, inform sender of this fact
            send_leader_response_unicast(sender_ip)

    elif int(msg) == MessageType.LEADER_RESPONSE.value:
        leader = sender_ip
        election_state = None

    elif int(msg) == MessageType.SET_TO_RED.value:
        my_color = NodeColor.RED

    elif int(msg) == MessageType.SET_TO_GREEN.value:
        my_color = NodeColor.GREEN

    elif int(msg) == MessageType.KEEPALIVE.value:
        pass

    else:
        print(f"Ignoring this message due to unknown message type: {msg}")


#################################################################################
# UDP SERVER
#################################################################################

class UDPListener:
    def __init__(self):
        pass

    def connection_made(self, transport):
        self.transport = transport
        print("UDP server is listening for packets...")

    def datagram_received(self, data, addr):
        message = data.decode()
        print("Received:", addr, data)
        process_msg(addr, message)

    def error_received(self, exc):
        print(f"Error received: {exc}")

    def connection_lost(self, exc):
        print("Closing UDP server")


#################################################################################
# KEEPALIVE
#################################################################################

async def timer_task():
    while True:
        print("Executing timer task...")
        global election_state, leader

        if leader is None:
            if election_state is None:
                # We don't have a leader - request a leader
                send_leader_request_broadcast()
                election_state = ElectionState.SENT_LEADER_REQUEST
            elif election_state == ElectionState.SENT_LEADER_REQUEST:
                # No response to LEADER REQUEST, start election
                send_election_broadcast()
                election_state = ElectionState.SENT_ELECTION_BROADCAST
            elif election_state == ElectionState.SENT_ELECTION_BROADCAST:
                # No other node has sent us ELECTION or VICTORY message before timeout, this node won the election
                send_victory_broadcast()
                leader = "THIS"
                election_state = None
            elif election_state == ElectionState.ELECTION_MSG_RECEIVED:
                # Node has been in the ELECTION_MSG_RECEIVED state for one timeout period
                # (This means node with higher IP has previously sent us ELECTION message - our node has lower priority)
                election_state = ElectionState.ELECTION_MSG_LONG_DELAY
            elif election_state == ElectionState.ELECTION_MSG_LONG_DELAY:
                # Node has not received any ELECTION messages for two timeout periods, the election process is restarted
                election_state = None
        else:
            # TODO: Send keepalive to leader
            # TODO: Validate keepalive from leader
            pass

        await asyncio.sleep(config.KEEPALIVE_INTERVAL) # TODO: Election interval? / Maybe split all election logic into separate file / section?


#################################################################################
# MAIN
#################################################################################

async def main():
    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        UDPListener,
        local_addr=(config.DEFAULT_LISTENING_IP, config.DEFAULT_LISTENING_PORT))

    # This sleep is needed or the first send_leader_request_broadcast() won't work (???) TODO: Move into UDP server init 
    await asyncio.sleep(config.KEEPALIVE_INTERVAL)

    asyncio.create_task(timer_task())

    try:
        await asyncio.Future()
    finally:
        transport.close()


asyncio.run(main())
