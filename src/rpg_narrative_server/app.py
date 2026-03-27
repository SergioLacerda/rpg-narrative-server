from fastapi import FastAPI

from rpg_narrative_server.interfaces.api.routes.router import api_router
from rpg_narrative_server.bootstrap.lifecycle import lifespan

from rpg_narrative_server.interfaces.api.middleware.request_context_middleware import (
    request_context_middleware,
)
from rpg_narrative_server.shared.logging.config import setup_logging

setup_logging()


def create_app() -> FastAPI:

    app = FastAPI(
        title="RPG Narrative Server",
        lifespan=lifespan,
    )

    app.middleware("http")(request_context_middleware)

    app.include_router(api_router)

    return app


app = create_app()
