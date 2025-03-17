import json
import config as config
import msg_types as msg_types


class MsgProcessor:
    def __init__(self):
        nodes_table = msg_types.NodesTable()

    def process_udp_message(self, udp_server, sender_addr, message_json):
        print(sender_addr, "sent:", message_json)
