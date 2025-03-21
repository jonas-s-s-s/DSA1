from enum import Enum
import socket
import json

from src import config


class MsgType(Enum):
    ELECTION = 1
    VICTORY = 2
    LEADER_REQUEST = 3
    LEADER_RESPONSE = 4
    SET_TO_RED = 5
    SET_TO_GREEN = 6
    KEEPALIVE = 7
    MONITOR_COLOR_REQUEST = 8
    MONITOR_COLOR_RESPONSE = 9


def encode_msg(msg_type: MsgType, data=""):
    return json.dumps({"type": msg_type.value, "data": data}).encode('utf-8')


def decode_msg(msg):
    decoded = json.loads(msg)
    return decoded['type'], decoded['data']


#################################################################################
# Generic functions
#################################################################################

def send_broadcast(msg_type: MsgType, data=""):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(encode_msg(msg_type, data), (config.BROADCAST_IP, config.DEFAULT_LISTENING_PORT))


def send_unicast(msg_type: MsgType, peer, data=""):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(encode_msg(msg_type, data), (peer, config.DEFAULT_LISTENING_PORT))


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


def send_keepalive_unicast(peer, data=""):
    print("Sending keepalive unicast:", peer)
    send_unicast(MsgType.KEEPALIVE, peer, data)


def send_monitor_color_request_broadcast():
    # print("Sending monitor color request broadcast")
    send_broadcast(MsgType.MONITOR_COLOR_REQUEST)


def send_monitor_color_response_unicast(peer, data):
    # print("Sending monitor color response unicast:", peer)
    send_unicast(MsgType.MONITOR_COLOR_RESPONSE, peer, data)
