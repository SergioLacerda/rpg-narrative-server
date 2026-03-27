import asyncio


class HealthService:
    def __init__(self, container):
        self.container = container

    # ---------------------------------------------------------
    # liveness (rápido, sem dependências)
    # ---------------------------------------------------------

    def is_alive(self) -> bool:
        return True

    # ---------------------------------------------------------
    # readiness (depende de infra)
    # ---------------------------------------------------------

    async def is_ready(self) -> bool:
        try:
            vector_index = self.container.vector_index

            # se tiver método async/sync, trata ambos
            if hasattr(vector_index, "ensure_ann_ready"):
                maybe = vector_index.ensure_ann_ready()
                if asyncio.iscoroutine(maybe):
                    await maybe

            return True

        except Exception:
            return False

    # ---------------------------------------------------------
    # status completo (opcional)
    # ---------------------------------------------------------

    async def status(self) -> dict:
        ready = await self.is_ready()

        return {
            "status": "ready" if ready else "loading",
            "components": {
                "vector_index": "ok" if ready else "loading",
                "embedding": type(self.container.embedding).__name__,
                "storage": type(self.container.storage).__name__,
            },
        }
