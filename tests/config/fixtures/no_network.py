import socket

import pytest


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    real_socket = socket.socket

    def guard(*args, **kwargs):
        raise RuntimeError("Network disabled in tests")

    # só bloqueia internet (AF_INET), não AF_UNIX (asyncio usa isso)
    def safe_socket(family, *args, **kwargs):
        if family == socket.AF_INET:
            return guard()
        return real_socket(family, *args, **kwargs)

    monkeypatch.setattr(socket, "socket", safe_socket)
