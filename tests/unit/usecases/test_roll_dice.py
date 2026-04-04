import pytest

from rpg_narrative_server.application.contracts.response import Response
from rpg_narrative_server.domain.dice.ast.nodes import RollNode
from rpg_narrative_server.domain.dice.value_objects import DiceExpression
from rpg_narrative_server.usecases.roll_dice import RollDiceUseCase

# ==========================================================
# MOCKS
# ==========================================================


class MockParser:
    def __init__(self, result=None, error=False):
        self.result = result
        self.error = error

    def parse(self, expression):
        if self.error:
            raise ValueError("parse error")
        return self.result


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------


@pytest.fixture
def usecase(container):
    return container.roll_dice


def data(response: Response) -> dict:
    return response.metadata or {}


class FakeAST:
    def evaluate(self):
        return 42


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


@pytest.mark.asyncio
async def test_invalid_expression_returns_error():
    parser = MockParser(result=None)

    usecase = RollDiceUseCase(rng=None, parser=parser)

    result = await usecase.execute("invalid")

    assert result.type == "error"
    assert "Invalid dice expression" in result.text


@pytest.mark.asyncio
async def test_invalid_type_returns_error():
    parser = MockParser()

    usecase = RollDiceUseCase(rng=None, parser=parser)

    result = await usecase.execute(123)

    assert result.type == "error"


@pytest.mark.asyncio
async def test_parse_exception():
    parser = MockParser(error=True)

    usecase = RollDiceUseCase(rng=None, parser=parser)

    result = await usecase.execute("2d6")

    assert result.type == "error"


@pytest.mark.asyncio
async def test_roll_exception(monkeypatch):
    parser = MockParser(result=FakeAST())

    usecase = RollDiceUseCase(rng=None, parser=parser)

    def fake_roll(ast, rng):
        raise Exception("boom")

    monkeypatch.setattr(
        "rpg_narrative_server.usecases.roll_dice.roll",
        fake_roll,
    )

    result = await usecase.execute("2d6")

    assert result.type == "error"
    assert "Roll execution failed" in result.text


@pytest.mark.asyncio
async def test_expression_with_evaluate_method(monkeypatch):
    class CustomExpression:
        def evaluate(self):
            return 42

    class MockParser:
        def parse(self, expression):
            return None

    usecase = RollDiceUseCase(
        rng=None,
        parser=MockParser(),
    )

    def fake_roll(ast, rng):
        return [1, 2, 3], 6

    monkeypatch.setattr(
        "rpg_narrative_server.usecases.roll_dice.roll",
        fake_roll,
    )

    result = await usecase.execute(CustomExpression())

    assert result.type == "dice"
    assert result.metadata is not None
    assert result.metadata["total"] == 6
