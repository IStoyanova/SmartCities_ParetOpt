from platypus import NSGAII, Problem, Real
from Scenarios.Infrastructure import *

print('Optimization of the multi-domain operation')
print()

T=96

def paropt(vars):
    x = vars[0]
    y = vars[1]
    return [4*x + 6*y, 10*x + 2*y], [100*x + 500*y - 2600, 32*x + 16*y - 256]

problem = Problem(2, 2, 2)
"""problem with two decision variables, two objectives, and two constraints, respectively"""
problem.types[:] = [Real(0, 30), Real(0, 30)]
problem.constraints[:] = "<=0"
problem.function = paropt
"""problem.directions[:] = Problem.MAXIMIZE"""

algorithm = NSGAII(problem)
algorithm.run(10000)


feasible_solutions = [s for s in algorithm.result if s.feasible]
for s in algorithm.result:
    if s.feasible==True:
        print(s)

import matplotlib.pyplot as plt

plt.scatter([s.objectives[0] for s in algorithm.result],
            [s.objectives[1] for s in algorithm.result])
plt.xlim([0, 100])
plt.ylim([0, 100])
plt.xlabel("$f_1(x)$")
plt.ylabel("$f_2(x)$")
plt.show()