import pytest

from rpg_narrative_server.shared.dice.dice_regex import DiceRegex


@pytest.fixture
def match():
    return DiceRegex.match


# --------------------------------------------------
# BASIC MATCH
# --------------------------------------------------


def test_match_basic(match):

    m = match("2d6")

    assert m is not None
    assert m.group("num") == "2"
    assert m.group("sides") == "6"


# --------------------------------------------------
# EXPLODE
# --------------------------------------------------


def test_match_explode(match):

    m = match("2d6!")

    assert m is not None
    assert m.group("explode") == "!"


# --------------------------------------------------
# KEEP HIGHEST
# --------------------------------------------------


def test_match_keep(match):

    m = match("4d6kh3")

    assert m is not None
    assert m.group("keep") == "kh3"


# --------------------------------------------------
# DROP LOWEST
# --------------------------------------------------


def test_match_drop(match):

    m = match("4d6dl1")

    assert m is not None
    assert m.group("drop") == "dl1"


# --------------------------------------------------
# REROLL
# --------------------------------------------------


def test_match_reroll(match):

    m = match("2d6r<3")

    assert m is not None
    assert m.group("reroll") == "r<3"


def test_match_reroll_greater_equal(match):

    m = match("2d6r>=5")

    assert m is not None
    assert m.group("reroll") == "r>=5"


# --------------------------------------------------
# COMBINED
# --------------------------------------------------


def test_match_combined(match):

    m = match("4d6!kh3r<2")

    assert m is not None

    assert m.group("explode") == "!"
    assert m.group("keep") == "kh3"
    assert m.group("reroll") == "r<2"


# --------------------------------------------------
# INVALID EXPRESSIONS
# --------------------------------------------------


@pytest.mark.parametrize(
    "expr",
    [
        "",
        "d6",
        "2d",
        "2d6kk3",
        "2d6!!",
        "abc",
        "2d6kh",
        "2d6dl",
        "2d6r",
    ],
)
def test_invalid_expressions(match, expr):

    assert match(expr) is None


# --------------------------------------------------
# EDGE CASES
# --------------------------------------------------


def test_min_values(match):

    m = match("1d1")

    assert m is not None
    assert m.group("num") == "1"
    assert m.group("sides") == "1"


def test_large_values(match):

    m = match("100d100")

    assert m is not None
    assert m.group("num") == "100"
    assert m.group("sides") == "100"
