from enum import Enum

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

class NodesTable:
    def __init__(self):
        self.nodes = {}

    def add_node(self, node_name: str, node_color: NodeColor):
        self.nodes[node_name] = node_color

    def remove_node(self, node_name: str):
        del self.nodes[node_name]

    def is_empty(self):
        return len(self.nodes) == 0

    def get_count(self):
        return len(self.nodes)

    def clear(self):
        self.nodes = {}