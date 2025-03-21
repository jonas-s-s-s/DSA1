import asyncio

import src.nodes.LeaderMode
from src.nodes.SlaveMode import SlaveMode
from src.utils import ip_tools
from src.utils.protocol_msgs import *


#################################################################################
# TYPES
#################################################################################
class NodeColor(Enum):
    INIT = 1
    RED = 2
    GREEN = 3


class ElectionState(Enum):
    INIT = 1
    SENT_LEADER_REQUEST = 2  # This node has sent a LEADER REQUEST message
    SENT_ELECTION_BROADCAST = 3
    ELECTION_MSG_RECEIVED = 4  # This node has received an ELECTION message
    ELECTION_MSG_LONG_DELAY = 5  # This node has already been in state ELECTION_MSG_RECEIVED for one timeout period


class OperationMode(Enum):
    SLAVE = 1
    LEADER = 2


#################################################################################
# BaseNode
#################################################################################

class BaseNode:
    def __init__(self):
        self.my_ip = None
        self.my_color: NodeColor = NodeColor.INIT
        self.election_state: ElectionState = ElectionState.INIT
        # BaseNode calls member functions of those two classes (depending on which mode it operates in)
        self.leader_mode: src.nodes.LeaderMode = src.nodes.LeaderMode.LeaderMode()  # TODO: Import issue
        self.slave_mode: SlaveMode = SlaveMode()
        # Starts as slave by default
        self.operation_mode: OperationMode = OperationMode.SLAVE

    def process_msg(self, sender_addr, msg):
        sender_ip = sender_addr[0]
        ### Get our IP (and ignore messages from same IP)
        if self.my_ip is None:
            self.my_ip = ip_tools.get_ip(config.IP_PREFIX)
        if sender_ip == self.my_ip:
            return
        #################################################
        msg_code, data = decode_msg(msg)
        msg_code = int(msg_code)
        if msg_code != 8: # Suppress monitor request prints
            print(f"Node {self.my_ip} received UDP message from {sender_addr}: {MsgType(msg_code).name}")
        ##############################################
        ### Process each message depending on the type

        if msg_code == MsgType.ELECTION.value:
            if ip_tools.is_higher_ip(sender_ip, self.my_ip):
                # There is a node with higher IP in the election
                self.election_state = ElectionState.ELECTION_MSG_RECEIVED
            else:
                # This node has lower IP than us, inform it
                send_election_unicast(sender_ip)
                # Sets election to INIT - will become leader earlier than nodes with ELECTION_MSG_RECEIVED
                self.election_state = ElectionState.INIT

            # Election in progress, invalidate current leader data
            self.operation_mode = OperationMode.SLAVE
            self.slave_mode.clear_leader()


        elif (msg_code == MsgType.VICTORY.value) or (msg_code == MsgType.LEADER_RESPONSE.value):
            # Another node has won the election (or response to our leader request)
            self.slave_mode.set_leader(sender_ip)
            self.operation_mode = OperationMode.SLAVE
            self.election_state = ElectionState.INIT

        elif msg_code == MsgType.LEADER_REQUEST.value:
            if self.operation_mode == OperationMode.LEADER:
                # We are the leader, inform sender of this fact
                send_leader_response_unicast(sender_ip)

        elif msg_code == MsgType.SET_TO_RED.value:
            self.set_my_color(NodeColor.RED)

        elif msg_code == MsgType.SET_TO_GREEN.value:
            self.set_my_color(NodeColor.GREEN)

        elif msg_code == MsgType.KEEPALIVE.value:
            if self.operation_mode == OperationMode.LEADER:
                self.leader_mode.got_keepalive_from_node(sender_ip, data)
            else:
                self.slave_mode.got_keepalive_from_leader()

        elif msg_code == MsgType.MONITOR_COLOR_REQUEST.value:
            # This exists only for monitoring purposes - isn't used for the algorithm
            send_monitor_color_response_unicast(sender_ip, self.my_color.value)

        else:
            print(f"Ignoring this message due to unknown message type: {msg_code}")

    async def timer_task(self):
        while True:
            print("Executing timer task...")

            ### Leader periodically checks if nodes are still alive
            if self.operation_mode == OperationMode.LEADER:
                self.leader_mode.validate_nodes_keepalive()

            ### Slave either manages election or sends keepalive to leader
            elif self.operation_mode == OperationMode.SLAVE:
                if self.slave_mode.leader is None:
                    self.evaluate_election_state()
                else:
                    self.slave_mode.keepalive_to_leader(self.my_color.value)

            ### TODO: Add separate interval for election?
            await asyncio.sleep(config.KEEPALIVE_INTERVAL)

    def evaluate_election_state(self):
        if self.election_state is ElectionState.INIT:
            # We don't have a leader - request a leader
            send_leader_request_broadcast()
            self.election_state = ElectionState.SENT_LEADER_REQUEST
        elif self.election_state == ElectionState.SENT_LEADER_REQUEST:
            # No response to LEADER REQUEST, start election
            send_election_broadcast()
            self.election_state = ElectionState.SENT_ELECTION_BROADCAST
        elif self.election_state == ElectionState.SENT_ELECTION_BROADCAST:
            # No other node has sent us ELECTION or VICTORY message before timeout, this node won the election
            send_victory_broadcast()
            self.operation_mode = OperationMode.LEADER
            self.set_my_color(NodeColor.RED)
        ############################################################################################################
        elif self.election_state == ElectionState.ELECTION_MSG_RECEIVED:
            # Node has been in the ELECTION_MSG_RECEIVED state for one timeout period
            # (This means node with higher IP has previously sent us ELECTION message - our node has lower priority)
            self.election_state = ElectionState.ELECTION_MSG_LONG_DELAY
        elif self.election_state == ElectionState.ELECTION_MSG_LONG_DELAY:
            # Node has not received any ELECTION messages for two timeout periods, the election process is restarted
            self.election_state = ElectionState.INIT

    def set_my_color(self, color: NodeColor):
        self.my_color = color
