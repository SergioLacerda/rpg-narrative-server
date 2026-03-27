def reroll(values, condition, sides, rng):
    result = []

    for v in values:
        while condition(v):
            v = rng.roll(sides)
        result.append(v)

    return result