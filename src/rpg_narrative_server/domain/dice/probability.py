from rpg_narrative_server.domain.dice.analysis.solver_fft import FFTDiceSolver


def analyze_distribution(ast):
    solver = FFTDiceSolver()
    return solver.solve(ast)