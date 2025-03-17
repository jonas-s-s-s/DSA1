import config
import asyncio
from enum import Enum
import json
import socket
import heapq
import ip_tools

#################################################################################
# TYPES
#################################################################################
class MessageType(Enum):
    DISCOVERY = 1
    ADVERTISEMENT = 2
    KEEPALIVE = 3
    REQUEST = 4
    REQUEST_ACK = 5


class NodeColor(Enum):
    INIT = 1
    RED = 2
    GREEN = 3

class SortedDict:
    def __init__(self, mapping=None):
        """
        Initializes the SortedDict.
        :param mapping: Optional dictionary to initialize the sorted dict.
        """
        self._dict = {}
        self._keys = []
        if mapping:
            for key, value in mapping.items():
                self[key] = value

    def __setitem__(self, key, value):
        """
        Sets a key-value pair and maintains sorted order by key.
        """
        if key not in self._dict:
            heapq.heappush(self._keys, key)
        self._dict[key] = value

    def __delitem__(self, key):
        """
        Removes a key from the dictionary.
        """
        if key in self._dict:
            self._keys.remove(key)
            heapq.heapify(self._keys)
            del self._dict[key]
        else:
            raise KeyError(f"Key {key} not found in SortedDict.")

    def __getitem__(self, key):
        """
        Retrieves a value by key.
        """
        return self._dict[key]

    def pop(self):
        """
        Removes and returns the key with the smallest key.
        """
        if not self._keys:
            raise KeyError("pop from empty SortedDict")
        key = heapq.heappop(self._keys)
        value = self._dict.pop(key)
        return key, value

    def items(self):
        """
        Returns sorted (key, value) pairs.
        """
        return [(key, self._dict[key]) for key in sorted(self._keys)]

    def keys(self):
        """
        Returns keys in sorted order.
        """
        return sorted(self._keys)

    def values(self):
        """
        Returns values sorted by their corresponding keys.
        """
        return [self._dict[key] for key in sorted(self._keys)]

    def __len__(self):
        """
        Returns the number of items in the dictionary.
        """
        return len(self._dict)

    def __iter__(self):
        """
        Returns an iterator over keys sorted by their values.
        """
        return iter(self.keys())

    def __repr__(self):
        """
        Returns a string representation of the sorted dictionary.
        """
        return f"SortedDict({self.items()})"

#################################################################################
# GLOBAL STATE
#################################################################################

nodes_table = SortedDict()
my_ip = None
lower_peer = None
higher_peer = None


#################################################################################
# MESSAGE PROCESSING
#################################################################################
def encode_msg(msg_type: MessageType, data=""):
    return json.dumps({"type": msg_type.value, "data": data}).encode('utf-8')


def decode_msg(msg):
    return json.loads(msg)


def process_discovery_msg(sender_addr):
    global lower_peer, higher_peer
    dist_to_sender = ip_tools.get_ip_distance(my_ip, sender_addr)

    if dist_to_sender == 0:
        return

    # TODO: clean up
    if lower_peer is None and dist_to_sender < 0:
        lower_peer = sender_addr
        print("IF1 - LP is now", sender_addr)
    elif higher_peer is None and dist_to_sender > 0:
        higher_peer = sender_addr
        print("IF2 - HP is now", sender_addr)
    elif lower_peer is not None and ip_tools.get_ip_distance(my_ip, lower_peer) < dist_to_sender:
        lower_peer = sender_addr
        print("IF3 - LP is now", sender_addr)
    elif higher_peer is not None and ip_tools.get_ip_distance(my_ip, higher_peer) > dist_to_sender:
        higher_peer = sender_addr
        print("IF4 - HP is now", sender_addr)



def process_udp_msg(sender_addr, msg: str):
    global my_ip
    if my_ip is None:
        my_ip = ip_tools.get_ip(config.IP_PREFIX)

    print(my_ip)
    if sender_addr[0] == my_ip:
        return

    parsed_msg = decode_msg(msg)
    print("Received UDP message from {}:{}".format(sender_addr, msg))
    print(parsed_msg["type"], ":", parsed_msg["data"])

    if parsed_msg["type"] == MessageType.DISCOVERY.value:
        process_discovery_msg(sender_addr[0])


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
        process_udp_msg(addr, message)

    def error_received(self, exc):
        print(f"Error received: {exc}")

    def connection_lost(self, exc):
        print("Closing UDP server")


def send_discovery_broadcast():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(encode_msg(MessageType.DISCOVERY, "Discovery"), (config.BROADCAST_IP, config.DEFAULT_LISTENING_PORT))
    sock.close()


def send_keepalive(peer):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(encode_msg(MessageType.KEEPALIVE, "Keepalive"), (peer, config.DEFAULT_LISTENING_PORT))
    sock.close()

#################################################################################
# KEEPALIVE
#################################################################################

async def keepalive_task():
    while True:
        print("Executing keepalive task...")

        if lower_peer is None and higher_peer is None:
            send_discovery_broadcast()
        else:
            if lower_peer is not None:
                send_keepalive(lower_peer)
            if higher_peer is not None:
                send_keepalive(higher_peer)

        await asyncio.sleep(config.KEEPALIVE_INTERVAL)


#################################################################################
# MAIN
#################################################################################

async def main():
    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        UDPListener,
        local_addr=(config.DEFAULT_LISTENING_IP, config.DEFAULT_LISTENING_PORT))

    send_discovery_broadcast()

    asyncio.create_task(keepalive_task())

    try:
        await asyncio.Future()
    finally:
        transport.close()


asyncio.run(main())
