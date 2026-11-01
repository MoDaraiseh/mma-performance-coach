"""Exercise real relay sockets without Docker or changes to the existing staging DB."""

import importlib.util
import socket
import socketserver
import threading
import time
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


def test_relay_rejects_excess_connections_and_releases_capacity():
    spec = importlib.util.spec_from_file_location(
        "staging_relay_capacity", Path(__file__).resolve().parents[2] / "deploy/staging_relay.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    entered = threading.Event()
    release = threading.Event()

    class Upstream(socketserver.BaseRequestHandler):
        def handle(self):
            self.request.recv(1)
            entered.set()
            release.wait(3)
            self.request.sendall(b"ok")

    with socketserver.TCPServer(("127.0.0.1", 0), Upstream) as upstream:
        threading.Thread(target=upstream.serve_forever, daemon=True).start()
        with module.RelayServer(("127.0.0.1", 0), upstream.server_address) as relay:
            relay.slots = threading.BoundedSemaphore(1)
            threading.Thread(target=relay.serve_forever, daemon=True).start()
            try:
                with socket.create_connection(relay.server_address, timeout=2) as first:
                    first.sendall(b"x")
                    first.shutdown(socket.SHUT_WR)
                    assert entered.wait(2)
                    with socket.create_connection(relay.server_address, timeout=2) as excess:
                        assert excess.recv(1) == b""
                    release.set()
                    assert first.recv(2) == b"ok"
                deadline = time.monotonic() + 2
                while not relay.slots.acquire(blocking=False):
                    assert time.monotonic() < deadline
                    time.sleep(0.01)
                relay.slots.release()
            finally:
                release.set()
                relay.shutdown()
                upstream.shutdown()


def test_relay_upstream_failure_is_private_and_reclaims_slot(capsys):
    spec = importlib.util.spec_from_file_location(
        "staging_relay_failure", Path(__file__).resolve().parents[2] / "deploy/staging_relay.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with socket.socket() as unused:
        unused.bind(("127.0.0.1", 0))
        unavailable = unused.getsockname()
    with module.RelayServer(("127.0.0.1", 0), unavailable) as relay:
        relay.slots = threading.BoundedSemaphore(1)
        threading.Thread(target=relay.serve_forever, daemon=True).start()
        try:
            with socket.create_connection(relay.server_address, timeout=7) as client:
                assert client.recv(1) == b""
            deadline = time.monotonic() + 2
            while not relay.slots.acquire(blocking=False):
                assert time.monotonic() < deadline
                time.sleep(0.01)
            relay.slots.release()
        finally:
            relay.shutdown()
    assert capsys.readouterr().err == ""
