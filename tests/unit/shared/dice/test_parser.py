import pytest

from rpg_narrative_server.shared.dice.parser import DiceParser
from rpg_narrative_server.domain.dice.ast.nodes import (
    RollNode,
    ExplodeNode,
    KeepHighestNode,
    DropLowestNode,
    RerollNode,
)


@pytest.fixture
def parser():
    return DiceParser()


# --------------------------------------------------
# BASIC
# --------------------------------------------------

def test_parse_basic(parser):

    node = parser.parse("2d6")

    assert isinstance(node, RollNode)
    assert node.quantity == 2
    assert node.sides == 6


# --------------------------------------------------
# EXPLODE
# --------------------------------------------------

def test_parse_explode(parser):

    node = parser.parse("2d6!")

    assert isinstance(node, ExplodeNode)
    assert isinstance(node.child, RollNode)


# --------------------------------------------------
# KEEP HIGHEST
# --------------------------------------------------

def test_parse_keep_highest(parser):

    node = parser.parse("4d6kh3")

    assert isinstance(node, KeepHighestNode)
    assert node.k == 3
    assert isinstance(node.child, RollNode)


# --------------------------------------------------
# DROP LOWEST
# --------------------------------------------------

def test_parse_drop_lowest(parser):

    node = parser.parse("4d6dl1")

    assert isinstance(node, DropLowestNode)
    assert node.k == 1
    assert isinstance(node.child, RollNode)


# --------------------------------------------------
# REROLL
# --------------------------------------------------

def test_parse_reroll(parser):

    node = parser.parse("2d6r<3")

    assert isinstance(node, RerollNode)

    assert node.condition(2) is True
    assert node.condition(4) is False


def test_parse_reroll_greater_equal(parser):

    node = parser.parse("2d6r>=5")

    assert isinstance(node, RerollNode)

    assert node.condition(5) is True
    assert node.condition(4) is False


# --------------------------------------------------
# INVALID
# --------------------------------------------------

def test_parse_invalid_expression(parser):

    with pytest.raises(ValueError):
        parser.parse("invalid")


def test_reroll_invalid_operator(parser):

    # regex não aceita "=" → deve falhar no parse
    with pytest.raises(ValueError):
        parser.parse("1d6r=3")


# --------------------------------------------------
# COMBINED (🔥 importante)
# --------------------------------------------------

def test_parse_combined(parser):

    node = parser.parse("4d6!kh3r<2")

    # ordem: Roll -> Explode -> Keep -> Reroll

    assert isinstance(node, RerollNode)

    inner = node.child
    assert isinstance(inner, KeepHighestNode)

    inner = inner.child
    assert isinstance(inner, ExplodeNode)

    inner = inner.child
    assert isinstance(inner, RollNode)


# --------------------------------------------------
# EDGE CASES
# --------------------------------------------------

def test_parse_minimum(parser):

    node = parser.parse("1d1")

    assert isinstance(node, RollNode)
    assert node.quantity == 1
    assert node.sides == 1


def test_parse_large_values(parser):

    node = parser.parse("100d100")

    assert isinstance(node, RollNode)
    assert node.quantity == 100
    assert node.sides == 100


# --------------------------------------------------
# AST SHAPE (robusto)
# --------------------------------------------------

def test_ast_shape(parser):

    node = parser.parse("2d6!")

    rep = repr(node)

    assert "ExplodeNode" in rep
    assert "RollNode" in rep