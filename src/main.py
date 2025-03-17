from msg_processor import MsgProcessor
import asyncio
import config as config


class UDPListener:
    def __init__(self):
        self.msg_processor: MsgProcessor = MsgProcessor()

    def connection_made(self, transport):
        self.transport = transport
        print("UDP server is listening for packets...")

    def datagram_received(self, data, addr):
        message = data.decode()
        self.msg_processor.process_udp_message(self, addr, message)
        # self.transport.sendto(data, addr)

    def error_received(self, exc):
        print(f"Error received: {exc}")

    def connection_lost(self, exc):
        print("Closing UDP server")


async def keepalive_task():
    while True:
        print("Executing keepalive task...")
        await asyncio.sleep(config.KEEPALIVE_INTERVAL)


async def main():
    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        UDPListener,
        local_addr=(config.DEFAULT_LISTENING_IP, config.DEFAULT_LISTENING_PORT))

    asyncio.create_task(keepalive_task())

    try:
        await asyncio.Future()
    finally:
        transport.close()


asyncio.run(main())
