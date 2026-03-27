import pytest

from rpg_narrative_server.utils.string_utils import (
    normalize_whitespace,
    normalize_linebreaks,
    strip_lines,
    remove_empty_lines,
    clean_text,
    truncate,
    truncate_lines,
    deduplicate,
    safe_join,
    ensure_prefix,
    count_chars,
    total_length,
)


# ---------------------------------------------------------
# NORMALIZAÇÃO
# ---------------------------------------------------------

def test_normalize_whitespace_basic():
    text = "a   b\t\tc"
    assert normalize_whitespace(text) == "a b c"


def test_normalize_whitespace_newlines():
    text = "a\n\n\nb"
    assert normalize_whitespace(text) == "a\n\nb"


def test_normalize_whitespace_empty():
    assert normalize_whitespace("") == ""


def test_normalize_linebreaks():
    text = "a\r\nb\rc"
    assert normalize_linebreaks(text) == "a\nb\nc"


# ---------------------------------------------------------
# LIMPEZA
# ---------------------------------------------------------

def test_strip_lines():
    text = " a \n b  "
    assert strip_lines(text) == "a\nb"


def test_remove_empty_lines():
    text = "a\n\n\nb\n"
    assert remove_empty_lines(text) == "a\nb"


def test_clean_text_pipeline():
    text = "  a \r\n\r\n b  \n\n"
    result = clean_text(text)
    assert result == "a\n\nb"


# ---------------------------------------------------------
# TRUNCAMENTO
# ---------------------------------------------------------

def test_truncate_basic():
    assert truncate("abcdef", 3) == "abc"


def test_truncate_empty():
    assert truncate("", 10) == ""


def test_truncate_lines():
    lines = ["a", "b", "c", "d"]
    assert truncate_lines(lines, 2) == ["c", "d"]


# ---------------------------------------------------------
# DEDUPLICAÇÃO
# ---------------------------------------------------------

def test_deduplicate_order_preserved():
    items = ["a", "b", "a", "c", "b"]
    assert deduplicate(items) == ["a", "b", "c"]


def test_deduplicate_empty():
    assert deduplicate([]) == []


# ---------------------------------------------------------
# JOIN / FORMATAÇÃO
# ---------------------------------------------------------

def test_safe_join_ignores_empty():
    items = ["a", "", "b", None]
    assert safe_join(items) == "a\nb"


def test_safe_join_custom_sep():
    items = ["a", "b"]
    assert safe_join(items, sep=",") == "a,b"


def test_ensure_prefix_adds():
    assert ensure_prefix("text", ">> ") == ">> text"


def test_clean_text_pipeline():
    text = "  a \r\n\r\n b  \n\n"
    result = clean_text(text)

    assert result == "a\nb"  # ✔ correto


# ---------------------------------------------------------
# MEDIÇÃO
# ---------------------------------------------------------

def test_count_chars():
    assert count_chars("abc") == 3


def test_count_chars_none():
    assert count_chars(None) == 0


def test_total_length():
    items = ["ab", "c", "", None]
    assert total_length(items) == 3