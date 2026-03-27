def explode(values, sides, rng):
    result = []

    for v in values:
        result.append(v)

        while v == sides:
            v = rng.roll(sides)
            result.append(v)

    return result