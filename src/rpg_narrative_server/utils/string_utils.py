# src/rpg_narrative_server/utils/string_utils.py

import re
from typing import Iterable


# ---------------------------------------------------------
# NORMALIZAÇÃO
# ---------------------------------------------------------

def normalize_whitespace(text: str) -> str:
    """
    Remove espaços duplicados e normaliza quebras de linha.
    """
    if not text:
        return ""

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()


def normalize_linebreaks(text: str) -> str:
    """
    Garante padrão consistente de quebras de linha.
    """
    return text.replace("\r\n", "\n").replace("\r", "\n")


# ---------------------------------------------------------
# LIMPEZA
# ---------------------------------------------------------

def strip_lines(text: str) -> str:
    """
    Remove espaços extras por linha.
    """
    return "\n".join(line.strip() for line in text.splitlines())


def remove_empty_lines(text: str) -> str:
    """
    Remove linhas vazias.
    """
    return "\n".join(line for line in text.splitlines() if line.strip())


def clean_text(text: str) -> str:
    """
    Limpeza geral (pipeline simples).
    """
    text = normalize_linebreaks(text)
    text = strip_lines(text)
    text = remove_empty_lines(text)
    text = normalize_whitespace(text)

    return text


# ---------------------------------------------------------
# TRUNCAMENTO
# ---------------------------------------------------------

def truncate(text: str, max_chars: int) -> str:
    """
    Limita o tamanho de uma string.
    """
    if not text:
        return ""

    return text[:max_chars]


def truncate_lines(lines: list[str], max_items: int) -> list[str]:
    """
    Mantém apenas os últimos N itens.
    """
    return lines[-max_items:]


# ---------------------------------------------------------
# DEDUPLICAÇÃO
# ---------------------------------------------------------

def deduplicate(items: Iterable[str]) -> list[str]:
    """
    Remove duplicados mantendo ordem.
    """
    seen = set()
    result = []

    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)

    return result


# ---------------------------------------------------------
# JOIN / FORMATAÇÃO
# ---------------------------------------------------------

def safe_join(items: Iterable[str], sep: str = "\n") -> str:
    """
    Junta strings ignorando vazios.
    """
    return sep.join(item for item in items if item)


def ensure_prefix(text: str, prefix: str) -> str:
    """
    Garante que o texto começa com prefixo.
    """
    if not text.startswith(prefix):
        return prefix + text
    return text


# ---------------------------------------------------------
# MEDIÇÃO
# ---------------------------------------------------------

def count_chars(text: str) -> int:
    return len(text or "")


def total_length(items: Iterable[str]) -> int:
    return sum(len(i) for i in items if i)