import pytest
import os
import sys
from pathlib import Path
import importlib
from fastapi.testclient import TestClient

from rpg_narrative_server.app import create_app

from tests.config.factories.container_factory import create_test_container
from rpg_narrative_server.config.loader import load_settings
from rpg_narrative_server.infrastructure.runtime.campaign_context import CampaignContext

from rpg_narrative_server.interfaces.api.dependencies import (
    get_container,
    get_narrative_usecase,
    get_roll_dice_usecase,
)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


# ---------------------------------------------------------
# ENV
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
# RESET GLOBAL STATE (🔥 ÚNICO)
# ---------------------------------------------------------
@pytest.fixture(autouse=True)
def reset_global_state():
    # reset container singleton

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
        help="Update golden snapshot files",
    )


@pytest.fixture
def update_golden(request):
    return request.config.getoption("--update-golden")
