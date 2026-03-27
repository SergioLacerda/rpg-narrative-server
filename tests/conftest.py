# ---------------------------------------------------------
# PATH
# ---------------------------------------------------------
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


# ---------------------------------------------------------
# ENV
# ---------------------------------------------------------
import os

os.environ["ENVIRONMENT"] = "test"
os.environ["DEVICE"] = "cpu"
os.environ["LLM_PROVIDER"] = "openai"
os.environ["EMBEDDING_PROVIDER"] = "sentence"


# ---------------------------------------------------------
# SETTINGS CACHE
# ---------------------------------------------------------
from rpg_narrative_server.config.loader import load_settings

load_settings.cache_clear()


# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------
import pytest

from fastapi.testclient import TestClient

from tests.config.factories.container_factory import create_test_container
from tests.config.fixtures.no_network import no_network

from rpg_narrative_server.infrastructure.runtime.campaign_context import CampaignContext
from rpg_narrative_server.interfaces.api.dependencies import (
    get_container,
    get_narrative_usecase,
    get_roll_dice_usecase,
)


# ---------------------------------------------------------
# RESET GLOBAL STATE (🔥 ÚNICO)
# ---------------------------------------------------------
@pytest.fixture(autouse=True)
def reset_global_state():

    # reset container singleton
    import importlib
    c = importlib.import_module("rpg_narrative_server.bootstrap.container")
    c._container = None


# ---------------------------------------------------------
# CONTAINER
# ---------------------------------------------------------
@pytest.fixture
def container():
    return create_test_container()


@pytest.fixture
def container_factory():
    def _factory(**overrides):
        container = create_test_container()

        if "llm" in overrides:
            container._llm_service = overrides["llm"]

        if "embedding" in overrides:
            container._embedding = overrides["embedding"]

        if "vector_index" in overrides:
            container._vector_index = overrides["vector_index"]

        return container

    return _factory


# ---------------------------------------------------------
# FASTAPI APP (🔥 ÚNICA)
# ---------------------------------------------------------
@pytest.fixture
def app(container):

    from rpg_narrative_server.app import create_app

    app = create_app()

    # container override
    app.dependency_overrides[get_container] = lambda: container

    # 🔥 overrides DIRETOS (ESSENCIAL)
    app.dependency_overrides[get_narrative_usecase] = lambda: container.narrative
    app.dependency_overrides[get_roll_dice_usecase] = lambda: container.roll_dice

    return app


# ---------------------------------------------------------
# CLIENT HTTP
# ---------------------------------------------------------
@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_campaign_context():

    ctx = CampaignContext()
    ctx.reset()

def pytest_addoption(parser):
    parser.addoption(
        "--update-golden",
        action="store_true",
        default=False,
        help="Update golden snapshot files"
    )

@pytest.fixture
def update_golden(request):
    return request.config.getoption("--update-golden")