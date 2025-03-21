from src import config
from src.nodes.BaseNode import NodeColor
from src.utils import ip_tools
from src.utils.protocol_msgs import MsgType, decode_msg, send_monitor_color_request_broadcast
from src.utils.sorted_structs import SortedDict
import asyncio


#################################################################################
# MonitorNode
#################################################################################
class MonitorNode:
    def __init__(self):
        self.my_ip = None
        self.node_dict = SortedDict()

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
        ##############################################

        if msg_code == MsgType.MONITOR_COLOR_RESPONSE.value:
            self.node_dict[sender_ip] = NodeColor(data).name
            print(self.node_dict)

    async def timer_task(self):
        while True:
            send_monitor_color_request_broadcast()
            await asyncio.sleep(config.MONITOR_COLOR_POLL_RATE)
