import os
from dataclasses import dataclass
from typing import Literal

StorageType = Literal["json", "chroma", "memory"]
EmbeddingProfile = Literal["local", "hybrid", "cloud"]


@dataclass(frozen=True)
class ProfileConfig:
    storage: StorageType
    embedding: str
    llm_provider: str


def load_profile() -> ProfileConfig:
    profile = os.getenv("APP_PROFILE", "local")

    if profile == "local":
        return ProfileConfig(
            storage="json",
            embedding="sentence",
            llm_provider="lmstudio",
        )

    if profile == "hybrid":
        return ProfileConfig(
            storage="chroma",
            embedding="sentence",
            llm_provider="openai",
        )

    if profile == "cloud":
        return ProfileConfig(
            storage="chroma",
            embedding="openai",
            llm_provider="openai",
        )

    raise ValueError(f"Invalid APP_PROFILE: {profile}")
