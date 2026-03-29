from rpg_narrative_server.application.contracts.response import Response
from tests.config.factories.context import make_context
from tests.config.fakes.intent.intent import DummyIntent
from tests.config.fakes.runtime import DummyRuntime
from tests.config.fakes.state import DummyCampaignState
from tests.config.helpers.discord_factory import (
    DummyExecutor,
    DummyUsecase,
)


class MessageHarness:
    def __init__(
        self,
        *,
        campaign_id="camp1",
        response="ok",
        intent="ACTION",
        cooldown=True,
        locked=False,
    ):
        # ---------------------------------------
        # CONTEXT
        # ---------------------------------------
        self.ctx = make_context(guild_id=None, user_id="999")
        self.sent = self.ctx.sent_messages
        self.message_content = "attack"

        # ---------------------------------------
        # STATE
        # ---------------------------------------
        self.campaign_id = campaign_id
        self.campaign_state = DummyCampaignState()

        if self.campaign_id:
            self.campaign_state.set(
                self.ctx.channel.id,
                self.campaign_id,
            )

        # ---------------------------------------
        # RESPONSE
        # ---------------------------------------
        response_obj = Response(
            text=response or "",
            type="narrative",
            metadata={},
        )

        # ---------------------------------------
        # DEPENDENCIES
        # ---------------------------------------
        self.usecases = type(
            "Usecases",
            (),
            {
                "narrative": DummyUsecase(result=response_obj),
            },
        )()

        self.executor = DummyExecutor()
        self.runtime = DummyRuntime(cooldown=cooldown, locked=locked)
        self.intent = DummyIntent(intent)

        # settings mínimo
        self.settings = type("Settings", (), {})()

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    def message(self, content: str):
        self.message_content = content
        return self

    # ---------------------------------------------------------
    # BUILD
    # ---------------------------------------------------------

    def build(self):
        from rpg_narrative_server.application.services.message_service import (
            MessageService,
        )

        return MessageService(
            usecases=self.usecases,
            executor=self.executor,
            campaign_state=self.campaign_state,
            runtime=self.runtime,
            intent_classifier=self.intent,
            settings=self.settings,
        )

    # ---------------------------------------------------------
    # EXECUTE
    # ---------------------------------------------------------

    async def run(self):
        msg = type(
            "Msg",
            (),
            {
                "content": self.message_content,
                "author": type("Author", (), {"bot": False}),
            },
        )()

        service = self.build()

        # 🔥 responder = ctx (como seus testes usam)
        await service.handle(msg, self.ctx, self.ctx)

        return self.sent
