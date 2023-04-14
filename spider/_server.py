import sys
import asyncio
import socket


class Server():
    def __init__(
            self, service: type = None,
            host: str = '', port: int = 8080):

        self.service = getattr(self, 'service', None) or self.service
        self.host = getattr(self, 'host', None) or host
        self.port = getattr(self, 'port', None) or port

        if self.service == None:
            raise ValueError("No service provided")

        start_callback = getattr(self, 'start', None)
        if callable(start_callback): start_callback()

    async def _tcp_server(self):
        loop = asyncio.get_running_loop()
        _server = await loop.create_server(
            lambda: self.service(self),
            sock=self.sock
        )

        async with _server:
            await _server.serve_forever()

    def start(self):
        """ Start
        Called when the server starts.
        """

    def handler(self, data):
        """ Handler
        Called to handle data received by a client.
        """

    def lost(self, exception):
        """ Lost
        Called whenever a connection disconnects or is dropped.
        """

    def serve(self, **kwargs):
        if not getattr(self, 'sock', None):
            self.sock = socket.socket()
            self.sock.bind((self.host, self.port))

        loop = asyncio.get_event_loop()
        loop.create_task(self._tcp_server())

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            loop.stop()
            loop.run_until_complete(loop.shutdown_asyncgens())

def serve(server: type):
    print("Serving", server.__name__)
    print("Press Ctrl+C to stop serving")
    _s = server()

    _s.serve()
    print("Closing")
