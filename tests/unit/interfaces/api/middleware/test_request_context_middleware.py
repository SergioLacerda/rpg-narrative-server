from types import SimpleNamespace

import pytest
from starlette.responses import Response

from rpg_narrative_server.interfaces.api import dependencies
from rpg_narrative_server.interfaces.api.middleware.request_context_middleware import (
    request_context_middleware,
)

# ---------------------------------------------------------
# DUMMIES
# ---------------------------------------------------------


class FakeRequest:
    def __init__(self, container):
        self.app = SimpleNamespace(state=SimpleNamespace(container=container))


class DummyRequest:
    method = "GET"

    class url:
        path = "/test"


class DummyContainer:
    def __init__(self):
        self.narrative = "narrative"
        self.roll_dice = "dice"
        self.end_session = "end"
        self.event_bus = "bus"

        class Health:
            async def is_ready(self):
                return True

        self.health = Health()


# ---------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------


@pytest.fixture
def fake_container(monkeypatch):
    container = DummyContainer()

    monkeypatch.setattr(
        dependencies,
        "get_container",
        lambda *args, **kwargs: container,
    )

    return container


# ---------------------------------------------------------
# MIDDLEWARE
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_request_context_success():
    async def call_next(request):
        return Response(status_code=200)

    response = await request_context_middleware(DummyRequest(), call_next)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_request_context_exception():
    async def call_next(request):
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        await request_context_middleware(DummyRequest(), call_next)


# ---------------------------------------------------------
# DEPENDENCIES
# ---------------------------------------------------------


def test_get_narrative(fake_container):
    request = FakeRequest(fake_container)

    assert dependencies.get_narrative_usecase(request) == "narrative"


def test_get_roll_dice(fake_container):
    request = FakeRequest(fake_container)

    assert dependencies.get_roll_dice_usecase(request) == "dice"


def test_get_end_session(fake_container):
    request = FakeRequest(fake_container)

    assert dependencies.get_end_session_usecase(request) == "end"


def test_get_event_bus(fake_container):
    request = FakeRequest(fake_container)

    assert dependencies.get_event_bus(request) == "bus"


@pytest.mark.asyncio
async def test_get_health_service(fake_container):
    request = FakeRequest(fake_container)

    service = dependencies.get_health_service(request)

    assert await service.is_ready() is True


def test_get_health_service_fallback():
    request = FakeRequest(container=None)

    service = dependencies.get_health_service(request)

    assert hasattr(service, "is_ready")
