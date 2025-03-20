from enum import Enum
import socket
import config


class MsgType(Enum):
    ELECTION = 1
    VICTORY = 2
    LEADER_REQUEST = 3
    LEADER_RESPONSE = 4
    SET_TO_RED = 5
    SET_TO_GREEN = 6
    KEEPALIVE = 7


#################################################################################
# Generic functions
#################################################################################

def send_broadcast(msg_type: MsgType):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(str(msg_type.value).encode('utf-8'), (config.BROADCAST_IP, config.DEFAULT_LISTENING_PORT))


def send_unicast(msg_type: MsgType, peer):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(str(msg_type.value).encode('utf-8'), (peer, config.DEFAULT_LISTENING_PORT))


#################################################################################
# Derived functions
#################################################################################

def send_election_broadcast():
    print("Sending election broadcast")
    send_broadcast(MsgType.ELECTION)


def send_election_unicast(peer):
    print("Sending election unicast:", peer)
    send_unicast(MsgType.ELECTION, peer)


def send_victory_broadcast():
    print("Sending victory broadcast")
    send_broadcast(MsgType.VICTORY)


def send_leader_request_broadcast():
    print("Sending leader request broadcast")
    send_broadcast(MsgType.LEADER_REQUEST)


def send_leader_response_unicast(peer):
    print("Sending leader response unicast:", peer)
    send_unicast(MsgType.LEADER_RESPONSE, peer)


def send_set_to_red_unicast(peer):
    print("Sending set to red unicast:", peer)
    send_unicast(MsgType.SET_TO_RED, peer)


def send_set_to_green_unicast(peer):
    print("Sending set to green unicast:", peer)
    send_unicast(MsgType.SET_TO_GREEN, peer)


def send_keepalive_unicast(peer):
    print("Sending keepalive unicast:", peer)
    send_unicast(MsgType.KEEPALIVE, peer)
