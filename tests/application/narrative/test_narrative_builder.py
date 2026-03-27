import pytest

from rpg_narrative_server.domain.narrative.narrative_builder import NarrativeBuilder


def build_prompt(builder, ctx, action):
    system = builder.build_system_prompt(ctx.get("scene_type"))
    user = builder.build_user_prompt(ctx=ctx, action=action)
    return f"{system}\n\n{user}"


# ---------------------------------------------------------
# PROMPT
# ---------------------------------------------------------


def test_prompt_structure():

    builder = NarrativeBuilder()

    ctx = {
        "summary": "",
        "recent_events": ["contexto teste"],
        "retrieved": "",
        "related_entities": [],
        "scene_type": "DEFAULT",
    }

    prompt = build_prompt(builder, ctx=ctx, action="abrir porta")

    assert "Você é um mestre de RPG" in prompt
    assert "Eventos recentes:" in prompt
    assert "contexto teste" in prompt
    assert "Ação do jogador:" in prompt
    assert "abrir porta" in prompt
    assert "Continue a narrativa" in prompt


def test_prompt_without_context():

    builder = NarrativeBuilder()

    ctx = {
        "summary": "",
        "recent_events": [],
        "retrieved": "",
        "related_entities": [],
        "scene_type": "DEFAULT",
    }

    prompt = build_prompt(builder, ctx=ctx, action="andar")

    assert "Ação do jogador:" in prompt
    assert "andar" in prompt


def test_system_prompt():

    builder = NarrativeBuilder()

    system = builder.build_system_prompt()

    assert "Você é um mestre de RPG" in system
    assert 'Nunca diga "OOC"' in system


def test_user_prompt():

    builder = NarrativeBuilder()

    ctx = {
        "summary": "",
        "recent_events": ["x"],
        "retrieved": "",
        "related_entities": [],
        "scene_type": "DEFAULT",
    }

    user = builder.build_user_prompt(
        ctx=ctx,
        action="y",
    )

    assert "Eventos recentes:" in user
    assert "x" in user
    assert "Ação do jogador:" in user
    assert "y" in user


# ---------------------------------------------------------
# UTILIDADES
# ---------------------------------------------------------


def test_normalize_action():

    builder = NarrativeBuilder()

    result = builder.normalize_action(" atacar\ninimigo ")

    assert result == "atacar inimigo"


def test_enforce_length():

    builder = NarrativeBuilder()

    text = "a" * 5000

    result = builder.enforce_length(text, max_chars=100)

    assert len(result) == 100


def test_sanitize_output():

    builder = NarrativeBuilder()

    text = "\n linha1 \n\n linha2 \n"

    result = builder.sanitize_output(text)

    assert result == "linha1\nlinha2"


def test_sanitize_output_none():

    builder = NarrativeBuilder()

    with pytest.raises(ValueError):
        builder.sanitize_output(None)
