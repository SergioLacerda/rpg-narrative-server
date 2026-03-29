import logging
from pathlib import Path

from rpg_narrative_server.application.services.document_resolver import DocumentResolver
from rpg_narrative_server.application.services.health_service import HealthService
from rpg_narrative_server.application.services.intent.intent_classifier import IntentClassifier
from rpg_narrative_server.application.services.intent.language_profiles import EN, PT_BR
from rpg_narrative_server.application.services.intent.llm_intent_classifier import (
    LLMIntentClassifier,
)
from rpg_narrative_server.application.services.llm.llm_service import LLMService
from rpg_narrative_server.application.services.memory_service import MemoryService
from rpg_narrative_server.application.state.campaign_state import CampaignState
from rpg_narrative_server.config.loader import load_settings
from rpg_narrative_server.domain.narrative.session_summarizer import SessionSummarizer
from rpg_narrative_server.domain.rag.context_builder import ContextBuilder
from rpg_narrative_server.domain.rag.context_window import DynamicContextWindow
from rpg_narrative_server.infrastructure.cache.response_cache import ResponseCache
from rpg_narrative_server.infrastructure.cache.response_cache_storage import build_file_storage
from rpg_narrative_server.infrastructure.cache.ttl_cache import TTLCache
from rpg_narrative_server.infrastructure.embeddings.factory import create_embedding
from rpg_narrative_server.infrastructure.events.blinker_event_bus import BlinkerEventBus
from rpg_narrative_server.infrastructure.llm.factory import create_llm_provider
from rpg_narrative_server.infrastructure.rag.async_vector_memory_adapter import (
    AsyncVectorMemoryAdapter,
)
from rpg_narrative_server.infrastructure.random.python_random_provider import PythonRandomProvider
from rpg_narrative_server.infrastructure.runtime.executor import Executor, ExecutorType
from rpg_narrative_server.infrastructure.storage.repositories.json_campaign_repository import (
    JSONCampaignRepository,
)
from rpg_narrative_server.infrastructure.storage.vector_store_config import VectorStoreConfig
from rpg_narrative_server.interfaces.dice.parser_adapter import DiceParserAdapter
from rpg_narrative_server.usecases.end_session import EndSessionUseCase
from rpg_narrative_server.usecases.narrative_event import NarrativeUseCase
from rpg_narrative_server.usecases.roll_dice import RollDiceUseCase
from rpg_narrative_server.vector_index.builder import VectorIndexBuilder

logger = logging.getLogger("rpg_narrative_server.container")


