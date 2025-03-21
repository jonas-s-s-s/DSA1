import time
import math
from src import config
import src.nodes.BaseNode as Base
from src.utils.protocol_msgs import *
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
    def __init__(self):
        self.nodes_table = SortedDict()

    def got_keepalive_from_node(self, node_id, node_color):
        send_keepalive_unicast(node_id)
        if not self.nodes_table.contains_key(node_id):
            data = NodeData(Base.NodeColor(node_color), time.time_ns())
            self.nodes_table[node_id] = data
            print("Added NEW node with key", node_id)
            self.reconfigure_nodes()
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
                self.reconfigure_nodes()
                print(self.nodes_table)

    def reconfigure_nodes(self):
        # Coloring algorithm - Leader is always RED, then nodes from the LOWEST IP are colored RED, the rest is colored GREEN
        total_nodes = len(self.nodes_table) + 1
        print("total_nodes", total_nodes)
        to_color_red = math.ceil(total_nodes * config.RED_RATIO)
        print("to_color_red", to_color_red)

        # Remove 1 because leader is RED by default
        to_color_red -= 1

        for node_id in self.nodes_table:
            #print(node_id)
            node_color = self.nodes_table[node_id].color
            if to_color_red > 0:
                if node_color != Base.NodeColor.RED:
                    #print("coloring red", node_color)
                    send_set_to_red_unicast(node_id)
                    self.nodes_table[node_id].color = Base.NodeColor.RED
                to_color_red -= 1
            elif (to_color_red <= 0) and (node_color != Base.NodeColor.GREEN):
                #print("coloring green", node_color)
                send_set_to_green_unicast(node_id)
                self.nodes_table[node_id].color = Base.NodeColor.GREEN
