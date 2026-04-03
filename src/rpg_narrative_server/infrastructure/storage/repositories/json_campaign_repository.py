import asyncio
import json
from pathlib import Path

from rpg_narrative_server.application.ports.campaign_repository import (
    CampaignRepositoryPort,
)


class JSONCampaignRepository(CampaignRepositoryPort):
    def __init__(self, base_path: Path):
        self.base_dir = base_path / "campaigns"

    # ---------------------------------------------------------
    # helpers
    # ---------------------------------------------------------

    def _events_path(self, campaign_id: str):
        return self.base_dir / str(campaign_id) / "events.json"

    def _sessions_path(self, campaign_id: str):
        return self.base_dir / str(campaign_id) / "sessions.json"

    def _ensure_dir(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # IO
    # ---------------------------------------------------------

    async def load(self, path: Path):
        if not path.exists():
            return []

        def _read():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                return []

        return await asyncio.to_thread(_read)

    async def save(self, path: Path, data):
        self._ensure_dir(path)

        def _write():
            path.write_text(json.dumps(data, indent=2))

        await asyncio.to_thread(_write)

    # ---------------------------------------------------------
    # PORT
    # ---------------------------------------------------------

    async def get_events(self, campaign_id: str) -> list:
        return await self.load(self._events_path(campaign_id))

    async def save_events(self, campaign_id: str, events: list):
        await self.save(self._events_path(campaign_id), events)

    async def get_sessions(self, campaign_id: str) -> list:
        return await self.load(self._sessions_path(campaign_id))

    async def save_sessions(self, campaign_id: str, sessions: list):
        await self.save(self._sessions_path(campaign_id), sessions)

    def _campaign_dir(self, campaign_id: str) -> Path:
        return self.base_dir / str(campaign_id)

    async def create(self, campaign_id: str) -> None:
        path = self._campaign_dir(campaign_id)

        def _create():
            path.mkdir(parents=True, exist_ok=True)

        await asyncio.to_thread(_create)

    async def list(self) -> list[str]:
        if not self.base_dir.exists():
            return []

        def _list():
            return [p.name for p in self.base_dir.iterdir() if p.is_dir()]

        return await asyncio.to_thread(_list)

    async def delete(self, campaign_id: str) -> None:
        import shutil

        path = self._campaign_dir(campaign_id)

        if not path.exists():
            return

        def _delete():
            shutil.rmtree(path)

        await asyncio.to_thread(_delete)

    async def exists(self, campaign_id: str) -> bool:
        path = self._campaign_dir(campaign_id)
        return path.exists()
