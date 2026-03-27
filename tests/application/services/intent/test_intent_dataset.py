import pytest

from rpg_narrative_server.application.services.intent.intent_classifier import (
    IntentClassifier,
)
from rpg_narrative_server.application.services.intent.language_profiles import (
    SUPPORTED_LANGUAGES,
)


# ---------------------------------------------------------
# MATCH INTELIGENTE
# ---------------------------------------------------------


def match_intent(result: str, expected: str) -> bool:

    if expected == "ACTION":
        return result in ("ACTION", "EXPLORATION")

    if expected == "EXPLORATION":
        return result in ("EXPLORATION", "ACTION")

    if expected == "CHAT":
        return result in ("CHAT", "OOC")

    return result == expected


# ---------------------------------------------------------
# EXPANDER
# ---------------------------------------------------------


class IntentDatasetExpander:

    def expand(self, text: str, n: int = 3):

        variants = set()

        for _ in range(n):

            variants.add(text)
            variants.add(f"{text} agora")
            variants.add(f"{text} rapidamente")

        return list(variants)


# ---------------------------------------------------------
# DATASET BASE
# ---------------------------------------------------------

DATASET_INTENT = [
    ("eu ataco o goblin", "ACTION"),
    ("saco minha espada", "ACTION"),
    ("olho ao redor", "EXPLORATION"),
    ("kkk isso foi engraçado", "CHAT"),
    ("isso está bugado", "OOC"),
]


# ---------------------------------------------------------
# TESTE PRINCIPAL
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_intent_dataset_with_expansion():

    clf = IntentClassifier(SUPPORTED_LANGUAGES)
    expander = IntentDatasetExpander()

    errors = []
    expanded_tests = []

    # ---------------------------------------------------------
    # PASSO 1: rodar dataset base
    # ---------------------------------------------------------

    for text, expected in DATASET_INTENT:

        result = await clf.classify(text)

        variations = expander.expand(text, n=3)

        for v in variations:
            expanded_tests.append((v, expected))

        if not match_intent(result, expected):
            errors.append((text, expected, result))

            variations = expander.expand(text, n=5)

            for v in variations:
                expanded_tests.append((v, expected))

    # ---------------------------------------------------------
    # PASSO 2: rodar variações
    # ---------------------------------------------------------

    expansion_errors = []

    for text, expected in expanded_tests:

        result = await clf.classify(text)

        if not match_intent(result, expected):
            expansion_errors.append((text, expected, result))

    # ---------------------------------------------------------
    # METRICS
    # ---------------------------------------------------------

    base_accuracy = 1 - (len(errors) / len(DATASET_INTENT))

    if expanded_tests:
        expansion_accuracy = 1 - (len(expansion_errors) / len(expanded_tests))
    else:
        expansion_accuracy = 1.0

    print(f"\nBase accuracy: {base_accuracy:.2f}")
    print(f"Expansion accuracy: {expansion_accuracy:.2f}")

    # ---------------------------------------------------------
    # DEBUG
    # ---------------------------------------------------------

    if errors:
        print("\n--- BASE ERRORS ---")
        for t, e, r in errors:
            print(f"[{e}] {t} → {r}")

    if expansion_errors:
        print("\n--- EXPANSION ERRORS ---")
        for t, e, r in expansion_errors:
            print(f"[{e}] {t} → {r}")

    # ---------------------------------------------------------
    # ASSERTS
    # ---------------------------------------------------------

    assert base_accuracy >= 0.75
    assert expansion_accuracy >= 0.30
