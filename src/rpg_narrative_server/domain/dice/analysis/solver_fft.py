import numpy as np

from rpg_narrative_server.domain.dice.ast.nodes import (
    RollNode,
    ExplodeNode,
    RerollNode,
)


class FFTDiceSolver:
    def __init__(self, max_explode_depth: int = 50):
        self.max_explode_depth = max_explode_depth

    # ========================
    # PUBLIC API (ENTRYPOINT)
    # ========================
    def solve(self, node):
        return self._solve_node(node)

    # ========================
    # CORE DISPATCH
    # ========================
    def _solve_node(self, node):
        if isinstance(node, RollNode):
            base = self._single_die(node.sides)
            return self._power(base, node.quantity)

        if isinstance(node, RerollNode):
            base = self._single_die(node.child.sides)
            base = self._apply_reroll(base, node.condition)
            return self._power(base, node.child.quantity)

        if isinstance(node, ExplodeNode):
            base = self._explode(node.child.sides)
            return self._power(base, node.child.quantity)

        raise NotImplementedError(type(node))

    # ========================
    # LOW LEVEL
    # ========================
    def _single_die(self, sides):
        dist = np.zeros(sides + 1)
        dist[1:] = 1.0 / sides
        return dist

    def _normalize(self, dist):
        s = dist.sum()
        return dist if s == 0 else dist / s

    def _fft_convolve(self, a, b):
        size = len(a) + len(b) - 1
        n = 1 << (size - 1).bit_length()

        fa = np.fft.rfft(a, n)
        fb = np.fft.rfft(b, n)

        result = np.fft.irfft(fa * fb, n)
        return np.maximum(result[:size], 0)

    def _power(self, base, n):
        result = np.array([1.0])
        power = base.copy()

        while n > 0:
            if n & 1:
                result = self._fft_convolve(result, power)
            power = self._fft_convolve(power, power)
            n >>= 1

        return self._normalize(result)

    def _apply_reroll(self, base, condition):
        mask = np.array([condition(i) for i in range(len(base))])
        reroll_prob = base[mask].sum()

        new_dist = base.copy()
        new_dist[mask] = 0
        new_dist += reroll_prob * base

        return self._normalize(new_dist)

    def _explode(self, sides):
        base = self._single_die(sides)
        p_explode = base[sides]

        result = np.zeros(1)
        current = base.copy()

        for _ in range(self.max_explode_depth):
            if len(result) < len(current):
                result = np.pad(result, (0, len(current) - len(result)))

            result[:len(current)] += current

            current = self._fft_convolve(current, base) * p_explode

            if current.sum() < 1e-10:
                break

        return self._normalize(result)