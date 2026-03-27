from typing import Optional


class MessageContext:
    """
    Adapter para compatibilizar discord.Message com o padrão de ctx usado nos commands.

    Objetivo:
    - Permitir reutilizar executor + responder
    - Evitar acoplamento do application layer com discord.Message
    """

    def __init__(self, message):
        self.message = message

        # compatibilidade com ctx padrão
        self.channel = message.channel
        self.author = message.author
        self.guild = getattr(message, "guild", None)

        # usado pelo responder (mantém compatibilidade)
        self.interaction: Optional[None] = None

    # -------------------------------------------------
    # API compatível com ctx.send()
    # -------------------------------------------------
    async def send(self, content: str):
        await self.channel.send(content)

    # -------------------------------------------------
    # Utilidades (opcional, mas útil)
    # -------------------------------------------------
    @property
    def channel_id(self) -> str:
        return str(self.channel.id)

    @property
    def user_id(self) -> str:
        return str(self.author.id)

    @property
    def guild_id(self) -> Optional[str]:
        if self.guild and getattr(self.guild, "id", None):
            return str(self.guild.id)
        return None

    def __repr__(self) -> str:
        return f"<MessageContext channel={self.channel_id} user={self.user_id}>"
