from rpg_narrative_server.infrastructure.storage.backends.json_backend import (
    JSONStorageBackend,
)
from rpg_narrative_server.infrastructure.storage.backends.chroma_backend import (
    ChromaStorageBackend,
)


def build_campaign_storage(settings, campaign_context):

    base_path = campaign_context.base_path

    if settings.app.storage == "json":
        return JSONStorageBackend(base_path, settings)

    if settings.app.storage == "chroma":
        return ChromaStorageBackend(base_path)

    raise ValueError(f"Unsupported storage: {settings.app.storage}")
