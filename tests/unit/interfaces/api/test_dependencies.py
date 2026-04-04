from types import SimpleNamespace

import pytest

from rpg_narrative_server.interfaces.api.dependencies import get_health_service


@pytest.mark.asyncio
async def test_get_health_service_without_container():
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace()))

    service = get_health_service(request)

    result = await service.is_ready()

    assert result is True


@pytest.mark.asyncio
async def test_get_health_service_without_health_attr():
    container = SimpleNamespace()

    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(container=container)))

    service = get_health_service(request)

    result = await service.is_ready()

    assert result is True
