from dataclasses import dataclass
import os


@dataclass
class ProfileConfig:
    storage: str
    embedding: str


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
            embedding="openai",
        )

    raise ValueError(f"Invalid APP_PROFILE: {profile}")