class Container:
    def __init__(self):
        logger.info("🚀 Initializing container")

        self.settings = load_settings()

        # infra base
        self._executor = Executor(mode=ExecutorType.PROCESS)
        self._storage = self._build_storage()

        # lazy core
        self._embedding = None
        self._vector_index = None
        self._llm_service = None

        # infra lazy
        self._campaign_repo = None
        self._campaign_state = None
        self._memory_service = None
        self._event_bus = None
        self._health = None

        # caches
        self._ttl_cache = None
        self._response_cache = None

        # use cases
        self._narrative = None
        self._end_session = None
        self._roll_dice = None

        # support
        self._tokenizer = None
        self._vector_memory = None
        self._document_resolver = None
        self._context_builder = None
        self._intent_classifier = None

    # ==========================================================
    # STORAGE
    # ==========================================================
    def _build_storage(self):
        storage_type = self.settings.storage
        base_path = Path(self.settings.campaign_file)

        config = VectorStoreConfig(
            max_file_size_kb=self.settings.max_file_size_kb,
            max_entries_per_file=self.settings.max_entries_per_file,
        )

        if storage_type == "json":
            from rpg_narrative_server.infrastructure.storage.backends.json_backend import (
                JSONStorageBackend,
            )

            return JSONStorageBackend(base_path, config)

        if storage_type == "memory":
            from rpg_narrative_server.infrastructure.storage.backends.inmemory_backend import (
                InMemoryStorageBackend,
            )

            return InMemoryStorageBackend()

        raise ValueError(f"Unknown storage backend: {storage_type}")

    # ==========================================================
    # CORE
    # ==========================================================
    @property
    def embedding(self):
        if self._embedding is None:
            self._embedding = create_embedding(self.settings)
        return self._embedding

    @property
    def vector_index(self):
        if self._vector_index is None:
            self._vector_index = VectorIndexBuilder(
                embedding_service=self.embedding,
                storage_backend=self._storage,
                tokenizer=self.tokenizer,
            ).build()
        return self._vector_index

    @property
    def llm(self):
        if self._llm_service is None:
            provider = create_llm_provider(self.settings)
            self._llm_service = LLMService(
                provider=provider,
                response_cache=self.response_cache,
                ttl_cache=self.ttl_cache,
            )
        return self._llm_service

    # ==========================================================
    # CACHES
    # ==========================================================
    @property
    def ttl_cache(self):
        if self._ttl_cache is None:
            self._ttl_cache = TTLCache(ttl=60)
        return self._ttl_cache

    @property
    def response_cache(self):
        if self._response_cache is None:
            path = Path("data/memory/response_cache.json")
            loader, saver = build_file_storage(path)
            self._response_cache = ResponseCache(loader=loader, saver=saver)
        return self._response_cache

    # ==========================================================
    # INFRA
    # ==========================================================
    @property
    def campaign_repo(self):
        if self._campaign_repo is None:
            self._campaign_repo = JSONCampaignRepository(Path(self.settings.campaign_file))
        return self._campaign_repo

    @property
    def event_bus(self):
        if self._event_bus is None:
            self._event_bus = BlinkerEventBus()
        return self._event_bus

    @property
    def memory_service(self):
        if self._memory_service is None:
            self._memory_service = MemoryService(
                repository=self.campaign_repo,
                summarizer=SessionSummarizer(),
                llm_service=self.llm,
                max_events=10,
            )
        return self._memory_service

    @property
    def health(self):
        if self._health is None:
            self._health = HealthService(self)
        return self._health

    # ==========================================================
    # SUPPORT
    # ==========================================================
    @property
    def tokenizer(self):
        if self._tokenizer is None:
            self._tokenizer = DynamicContextWindow()
        return self._tokenizer

    @property
    def vector_memory(self):
        if self._vector_memory is None:
            self._vector_memory = AsyncVectorMemoryAdapter(self.vector_index)
        return self._vector_memory

    @property
    def document_resolver(self):
        if self._document_resolver is None:
            self._document_resolver = DocumentResolver(
                document_store=self.vector_index.components.document_store,
                metadata_store=self.vector_index.components.metadata_store,
            )
        return self._document_resolver

    @property
    def context_builder(self):
        if self._context_builder is None:
            self._context_builder = ContextBuilder(memory_service=self.memory_service)
        return self._context_builder

    @property
    def intent_classifier(self):
        if self._intent_classifier is None:
            llm_intent = LLMIntentClassifier(lambda: self.llm)
            self._intent_classifier = IntentClassifier(
                profiles=[PT_BR, EN],
                llm_classifier=llm_intent,
            )
        return self._intent_classifier

    # ==========================================================
    # USE CASES
    # ==========================================================
    @property
    def narrative(self):
        if self._narrative is None:
            self._narrative = NarrativeUseCase(
                repo=self.campaign_repo,
                llm=self.llm,
                vector_index=self.vector_index,
                event_bus=self.event_bus,
                memory_service=self.memory_service,
                vector_memory=self.vector_memory,
                document_resolver=self.document_resolver,
                context_builder=self.context_builder,
            )
        return self._narrative

    @property
    def end_session(self):
        if self._end_session is None:
            self._end_session = EndSessionUseCase(
                memory_service=self.memory_service,
                llm=self.llm,
                vector_memory=self.vector_memory,
            )
        return self._end_session

    @property
    def roll_dice(self):
        if self._roll_dice is None:
            self._roll_dice = RollDiceUseCase(
                rng=PythonRandomProvider(),
                parser=DiceParserAdapter(),
            )
        return self._roll_dice

    @property
    def campaign_state(self) -> CampaignState:
        if self._campaign_state is None:
            self._campaign_state = CampaignState()
        return self._campaign_state
