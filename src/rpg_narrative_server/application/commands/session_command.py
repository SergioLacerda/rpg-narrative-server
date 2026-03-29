from typing import Any


class SessionCommand:
    name = "endsession"

    def __init__(self, end_session_usecase, campaign_state):
        self.end_session = end_session_usecase
        self.campaign_state = campaign_state

    async def execute(self, ctx: Any):
        campaign_id = self.campaign_state.get(ctx.channel.id)

        if not campaign_id:
            return "⚠️ Nenhuma campanha ativa."

        result = await self.end_session.execute(campaign_id=campaign_id)

        self.campaign_state.clear(ctx.channel.id)

        if result is None:
            return "⚠️ Nenhum resumo gerado."

        return f"🛑 Sessão encerrada.\n\n{result}"


def build_session_command(deps):
    return SessionCommand(deps.end_session, deps.campaign_state)
