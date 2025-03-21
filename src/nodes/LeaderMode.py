import time

from src import config
import src.nodes.BaseNode as Base
from src.utils.protocol_msgs import send_keepalive_unicast
from src.utils.sorted_structs import SortedDict


#################################################################################
# TYPES
#################################################################################

class NodeData:
    def __init__(self, color, last_seen):
        self.last_seen = last_seen
        self.color = color

    def __repr__(self):
        return f"NodeData({self.last_seen}, {self.color})"


#################################################################################
# LeaderMode
#################################################################################

class LeaderMode:
    def __init__(self, base_node):
        self.nodes_table = SortedDict()
        self.base_node: Base.BaseNode = base_node

    def got_keepalive_from_node(self, node_id):
        send_keepalive_unicast(node_id)
        if not self.nodes_table.contains_key(node_id):
            data = NodeData(Base.NodeColor.INIT, time.time_ns())
            self.nodes_table[node_id] = data
            print("Added NEW node with key", node_id)
            # TODO recompute node assignments
            print(self.nodes_table)
        else:
            self.nodes_table[node_id].last_seen = time.time_ns()

    def validate_nodes_keepalive(self):
        current_time = time.time_ns()

        for key in self.nodes_table:
            data = self.nodes_table[key]
            if current_time - data.last_seen > config.NODE_DEAD_AFTER:
                del self.nodes_table[key]
                print("Removed DEAD node with key", key)
                # TODO recompute node assignments
                print(self.nodes_table)
