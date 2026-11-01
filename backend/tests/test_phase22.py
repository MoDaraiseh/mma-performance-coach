"""Exercise real relay sockets without Docker or changes to the existing staging DB."""

import importlib.util
import socket
import socketserver
import threading
from pathlib import Path


def test_relay_preserves_large_payload_and_half_close():
    spec = importlib.util.spec_from_file_location(
        "staging_relay", Path(__file__).resolve().parents[2] / "deploy/staging_relay.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    class Upstream(socketserver.BaseRequestHandler):
        def handle(self):
            chunks = []
            while chunk := self.request.recv(65536):
                chunks.append(chunk)
            self.request.sendall(b"fixed-upstream:" + b"".join(chunks))

    with socketserver.TCPServer(("127.0.0.1", 0), Upstream) as upstream:
        threading.Thread(target=upstream.serve_forever, daemon=True).start()
        with module.RelayServer(("127.0.0.1", 0), upstream.server_address) as relay:
            threading.Thread(target=relay.serve_forever, daemon=True).start()
            try:
                payload = (
                    b"Host: arbitrary.invalid\r\nCookie: synthetic\r\n" + bytes(range(256)) * 1024
                )
                with socket.create_connection(relay.server_address, timeout=5) as client:
                    client.sendall(payload)
                    client.shutdown(socket.SHUT_WR)
                    chunks = []
                    while chunk := client.recv(65536):
                        chunks.append(chunk)
                assert b"".join(chunks) == b"fixed-upstream:" + payload
            finally:
                relay.shutdown()
                upstream.shutdown()
