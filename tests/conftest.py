import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from rpg_narrative_server.app import create_app
from rpg_narrative_server.config.loader import load_settings
from rpg_narrative_server.infrastructure.runtime.campaign_context import CampaignContext
from rpg_narrative_server.interfaces.api.dependencies import (
    get_container,
    get_narrative_usecase,
    get_roll_dice_usecase,
)
from tests.config.builders.test_container_builder import TestContainerBuilder


@pytest.fixture
def container():
    return TestContainerBuilder().build()


@pytest.fixture
def container_factory():
    def _factory(**overrides):
        builder = TestContainerBuilder()

        if "llm" in overrides:
            builder = builder.with_llm(overrides["llm"])

        if "embedding" in overrides:
            builder = builder.with_embedding(overrides["embedding"])

        if "vector_index" in overrides:
            builder = builder.with_vector_index(overrides["vector_index"])

        return builder.build()

    return _factory


# ---------------------------------------------------------
# PATH (ideal mover para pytest.ini futuramente)
# ---------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


# ---------------------------------------------------------
# ENV (test profile)
# ---------------------------------------------------------
os.environ["ENVIRONMENT"] = "test"
os.environ["DEVICE"] = "cpu"
os.environ["LLM_PROVIDER"] = "openai"
os.environ["EMBEDDING_PROVIDER"] = "sentence"


# ---------------------------------------------------------
# SETTINGS CACHE
# ---------------------------------------------------------
load_settings.cache_clear()


# ---------------------------------------------------------
# FASTAPI APP
# ---------------------------------------------------------
@pytest.fixture
def app(container):
    app = create_app()

    app.dependency_overrides[get_container] = lambda: container
    app.dependency_overrides[get_narrative_usecase] = lambda: container.narrative
    app.dependency_overrides[get_roll_dice_usecase] = lambda: container.roll_dice

    return app


# ---------------------------------------------------------
# CLIENT HTTP
# ---------------------------------------------------------
@pytest.fixture
def client(app):
    return TestClient(app)


# ---------------------------------------------------------
# RESET CONTEXTO GLOBAL
# ---------------------------------------------------------
@pytest.fixture(autouse=True)
def reset_campaign_context():
    ctx = CampaignContext()
    ctx.reset()
    yield


# ---------------------------------------------------------
# GOLDEN FILES
# ---------------------------------------------------------
def pytest_addoption(parser):
    parser.addoption(
        "--update-golden",
        action="store_true",
        default=False,
        help="Update golden snapshot files",
    )


@pytest.fixture
def update_golden(request):
    return request.config.getoption("--update-golden")
