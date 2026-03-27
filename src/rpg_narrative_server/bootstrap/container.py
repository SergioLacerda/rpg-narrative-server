import logging
from pathlib import Path

from rpg_narrative_server.config.loader import load_settings

# embeddings
from rpg_narrative_server.infrastructure.embeddings.registry import EmbeddingRegistry
from rpg_narrative_server.infrastructure.embeddings.providers.sentence_embedding_provider import create_sentence_embedding
from rpg_narrative_server.infrastructure.embeddings.providers.openai_embedding_provider import create_openai_embedding
from rpg_narrative_server.infrastructure.embeddings.providers.ollama_embedding_provider import create_ollama_embedding
from rpg_narrative_server.infrastructure.embeddings.providers.lmstudio_embedding_provider import create_lmstudio_embedding
from rpg_narrative_server.infrastructure.embeddings.providers.gemini_embedding_provider import create_gemini_embedding

from rpg_narrative_server.infrastructure.cache.ttl_cache import TTLCache
from rpg_narrative_server.infrastructure.cache.response_cache import ResponseCache
from rpg_narrative_server.infrastructure.cache.response_cache_storage import build_file_storage

# storage
from rpg_narrative_server.infrastructure.storage.vector_store_config import VectorStoreConfig

from rpg_narrative_server.infrastructure.storage.backends.json_backend import JSONStorageBackend
from rpg_narrative_server.infrastructure.storage.backends.chroma_backend import ChromaStorageBackend
from rpg_narrative_server.infrastructure.storage.backends.inmemory_backend import InMemoryStorageBackend


# vector index
from rpg_narrative_server.vector_index.builder import VectorIndexBuilder

# repositories
from rpg_narrative_server.infrastructure.storage.repositories.json_campaign_repository import JSONCampaignRepository

# use cases
from rpg_narrative_server.usecases.narrative_event import NarrativeUseCase
from rpg_narrative_server.usecases.roll_dice import RollDiceUseCase
from rpg_narrative_server.usecases.end_session import EndSessionUseCase

# infra
from rpg_narrative_server.infrastructure.random.python_random_provider import PythonRandomProvider
from rpg_narrative_server.infrastructure.events.blinker_event_bus import BlinkerEventBus

# services
from rpg_narrative_server.application.services.memory_service import MemoryService
from rpg_narrative_server.application.services.health_service import HealthService
from rpg_narrative_server.application.services.llm.llm_service import LLMService
from rpg_narrative_server.application.services.document_resolver import DocumentResolver
from rpg_narrative_server.application.services.intent.llm_intent_classifier import LLMIntentClassifier
from rpg_narrative_server.application.services.intent.intent_classifier import IntentClassifier
from rpg_narrative_server.application.services.intent.language_profiles import PT_BR, EN
# rag
from rpg_narrative_server.domain.rag.context_window import DynamicContextWindow

# executor
from rpg_narrative_server.infrastructure.runtime.executor import Executor, ExecutorType

# retrieval
from rpg_narrative_server.infrastructure.rag.retrieval_engine import RetrievalEngine
from rpg_narrative_server.infrastructure.rag.async_vector_memory_adapter import AsyncVectorMemoryAdapter

from rpg_narrative_server.interfaces.dice.parser_adapter import DiceParserAdapter
from rpg_narrative_server.application.state.campaign_state_store import CampaignStateStore

from rpg_narrative_server.domain.rag.context_builder import ContextBuilder
from rpg_narrative_server.domain.rag.context_formatter import ContextFormatter
from rpg_narrative_server.domain.narrative.session_summarizer import SessionSummarizer

logger = logging.getLogger("rpg_narrative_server.container")


# ==========================================================
# 🔥 SIMPLE CACHE (CORRETO)
# ==========================================================

class SimpleCache:

    def __init__(self):
        self._data = {}

    def get(self, key):
        return self._data.get(key)

    def set(self, key, value):
        self._data[key] = value


# ==========================================================
# CONTAINER
# ==========================================================

