from rpg_narrative_server.application.commands.command_bus import CommandBus
from rpg_narrative_server.application.commands.command_registry import CommandRegistry
from rpg_narrative_server.frameworks.discord.bot import create_bot
from tests.config.factories.deps import make_deps
from tests.config.helpers.discord_factory import DummyExecutor, DummySettings


def make_bot(with_bus: bool = True):
    # -------------------------------------------------
    # BOT BASE (SEM COMMANDS)
    # -------------------------------------------------
    bot = create_bot(
        settings=DummySettings(),
        deps=make_deps(),
        register_commands=False,
    )

    # -------------------------------------------------
    # TEST HARNESS
    # -------------------------------------------------
    registry = CommandRegistry()
    executor = DummyExecutor()

    bus = CommandBus(registry, executor)

    async def _command(ctx, command_name=None, **kwargs):
        return await bus.dispatch(ctx, command_name=command_name, **kwargs)

    bot._command = _command
    bot._registry = registry
    bot._bus = bus

    return bot


def make_executor():
    from tests.config.helpers.discord_factory import DummyExecutor

    return DummyExecutor()
