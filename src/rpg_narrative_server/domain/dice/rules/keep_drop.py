def keep_highest(values, k):
    return sorted(values, reverse=True)[:k]


def drop_lowest(values, k):
    return sorted(values)[k:]