from pydantic import BaseModel, Field


class NarrativeEventRequest(BaseModel):
    action: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Ação do jogador no RPG",
        examples=["Ataco o goblin com minha espada"],
    )

    user_id: str = Field(
        ...,
        description="Identificador do jogador",
        examples=["user_123"],
    )
