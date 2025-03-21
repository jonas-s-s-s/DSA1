import time
from src import config
from src.utils.protocol_msgs import send_keepalive_unicast


#################################################################################
# SlaveMode
#################################################################################
class SlaveMode:
    def __init__(self):
        self.leader = None
        self.last_keepalive_from_leader = None

    def got_keepalive_from_leader(self):
        self.last_keepalive_from_leader = time.time_ns()

    def keepalive_to_leader(self, my_color):
        current_timestamp = time.time_ns()
        if self.last_keepalive_from_leader is not None:
            if current_timestamp - self.last_keepalive_from_leader > config.LEADER_DEAD_AFTER:
                # Leader is dead
                print(current_timestamp - self.last_keepalive_from_leader, ">", config.LEADER_DEAD_AFTER)
                print("My leader is dead")
                self.clear_leader()
                return

        send_keepalive_unicast(self.leader, my_color)

    def clear_leader(self):
        self.leader = None
        self.last_keepalive_from_leader = None

    def set_leader(self, leader_id):
        self.leader = leader_id
        self.last_keepalive_from_leader = time.time_ns()
