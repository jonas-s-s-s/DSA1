import asyncio

class UDPServer(asyncio.DatagramProtocol):
    def __init__(self):
        self.msg_processing_ptr = None

    def connection_made(self, transport):
        self.transport = transport
        print("UDP server is listening for packets...")

    def datagram_received(self, data, addr):
        message = data.decode()
        #print("Received:", addr, data)
        if self.msg_processing_ptr is not None:
            self.msg_processing_ptr(addr, message)

    def error_received(self, exc):
        print(f"Error received: {exc}")

    def connection_lost(self, exc):
        print("Closing UDP server")

    def set_processing_func(self, processing_func):
        self.msg_processing_ptr = processing_func