import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from rpg_narrative_server.application.services.llm.llm_service import LLMService


class DummyRequest:
    def __init__(self, prompt="hello", system_prompt="sys", temperature=0.0, max_tokens=100):
        self.prompt = prompt
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens