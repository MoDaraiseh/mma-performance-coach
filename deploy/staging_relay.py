"""Local staging TCP ingress: fixed app upstream, no credentials or HTTP rewriting."""

import select
import socket
import socketserver
import threading
import time


class RelayServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, address, upstream):
        self.upstream = upstream
        self.slots = threading.BoundedSemaphore(32)
        super().__init__(address, RelayHandler)

    def process_request(self, request, client_address):
        if not self.slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except Exception:
            self.slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.slots.release()

    def handle_error(self, request, client_address):
        # Request bytes, cookies and peer identities never enter shared logs.
        pass


class RelayHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            with socket.create_connection(self.server.upstream, timeout=5) as upstream:
                self.request.settimeout(10)
                upstream.settimeout(10)
                peers = {self.request: upstream, upstream: self.request}
                readable = list(peers)
                deadline = time.monotonic() + 300
                while readable and time.monotonic() < deadline:
                    ready, _, _ = select.select(readable, [], [], 30)
                    if not ready:
                        return
                    for source in ready:
                        data = source.recv(65536)
                        if data:
                            peers[source].sendall(data)
                        else:
                            readable.remove(source)
                            peers[source].shutdown(socket.SHUT_WR)
        except OSError:
            return


if __name__ == "__main__":
    # Neither incoming Host/URL nor user-controlled environment chooses the target.
    with RelayServer(("0.0.0.0", 8080), ("app", 8000)) as server:
        server.serve_forever()
