import pytest

from tests.config.helpers.discord_factory import make_ctx

from rpg_narrative_server.frameworks.discord.utils import (
    get_campaign_id,
    get_user_id,
    send_long_response,
    MAX_MESSAGE_LEN,
)


# ----------------------------------------
# get_campaign_id
# ----------------------------------------


def test_campaign_id_from_guild():
    ctx = make_ctx()
    ctx.guild.id = "123"

    result = get_campaign_id(ctx)

    assert result == "123"


def test_campaign_id_dm():
    ctx = make_ctx()
    ctx.guild = None
    ctx.author.id = "999"

    result = get_campaign_id(ctx)

    assert result == "dm_999"


# ----------------------------------------
# get_user_id
# ----------------------------------------


def test_get_user_id():
    ctx = make_ctx()
    ctx.author.id = "abc"

    assert get_user_id(ctx) == "abc"


# ----------------------------------------
# send_long_response
# ----------------------------------------


@pytest.mark.asyncio
async def test_send_long_response_short():
    ctx = make_ctx()

    await send_long_response(ctx, "hello")

    assert ctx.sent_messages[0] == "hello"


@pytest.mark.asyncio
async def test_send_long_response_long():
    ctx = make_ctx()

    long_text = "a" * 5000

    await send_long_response(ctx, long_text)

    # deve dividir em múltiplas mensagens
    assert len(ctx.sent_messages) > 1


@pytest.mark.asyncio
async def test_send_long_response_with_interaction():
    ctx = make_ctx(interaction=True)

    await send_long_response(ctx, "hello")

    assert ctx.sent_messages[0] == "hello"


@pytest.mark.asyncio
async def test_send_long_response_long_interaction():
    ctx = make_ctx(interaction=True)

    long_text = "a" * 5000

    await send_long_response(ctx, long_text)

    # múltiplas mensagens
    assert len(ctx.sent_messages) > 1


@pytest.mark.asyncio
async def test_send_long_response_empty():
    ctx = make_ctx()

    await send_long_response(ctx, "")

    assert "Sem conteúdo" in ctx.sent_messages[0]


@pytest.mark.asyncio
async def test_send_long_response_with_header_short():
    ctx = make_ctx()

    header = "HEADER: "
    content = "hello"

    await send_long_response(ctx, content, header=header)

    assert ctx.sent_messages[0] == "HEADER: hello"


@pytest.mark.asyncio
async def test_send_long_response_with_header_long():
    ctx = make_ctx()

    header = "HEADER: "
    content = "a" * 5000

    await send_long_response(ctx, content, header=header)

    # primeiro envia header separado
    assert ctx.sent_messages[0] == header

    # depois envia chunks
    assert len(ctx.sent_messages) > 1


@pytest.mark.asyncio
async def test_chunk_size_respected():
    ctx = make_ctx()

    content = "a" * (MAX_MESSAGE_LEN + 10)

    await send_long_response(ctx, content)

    assert len(ctx.sent_messages) == 2
    assert len(ctx.sent_messages[0]) == MAX_MESSAGE_LEN
