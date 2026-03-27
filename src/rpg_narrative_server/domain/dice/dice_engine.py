from rpg_narrative_server.domain.dice.rules.evaluator import evaluate


def roll(ast, rng) -> tuple[list[int], int]:
    """
    Executa rolagem a partir de um AST (não string).
    """

    rolls = evaluate(ast, rng)
    total = sum(rolls)

    return rolls, total