class Container:

    def __init__(self):

        logger.info("🚀 Initializing container")

        self.settings = load_settings()

        # registry
        self.embedding_registry = EmbeddingRegistry()
        self._register_embeddings()

        # executor
        self._executor = Executor(mode=ExecutorType.PROCESS)

        # eager
        self._storage = self._build_storage()

        # lazy core
        self._embedding = None
        self._vector_index = None
        self._retrieval_engine = None

        self._campaign_repo = None
        self._memory_service = None
        self._event_bus = None
        self._llm_service = None
        self._health = None

        # 🔥 novos
        self._provider_selector = None
        self._cache = None

        # lazy usecases
        self._narrative = None
        self._end_session = None
        self._roll_dice = None

        self._intent_classifier = None

        self._context_builder = None
        self._context_formatter = None

        logger.info("🔥 Container ready (optimized mode)")

    # ==========================================================
    # REGISTRY
    # ==========================================================

    def _register_embeddings(self):
        self.embedding_registry.register("sentence", create_sentence_embedding)
        self.embedding_registry.register("openai", create_openai_embedding)
        self.embedding_registry.register("ollama", create_ollama_embedding)
        self.embedding_registry.register("lmstudio", create_lmstudio_embedding)
        self.embedding_registry.register("gemini", create_gemini_embedding)

    # ==========================================================
    # STORAGE
    # ==========================================================

    def _build_storage(self):

        storage_type = self.settings.app.storage
        base_path = Path(self.settings.app.campaign_file)

        vector_store_config = VectorStoreConfig(
            max_file_size_kb=self.settings.app.max_file_size_kb,
            max_entries_per_file=self.settings.app.max_entries_per_file,
        )

        if storage_type == "json":
            return JSONStorageBackend(base_path, vector_store_config)

        if storage_type == "chroma":
            return ChromaStorageBackend(base_path)

        if storage_type == "memory":
            return InMemoryStorageBackend()

        raise ValueError(f"Unknown storage: {storage_type}")

    # ==========================================================
    # EMBEDDING
    # ==========================================================

    def _build_embedding(self):

        s = self.settings.embeddings

        logger.info(
            "🔧 embedding provider=%s model=%s",
            s.provider,
            s.model,
        )

        return self.embedding_registry.create(
            s.provider,
            model=s.model,
            api_key=s.api_key,
            base_url=s.base_url,
            batch_size=s.batch_size,
        )

    # ==========================================================
    # LLM PROVIDERS (🔥 MULTI)
    # ==========================================================

    def _build_llm_provider(self):

        s = self.settings.llm
        provider = s.provider.lower()

        if provider == "openai":
            from rpg_narrative_server.infrastructure.llm.openai_provider import OpenAIProvider
            return OpenAIProvider(api_key=s.api_key, model=s.model, base_url=s.base_url)

        elif provider == "lmstudio":
            from rpg_narrative_server.infrastructure.llm.lmstudio_provider import LMStudioProvider
            return LMStudioProvider(base_url=s.base_url, model=s.model)

        elif provider == "ollama":
            from rpg_narrative_server.infrastructure.llm.ollama_provider import OllamaProvider
            return OllamaProvider(model=s.model, base_url=s.base_url)

        elif provider == "gemini":
            from rpg_narrative_server.infrastructure.llm.gemini_provider import GeminiProvider
            return GeminiProvider(api_key=s.api_key, model=s.model)

        elif provider == "groq":
            from rpg_narrative_server.infrastructure.llm.groq_provider import GroqProvider
            return GroqProvider(api_key=s.api_key, model=s.model)

        elif provider == "deepseek":
            from rpg_narrative_server.infrastructure.llm.deepseek_provider import DeepSeekProvider
            return DeepSeekProvider(api_key=s.api_key, model=s.model)

        elif provider == "anthropic":
            from rpg_narrative_server.infrastructure.llm.anthropic_provider import AnthropicProvider
            return AnthropicProvider(api_key=s.api_key, model=s.model)

        else:
            raise ValueError(f"Unknown LLM provider: {provider}")

    # ==========================================================
    # LLM SERVICE
    # ==========================================================

    def _build_llm_service(self):

        provider = self._build_llm_provider()

        return LLMService(
            provider=provider,
            response_cache=self.response_cache,
            ttl_cache=self.ttl_cache,
        )

    # ==========================================================
    # CORE
    # ==========================================================

    @property
    def executor(self):
        return self._executor

    @property
    def storage(self):
        return self._storage

    @property
    def embedding(self):
        if self._embedding is None:
            self._embedding = self._build_embedding()
        return self._embedding

    @property
    def vector_index(self):
        if self._vector_index is None:
            builder = VectorIndexBuilder(
                embedding_service=self.embedding,
                storage_backend=self.storage,
                tokenizer=self.tokenizer,
            )
            self._vector_index = builder.build()
        return self._vector_index

    @property
    def retrieval_engine(self):
        if self._retrieval_engine is None:
            self._retrieval_engine = RetrievalEngine(
                vector_index=self.vector_index,
                embedding_cache=self.embedding,
                semantic_cache={},
                executor=self.executor,
                enable_hedging=True,
            )
        return self._retrieval_engine

    @property
    def campaign_repo(self):
        if self._campaign_repo is None:
            self._campaign_repo = JSONCampaignRepository(
                Path(self.settings.app.campaign_file)
            )
        return self._campaign_repo

    @property
    def event_bus(self):
        if self._event_bus is None:
            self._event_bus = BlinkerEventBus()
        return self._event_bus

    @property
    def cache(self):
        if self._cache is None:
            self._cache = SimpleCache()
        return self._cache

    @property
    def llm(self):
        if self._llm_service is not None:
            return self._llm_service

        self._llm_service = self._build_llm_service()
        return self._llm_service

    @property
    def health(self):
        if self._health is None:
            self._health = HealthService(self)
        return self._health

    # ==========================================================
    # USE CASES
    # ==========================================================

    @property
    def roll_dice(self):
        if self._roll_dice is None:
            self._roll_dice = RollDiceUseCase(
                rng=PythonRandomProvider(),
                parser=DiceParserAdapter(),
            )
        return self._roll_dice

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
    def tokenizer(self):
        if not hasattr(self, "_tokenizer"):
            self._tokenizer = DynamicContextWindow()
        return self._tokenizer


    @property
    def vector_memory(self):
        if not hasattr(self, "_vector_memory"):
            self._vector_memory = AsyncVectorMemoryAdapter(self.vector_index)
        return self._vector_memory


    @property
    def document_resolver(self):
        if not hasattr(self, "_document_resolver"):
            self._document_resolver = DocumentResolver(
                document_store=self.vector_index.components.document_store,
                metadata_store=self.vector_index.components.metadata_store,
            )
        return self._document_resolver

    @property
    def campaign_state(self):
        if not hasattr(self, "_campaign_state_store"):
            from pathlib import Path
            self._campaign_state_store = CampaignStateStore(
                Path("data/campaign_state.json")
            )
        return self._campaign_state_store

    @property
    def intent_classifier(self):
        if self._intent_classifier is None:

            llm_intent = LLMIntentClassifier(lambda: self.llm)

            self._intent_classifier = IntentClassifier(
                profiles=[PT_BR, EN],
                llm_classifier=llm_intent,
            )

        return self._intent_classifier

    @property
    def ttl_cache(self):
        if not hasattr(self, "_ttl_cache"):
            self._ttl_cache = TTLCache(ttl=60)
        return self._ttl_cache

    @property
    def response_cache(self):
        if not hasattr(self, "_response_cache"):

            path = Path("data/memory/response_cache.json")

            loader, saver = build_file_storage(path)

            self._response_cache = ResponseCache(
                loader=loader,
                saver=saver,
            )

        return self._response_cache


    @property
    def memory_service(self):
        if self._memory_service is None:
            self._memory_service = MemoryService(
                repository=self.campaign_repo,
                max_events=10,
                summarizer=SessionSummarizer(),
                llm_service=self.llm,
            )
        return self._memory_service

    @property
    def context_builder(self):
        if self._context_builder is None:
            self._context_builder = ContextBuilder(
                memory_service=self.memory_service
            )
        return self._context_builder

    @property
    def context_formatter(self):
        if self._context_formatter is None:
            self._context_formatter = ContextFormatter()
        return self._context_formatter

# ==========================================================
# SINGLETON
# ==========================================================

_container = None


def get_container() -> "Container":
    global _container

    if _container is None:
        _container = Container()

    return _container