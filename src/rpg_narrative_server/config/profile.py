from dataclasses import dataclass
from typing import Literal
import os


StorageType = Literal["json", "chroma", "memory"]
EmbeddingProfile = Literal["local", "hybrid", "cloud"]


@dataclass(frozen=True)
class ProfileConfig:
    storage: StorageType
    embedding: EmbeddingProfile


def load_profile() -> ProfileConfig:
    profile = os.getenv("APP_PROFILE", "local")

    if profile == "local":
        return ProfileConfig(
            storage="json",
            embedding="local",
        )

    if profile == "hybrid":
        return ProfileConfig(
            storage="chroma",
            embedding="local",
        )

    if profile == "cloud":
        return ProfileConfig(
            storage="chroma",
            embedding="cloud",
        )

    raise ValueError(f"Invalid APP_PROFILE: {profile}")
