import asyncio
import src.config
import src.nodes.BaseNode
import src.utils.UDPServer
import os

from src.nodes.MonitorNode import MonitorNode


#################################################################################
# MAIN
#################################################################################

async def main():
    loop = asyncio.get_running_loop()

    transport, udp_server = await loop.create_datagram_endpoint(
        src.utils.UDPServer.UDPServer,
        local_addr=(src.config.DEFAULT_LISTENING_IP, src.config.DEFAULT_LISTENING_PORT))

    monitor_mode = os.getenv("MONITOR_MODE")
    if monitor_mode == "active":
        print("Running in MONITOR mode")
        monitor_node = MonitorNode()
        udp_server.set_processing_func(monitor_node.process_msg)
        asyncio.create_task(monitor_node.timer_task())
    else:
        print("Running in BASE mode")
        base_node = src.nodes.BaseNode.BaseNode()
        udp_server.set_processing_func(base_node.process_msg)
        # This sleep is needed or the first send_leader_request_broadcast() won't work (???)
        await asyncio.sleep(src.config.KEEPALIVE_INTERVAL)
        asyncio.create_task(base_node.timer_task())

    try:
        await asyncio.Future()
    finally:
        transport.close()


if __name__ == "__main__":
    asyncio.run(main())
