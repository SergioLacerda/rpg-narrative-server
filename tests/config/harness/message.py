from tests.config.helpers.discord_factory import (
    make_ctx,
    DummyExecutor,
    DummyUsecase,
)

from tests.config.fakes.runtime import DummyRuntime
from tests.config.fakes.intent.intent import DummyIntent
from tests.config.fakes.state import DummyCampaignState


class MessageHarness:

    def __init__(
        self,
        *,
        campaign_id="camp1",
        response="ok",
        intent=True,
        cooldown=True,
        locked=False,
    ):
        # ctx adapter
        self.ctx = make_ctx()
        self.ctx.channel_id = self.ctx.channel.id
        self.ctx.user_id = self.ctx.author.id

        self.sent = self.ctx.sent_messages
        self.message_content = "attack"

        # dependencies
        self.usecases = type(
            "Usecases", (), {"narrative": DummyUsecase(result=response)}
        )()

        self.executor = DummyExecutor()
        self.campaign_state = DummyCampaignState(campaign_id)
        self.runtime = DummyRuntime(cooldown=cooldown, locked=locked)
        self.intent = DummyIntent(intent)

        self.settings = None

    def message(self, content: str):
        self.message_content = content
        return self

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
        await service.handle(msg, self.ctx)
