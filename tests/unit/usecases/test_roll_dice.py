import pytest

from rpg_narrative_server.application.contracts.response import Response
from rpg_narrative_server.domain.dice.ast.nodes import RollNode
from rpg_narrative_server.domain.dice.value_objects import DiceExpression


@pytest.fixture
def usecase(container):
    return container.roll_dice


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------


def data(response: Response) -> dict:
    return response.metadata or {}


# ---------------------------------------------------------
# UNIT / BASIC
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_roll_dice_invalid(usecase):
    result = await usecase.execute("invalid")

    assert result.type == "error"
    assert data(result)["error"] == "Invalid dice expression"


@pytest.mark.asyncio
async def test_roll_dice_usecase(usecase):
    result = await usecase.execute(DiceExpression(2, 6, 1))

    d = data(result)

    assert isinstance(d["total"], int)
    assert "rolls" in d


# ---------------------------------------------------------
# FLOW
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_roll_dice_with_expression(usecase):
    result = await usecase.execute(DiceExpression(2, 6))

    assert data(result)["total"] > 0


@pytest.mark.asyncio
async def test_roll_dice_with_analysis(usecase):
    usecase.enable_analysis = True

    result = await usecase.execute(DiceExpression(1, 6))

    assert "distribution" in data(result)


@pytest.mark.asyncio
async def test_roll_dice_analysis_failure(usecase, monkeypatch):
    monkeypatch.setattr(
        "rpg_narrative_server.usecases.roll_dice.analyze_distribution",
        lambda ast: (_ for _ in ()).throw(Exception()),
    )

    usecase.enable_analysis = True

    result = await usecase.execute(DiceExpression(1, 6))

    assert data(result)["distribution"] is None


@pytest.mark.asyncio
async def test_roll_dice_parser_path(container):
    class FakeParser:
        def parse(self, expr):
            return RollNode(1, 6)

    container.roll_dice.parser = FakeParser()

    result = await container.roll_dice.execute("1d6")

    assert data(result)["total"] > 0
