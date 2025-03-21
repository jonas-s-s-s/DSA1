import asyncio
from enum import Enum
import config
import ip_tools
from sorted_structs import SortedDict
from protocol_msgs import *
from udp_server import UDPServer
import time


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

class NodeData:
    def __init__(self, color, last_seen):
        self.last_seen = last_seen
        self.color = color

    def __repr__(self):
        return f"NodeData({self.last_seen}, {self.color})"

#################################################################################
# GLOBAL STATE
#################################################################################

nodes_table = SortedDict()
my_ip = None
leader = None
my_color = NodeColor.INIT
election_state = None

last_keepalive_from_leader = None


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
    print("Node {} received UDP message from {}:{}".format(my_ip, sender_addr, msg))

    if int(msg) == MsgType.ELECTION.value:
        if ip_tools.is_higher_ip(sender_ip, my_ip):
            # There is a node with higher IP in the election
            election_state = ElectionState.ELECTION_MSG_RECEIVED
        else:
            # This node has lower IP than us, inform it
            send_election_unicast(sender_ip)
            clear_leader()

    elif int(msg) == MsgType.VICTORY.value:
        # Another node has won the election
        set_leader(sender_ip)

    elif int(msg) == MsgType.LEADER_REQUEST.value:
        if am_i_leader():
            # We are the leader, inform sender of this fact
            send_leader_response_unicast(sender_ip)

    elif int(msg) == MsgType.LEADER_RESPONSE.value:
        set_leader(sender_ip)

    elif int(msg) == MsgType.SET_TO_RED.value:
        my_color = NodeColor.RED

    elif int(msg) == MsgType.SET_TO_GREEN.value:
        my_color = NodeColor.GREEN

    elif int(msg) == MsgType.KEEPALIVE.value:
        if am_i_leader():
            got_keepalive_from_node(sender_ip)
        else:
            got_keepalive_from_leader()

    else:
        print(f"Ignoring this message due to unknown message type: {msg}")


#################################################################################
# LEADER LOGIC
#################################################################################
def got_keepalive_from_node(node_id):
    send_keepalive_unicast(node_id)
    if not nodes_table.contains_key(node_id):
        data = NodeData(NodeColor.INIT, time.time_ns())
        nodes_table[node_id] = data
        print("Added NEW node with key", node_id)
        # TODO recompute node assignments
        print(nodes_table)
    else:
        nodes_table[node_id].last_seen = time.time_ns()


def validate_nodes_keepalive():
    current_time = time.time_ns()

    for key in nodes_table:
        data = nodes_table[key]
        if current_time - data.last_seen > config.NODE_DEAD_AFTER:
            del nodes_table[key]
            print("Removed DEAD node with key", key)
            # TODO recompute node assignments
            print(nodes_table)

#################################################################################
# SLAVE LOGIC
#################################################################################
def got_keepalive_from_leader():
    global last_keepalive_from_leader
    last_keepalive_from_leader = time.time_ns()


def keepalive_to_leader():
    current_timestamp = time.time_ns()
    if last_keepalive_from_leader is not None:
        if current_timestamp - last_keepalive_from_leader > config.LEADER_DEAD_AFTER:
            # Leader is dead
            print(current_timestamp - last_keepalive_from_leader, ">", config.LEADER_DEAD_AFTER)
            print("My leader is dead")
            clear_leader()
            return

    send_keepalive_unicast(leader)


#################################################################################
# TIMER TASK
#################################################################################

async def timer_task():
    while True:
        print("Executing timer task...")
        global leader

        if leader is None:
            evaluate_election_state()
        else:
            if am_i_leader():
                validate_nodes_keepalive()
            else:
                keepalive_to_leader()

        await asyncio.sleep(config.KEEPALIVE_INTERVAL)
        # TODO: Election interval? / Maybe split all election logic into separate file / section?


def evaluate_election_state():
    global election_state, leader

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
        set_me_as_leader()
    ############################################################################################################
    elif election_state == ElectionState.ELECTION_MSG_RECEIVED:
        # Node has been in the ELECTION_MSG_RECEIVED state for one timeout period
        # (This means node with higher IP has previously sent us ELECTION message - our node has lower priority)
        election_state = ElectionState.ELECTION_MSG_LONG_DELAY
    elif election_state == ElectionState.ELECTION_MSG_LONG_DELAY:
        # Node has not received any ELECTION messages for two timeout periods, the election process is restarted
        election_state = None


#################################################################################
# SETTING / CLEARING LEADER
#################################################################################

def set_me_as_leader():
    set_leader("THIS")


def am_i_leader():
    return leader == "THIS"


def clear_leader():
    global leader, election_state, last_keepalive_from_leader
    leader = None
    election_state = None
    last_keepalive_from_leader = None


def set_leader(leader_id):
    global leader, election_state, last_keepalive_from_leader
    leader = leader_id
    election_state = None
    last_keepalive_from_leader = time.time_ns()


#################################################################################
# MAIN
#################################################################################

async def main():
    loop = asyncio.get_running_loop()

    transport, udp_server = await loop.create_datagram_endpoint(
        UDPServer,
        local_addr=(config.DEFAULT_LISTENING_IP, config.DEFAULT_LISTENING_PORT))

    udp_server.set_processing_func(process_msg)

    # This sleep is needed or the first send_leader_request_broadcast() won't work (???)
    await asyncio.sleep(config.KEEPALIVE_INTERVAL)

    asyncio.create_task(timer_task())

    try:
        await asyncio.Future()
    finally:
        transport.close()

if __name__ == "__main__":
    asyncio.run(main())
